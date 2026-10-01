# R16 — Réutilisation d’un terminal live en lecture seule

État au 1er octobre 2026 : **composant FLUJO inspecté, non installé et non exécuté. R16 n’est pas livré.**

L’objectif est un vrai terminal cloud dont la sortie apparaît en direct, en lecture seule, dans la conversation. Une page de navigateur, une capture et un enregistrement ne valident pas ce résultat.

## Conclusion

Un sous-composant existant est réutilisable : le terminal MCP App de **FLUJO**. Il fournit un vrai PTY et un rendu xterm, mais accepte actuellement les entrées utilisateur. Une adaptation limitée, une connexion MCP privée et un essai dans la conversation cible restent nécessaires.

Décision : poursuivre la préparation d’un **observateur de terminal**, sans installer la plateforme FLUJO entière. Ne pas annoncer une livraison avant les essais d’acceptation ci-dessous.

## Sources et versions vérifiées

| Élément | Référence examinée | Résultat |
| --- | --- | --- |
| FLUJO | Version **3.46.1**, commit de release **bd41f469cb1040d259a6b6dbe95a18f9bc702166**, 28 septembre 2026 | Candidat concret : `mcp-servers/bash` |
| FLUJO, activité récente | Commit **3fccc557df97aba0e96ce28a8e6eebaa8e71d7d9**, 30 septembre 2026 | Les fichiers `index.ts`, `resources.ts`, `tools.ts` et `package.json` du terminal sont identiques à ceux du commit de release |
| MCP Apps officiel | Version du dépôt **2.0.3**, commit **82221c0c8ce7661efa6771c9d461511b1650495f**, 25 septembre 2026 | Exemple `system-monitor-server` : vue inline et polling réel, mais aucune fonction de terminal PTY |
| ttyd, référence partielle | Version **1.7.7**, commit **40e79c706be14029b391f369bee6613c31667abb** | Terminal web avec blocage serveur des entrées lorsque le mode writable est désactivé; aucune intégration inline démontrée |

Sources : [release FLUJO](https://github.com/mario-andreschak/FLUJO/releases/tag/v3.46.1), [composant FLUJO figé](https://github.com/mario-andreschak/FLUJO/tree/bd41f469cb1040d259a6b6dbe95a18f9bc702166/mcp-servers/bash), [exemple MCP officiel](https://github.com/modelcontextprotocol/ext-apps/tree/82221c0c8ce7661efa6771c9d461511b1650495f/examples/system-monitor-server), [blocage d’entrée ttyd](https://github.com/tsl0922/ttyd/blob/40e79c706be14029b391f369bee6613c31667abb/src/protocol.c#L308-L310)

### Licence et installation

FLUJO porte une [licence MIT](https://github.com/mario-andreschak/FLUJO/blob/bd41f469cb1040d259a6b6dbe95a18f9bc702166/LICENSE). L’arbre examiné ne contient aucune licence distincte dans les sous-dossiers Bash et shared. Une réutilisation doit conserver le copyright et la notice MIT.

Le [manifest du composant](https://github.com/mario-andreschak/FLUJO/blob/bd41f469cb1040d259a6b6dbe95a18f9bc702166/mcp-servers/bash/package.json) exige Node.js ≥20. Le [lockfile examiné](https://github.com/mario-andreschak/FLUJO/blob/3fccc557df97aba0e96ce28a8e6eebaa8e71d7d9/package-lock.json) fixe les dépendances principales suivantes :

- `@lydell/node-pty` 1.1.0, MIT, avec paquets binaires natifs optionnels par plateforme
- `@modelcontextprotocol/sdk` 1.30.0, MIT
- `@xterm/xterm` 6.0.0 et `@xterm/addon-fit` 0.11.0, MIT
- TypeScript 6.0.3, Apache-2.0, pour la compilation

Le lockfile référence le registre npm officiel et contient les intégrités SHA-512 de ces archives. Cela ne constitue ni un audit complet des dépendances transitives ni une validation des binaires. La compilation du sous-composant utilise aussi le workspace shared et [son script d’assemblage](https://github.com/mario-andreschak/FLUJO/blob/3fccc557df97aba0e96ce28a8e6eebaa8e71d7d9/mcp-servers/embed-shared.mjs). Installer tout le dépôt ajouterait des composants inutiles, dont la préparation du navigateur.

## Ce que le code fait réellement

La [ressource de vue](https://github.com/mario-andreschak/FLUJO/blob/bd41f469cb1040d259a6b6dbe95a18f9bc702166/mcp-servers/bash/src/resources.ts) est un document HTML MCP App autonome avec xterm. Elle lit les nouveaux caractères à partir d’un curseur. Le serveur reçoit ces caractères d’un PTY natif : il s’agit donc d’une sortie live par polling, pas d’une vidéo ni d’un replay préenregistré.

Le code actuel attend 60 ms entre deux lectures pendant l’exécution. Cette cadence doit être adaptée aux limites et à la latence du host; sa performance n’a pas été mesurée dans ChatGPT.

Deux distinctions sont essentielles :

- Les commandes ordinaires `run` et `start` de FLUJO utilisent des **pipes séparés**. Elles n’apparaissent pas automatiquement dans le PTY affiché
- `terminal.write(chunk)` dans xterm **affiche une sortie**. `session.pty.write(data)` côté serveur **injecte une entrée** dans le processus

Le contrôleur agent doit donc lancer les tâches observées dans le PTY effectivement associé à la vue. Ce raccordement n’existe pas automatiquement pour les sessions shell d’un autre outil.

Source : [implémentation serveur](https://github.com/mario-andreschak/FLUJO/blob/bd41f469cb1040d259a6b6dbe95a18f9bc702166/mcp-servers/bash/src/tools.ts)

## Adaptation minimale en lecture seule

### Serveur : séparer observation et commande

Conserver la capacité de l’agent à lancer les tâches autorisées. En revanche, la façade MCP accessible au spectateur doit seulement rendre une session existante et lire sa sortie bornée.

- Refuser côté serveur les écritures, lancements, fermetures et redimensionnements sur cette façade
- Conserver le contrôleur sur une interface privée distincte, non accessible à la vue
- Vérifier le propriétaire et la session à chaque lecture; ne pas reprendre le repli `legacy:anonymous` comme contrôle d’accès distant
- Ne pas hériter aveuglément de tout l’environnement du serveur dans les processus enfants
- Ne pas présenter le confinement du répertoire de travail comme un sandbox du shell

`visibility: ["model"]` peut exclure `terminal_write` de la surface widget tout en le laissant disponible à l’agent. Le host doit alors rejeter un appel provenant de l’app. Cependant, cette règle du host ne remplace pas le contrôle d’accès serveur de la façade observateur. Les outils sans visibilité explicite sont accessibles par défaut au modèle **et** à l’app.

Il faut couvrir aussi `run`, `start`, `write_stdin`, `kill`, `release_owner` et `open_terminal`, plutôt que bloquer seulement une méthode.

Source : [spécification normative de visibilité](https://github.com/modelcontextprotocol/ext-apps/blob/82221c0c8ce7661efa6771c9d461511b1650495f/specification/2026-01-26/apps.mdx#L397-L403)

### Widget : supprimer les voies de retour

- Garder le rendu xterm, la sélection, le défilement et la lecture différentielle
- Retirer `terminal.onData`, la file d’entrée, le collage transmis et toute réponse automatique renvoyée au PTY
- Ajouter `disableStdin` comme protection ergonomique complémentaire
- Retirer New, Close, le choix du shell et du répertoire, ainsi que tout lancement automatique
- Retirer la demande automatique de mode PiP afin de rester inline
- Adapter l’affichage local sans redimensionner le PTY observé
- À la fermeture de la vue, arrêter son polling sans arrêter le processus

Le simple masquage du clavier ne prouve pas la lecture seule. Voir l’[API xterm](https://xtermjs.org/docs/api/terminal/classes/terminal/) et son [option disableStdin](https://xtermjs.org/docs/api/terminal/interfaces/iterminaloptions/).

### Arrêt, redimensionnement et replay

| Opération actuelle | Effet | Traitement attendu |
| --- | --- | --- |
| `terminal_close` | Appelle `pty.kill()` | Interdit au spectateur |
| `terminal_resize` | Modifie le PTY | Taille du PTY fixée par le contrôleur |
| `terminal_read` | Relit une portion du buffer | Autorisé avec session vérifiée et limites |
| Reconnexion sans session | Peut ouvrir automatiquement un shell | Supprimer ce comportement |
| Replay | Doit seulement réafficher des données | Aucune réexécution, aucune entrée transmise |

Source : [handlers serveur](https://github.com/mario-andreschak/FLUJO/blob/bd41f469cb1040d259a6b6dbe95a18f9bc702166/mcp-servers/bash/src/tools.ts#L2779-L2838)

## Voie privée vers une vraie vue inline

OpenAI documente le [rendu MCP Apps dans la conversation](https://developers.openai.com/plugins/build/chatgpt-ui) : un outil référence une ressource HTML et le host la rend dans une iframe contrôlée. Cela confirme le support produit général, pas le fonctionnement de ce composant dans la conversation cible.

La voie documentée sans serveur exposé publiquement est [Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels). Le client du tunnel peut joindre un serveur MCP stdio ou HTTP et communiquer avec OpenAI par connexion sortante. Cette voie couvre les connexions privées et les tests développeur ; elle ne constitue pas une distribution publique de plugin.

Prérequis encore non vérifiés pour cette intégration :

1. Un hôte cloud durable capable d’exécuter le PTY et le serveur
2. L’installation approuvée de `tunnel-client` et des dépendances nécessaires
3. La configuration sécurisée d’un tunnel et de son authentification runtime
4. Les droits Tunnels Read + Use, ainsi que Manage pour créer ou modifier le tunnel
5. La disponibilité du mode développeur et l’association au bon compte/workspace
6. La connexion du plugin et un essai inline dans la conversation cible

Les [instructions officielles de connexion et de test](https://developers.openai.com/plugins/deploy/connect-chatgpt) décrivent ces étapes. Aucun tunnel ni plugin n’a été configuré dans cette investigation. Aucun outil actuellement vérifié ne permet d’injecter directement ce terminal dans le message courant.

## Plan d’acceptation

Les tests suivants doivent réussir avant de marquer R16 livré :

1. **Vraie source live** : une tâche exécutée dans un PTY cloud produit un marqueur imprévisible et des lignes horodatées; la vue les affiche avant la fin du processus
2. **Vrai inline** : la sortie est visible dans la conversation, sans ouvrir de page externe et sans dépendre du PiP
3. **Lecture seule serveur** : les appels forgés d’écriture, de lancement, d’arrêt et de resize depuis la surface observateur sont rejetés
4. **Lecture seule UI** : clavier, collage, Ctrl-C, événements souris et réponses automatiques du terminal n’injectent aucune entrée
5. **Contrôle agent conservé** : l’agent peut lancer une seconde tâche autorisée dans le PTY associé et la voir apparaître
6. **Cycle de vie sûr** : reconnexion, fermeture de la vue et replay n’ajoutent aucun processus et ne relancent aucune commande
7. **Isolation** : l’accès non authentifié et l’accès à une autre session ou à un autre propriétaire échouent
8. **État honnête** : fin de tâche, déconnexion, retard et sortie tronquée sont signalés; aucune animation ne simule une activité absente

Les tests existants de FLUJO valident notamment la présence des fonctions interactives. Ils ne démontrent pas ces garanties de lecture seule.

## Prototype navigateur distinct

Un essai séparé basé sur **ttyd 1.7.7** et **tmux 3.5a** a été préparé à partir de paquets officiels Debian : signatures et hachages contrôlés, extraction locale et chargement des exécutables vérifiés. Le lancement de tmux a échoué avec `Operation not permitted` à la création de son socket local, y compris lors de l’unique reprise par le mécanisme d’approbation prévu.

Aucun serveur, processus résiduel, listener ou accès public n’a été créé. Les tests d’affichage navigateur, de refus des entrées, de redimensionnement et de reconnexion sont **NON EXÉCUTÉS**. Cet essai ne fournit donc aucune URL active ni preuve de lecture seule en fonctionnement.

Même si ses essais réussissent, il validera une observation live dans un navigateur. Il ne validera pas le rendu inline MCP Apps demandé pour R16.

**Bilan : recherche et plan vérifiés; adaptation, installation, exécution, connexion privée et validation inline restent à effectuer dans leur périmètre autorisé.**

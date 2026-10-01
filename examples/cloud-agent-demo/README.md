# Démonstration cloud : composants existants et tests réels

État vérifié le 1er octobre 2026. Ce dossier contient les tests originaux et les versions utilisées, pas un nouvel orchestrateur. Aucun identifiant, profil authentifié, journal privé ou dépendance vendue avec le projet n’est inclus.

## Résultats et limites

| Composant | Version vérifiée | Résultat réel |
| --- | --- | --- |
| Codex CLI | 0.159.0-alpha.7, déjà présent dans l’environnement de test | Version et aide vérifiées ; aucun appel modèle. La fixture publiée comporte volontairement un défaut |
| OpenHands SDK + Tools | 1.50.1 | Installation et 185 versions du lock vérifiées ; conversation, configuration enfant et schéma `task` contrôlés hors modèle |
| Sequential Thinking officiel | 2026.8.31 | Cinq groupes de contrôles MCP stdio réussis, dont schémas, appel synthétique et rejet d’une entrée invalide |
| DecisionMatrix MCP | 1.0.2 | 25 contrôles réussis, **un défaut réel reproduit**, verdict global non validé |

Une revue indépendante a reproduit les contrôles. Aucun compte n’a été connecté, aucune inférence n’a été exécutée et aucun véritable sous-agent OpenHands n’a été lancé. La configuration d’une conversation enfant n’est pas une délégation exécutée.

Le SDK OpenHands consomme des outils MCP : il n’est pas, à lui seul, un serveur MCP OpenHands. Le candidat tiers [healdigital/openhands-mcp](https://github.com/healdigital/openhands-mcp/tree/5e84d0c4ea4f8d56af7ae18f12b74aea0de02f44), package 0.2.2, a été inspecté mais **pas installé ni exécuté**. Il exige un backend OpenHands compatible, absent de cette démonstration.

## Reproduire les contrôles

Environnement testé : Linux, Python 3.12.14 et Node.js 24.19.0. Les dépendances sont installées localement. Une autre plateforme ou version n’est pas réputée validée par ces reçus.

### MCP de raisonnement et de décision

Dans `reasoning-tools` :

```sh
npm ci --ignore-scripts
mkdir -p evidence
python3 verify_mcp.py
python3 verify_decisionmatrix.py
```

Le premier test doit réussir. Le second conserve le défaut vendor : il retourne actuellement un **code de sortie 1**. Ne pas masquer cet échec pour afficher une validation globale verte. Les scripts écrivent des reçus et journaux synthétiques dans `evidence` ; ils ne nécessitent ni clé ni modèle.

Sequential Thinking reçoit seulement le texte neutre « Synthetic protocol verification ». C’est un registre structuré en mémoire, pas un moteur qui vérifie les faits ni une garantie de bonne décision.

DecisionMatrix est comparé à un oracle Python en fractions exactes pour une matrice pondérée. Ses tests couvrent aussi des erreurs d’entrée et des cas limites. Ces vérifications ne garantissent ni la qualité des scores fournis ni la pertinence des préférences humaines.

### Défaut DecisionMatrix conservé

Avec un critère de coût, A=4 et B=2, TOPSIS classe correctement B devant A. Mais `compare_two` indique que le critère favorise A et lui attribue la victoire sur ce critère. L’explication contredit le classement.

Le paquet est resté intact. Dans le profil Codex de démonstration, `compare_two` est exclu par la liste d’outils autorisés et interdits. Cela vérifie une configuration de client, pas un contrôle d’accès ajouté au serveur. Les autres fonctions restent limitées aux cas testés. Le paquet annonce aussi une version de serveur différente de sa version npm : ne pas confondre ces métadonnées.

### OpenHands hors modèle

Dans `openhands`, avec `uv` installé depuis sa source officielle :

```sh
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.lock.txt
uv pip check --python .venv/bin/python
test_home="$(mktemp -d)"
env -i PATH="$PATH" HOME="$test_home" .venv/bin/python -I -B checks/offline_check.py
```

Le test définit le mode local de la carte de coûts LiteLLM avant tout import. Il contrôle les événements Python DNS/réseau et interdit les sous-processus. Ce garde-fou de test Python n’est **pas** un sandbox système d’exploitation.

Le reçu exige des assertions réelles sur l’enfant, le schéma et le rejet d’un appel sans prompt. Aucun `Conversation.run()` n’est appelé. Le premier test dépendait d’un réglage ambiant LiteLLM ; cette faiblesse a été corrigée et la version publiée a été reproduite avec un HOME et un environnement vides.

### Fixture Codex

```sh
python3 -m unittest discover -s codex-client/demo -v
```

Résultat initial attendu : trois tests, **un échec volontaire** parce que `count_nonnegative` exclut zéro. Ce code est une entrée de démonstration, pas une correction livrée par Codex. Une vraie exécution du modèle, sa modification et le retour au vert restent à effectuer après connexion officielle autorisée. Le lanceur interne et les profils de l’environnement de test ne sont pas distribués.

## Sources, licences et branchement

- [Codex CLI](https://learn.chatgpt.com/docs/codex/cli), [authentification](https://learn.chatgpt.com/docs/auth), [configuration MCP](https://learn.chatgpt.com/docs/extend/mcp)
- [OpenHands SDK](https://docs.openhands.dev/sdk/getting-started), [TaskToolSet](https://docs.openhands.dev/sdk/guides/task-tool-set), [MCP](https://docs.openhands.dev/sdk/guides/mcp) ; SDK et Tools sous MIT
- [Sequential Thinking officiel](https://github.com/modelcontextprotocol/servers/tree/579c3903f30044eb702a599a74b3ae77588e722e/src/sequentialthinking) ; respecter la [licence du dépôt à cette version](https://github.com/modelcontextprotocol/servers/blob/579c3903f30044eb702a599a74b3ae77588e722e/LICENSE), qui ne se résume pas à MIT pour l’ensemble du contenu
- [DecisionMatrix](https://github.com/inity13/decisionmatrix-mcp/tree/5d317cadbf679d773a97d258ea884a764f8d1a8c), sous MIT ; dépendance `decimal.js`

Les paquets MCP installés ont été comparés à leurs archives et aux intégrités du lock. L’audit npm n’a signalé aucune vulnérabilité connue au moment du contrôle ; cela n’est pas un audit de sécurité complet. Les licences des dépendances restent applicables. Ce dossier n’attribue aucune nouvelle licence au nom du propriétaire.

Les serveurs sont configurés uniquement dans le profil Codex dédié de la démonstration, avec journalisation de pensées désactivée. Cela ne les ajoute pas automatiquement aux outils natifs de toute conversation ChatGPT. Avant de retirer les paquets, retirer ou désactiver leurs deux entrées dans ce profil. Aucun profil global de l’hôte n’a été modifié.

`SHA256SUMS` permet de contrôler les fichiers publiés. Les trois reçus JSON décrivent uniquement les contrôles bornés ci-dessus.

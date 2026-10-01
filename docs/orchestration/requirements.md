# Exigences du blueprint d’orchestration

## 1. Résultat visé

Passer d’une demande en langage naturel à un livrable vérifié : interpréter l’intention, retrouver les connaissances utiles, planifier, répartir le travail, contrôler l’exécution et livrer. Mesurer le temps humain requis, la qualité, les coûts et les reprises. Aucun revenu, niveau d’autonomie, gain de temps ou taux de réussite n’est garanti par cette spécification.

Ce document décrit une architecture cible. Aucun système complet ni démonstrateur vocal livré n’est revendiqué. Le registre associé est un document de planification, pas un moteur de workflow.

## 2. Invariants

- Connaissances avant modification : lire sources officielles et exemples adaptés aux versions réellement utilisées
- Réutilisation avant construction : vérifier les outils, dépôts et travaux existants, puis limiter les adaptations
- Isolation sans cloisonnement des échanges : dossiers et runtimes séparés, canaux de communication explicites entre IA
- Coordination des écritures : un propriétaire par ressource modifiée, réparations ciblées possibles après accord de périmètre
- Preuves proportionnées : distinguer documentation, installation, test isolé, intégration et acceptation finale
- Supervision réelle : vérifier les étapes significatives et les erreurs, pas seulement attendre une notification de fin
- Confidentialité : secrets et données privées hors du registre public ; ne publier que des preuves expurgées et autorisées
- Accès effectif : vérifier le contexte courant et respecter les contrôles ; une capacité produit ne garantit pas sa disponibilité dans une session
- Simplicité : utiliser une interface ou connexion existante quand elle satisfait le besoin, avant d’ajouter une dépendance
- Continuité : reprise à partir d’états durables et d’événements observables ; aucun service permanent supposé
- Maintenance : sauvegardes, tests de non-régression, retour arrière et versions explicites

## 3. Architecture proposée

La coordination principale transforme les demandes en résultats attendus et arbitre les dépendances. Deux fonctions distinctes organisent la livraison et la qualité. Des spécialistes exécutent recherche, développement, connaissances, interface, vision ou voix dans des espaces dédiés.

Cette hiérarchie est une proposition d’organisation, pas une obligation de multiplier les agents. Le nombre d’exécutants dépend du travail, des capacités et des coûts constatés.

Un nœud décrit son rôle, ses entrées, ses sorties, ses effets de bord, ses permissions nécessaires et son critère d’acceptation. Les messages transportent l’identifiant de la tâche, l’état, les références utiles et les erreurs exploitables. Une communication n’autorise pas automatiquement une modification des fichiers du destinataire.

Les transports possibles doivent être évalués sur la cible : appels d’outils, MCP, ACP, API ou mécanismes natifs des produits. Ces interfaces ne sont pas interchangeables. Aucun choix de transport ou de plateforme n’est imposé avant vérification.

## 4. États et preuves

Les tâches commencent à l’état `a_evaluer` et évoluent uniquement selon des preuves délimitées. R01 reflète désormais la publication documentaire confirmée ; les acceptations runtime restent ouvertes. Ces statuts ne décrivent pas l’inventaire d’une installation privée. Chaque tâche possède un rôle responsable proposé, des dépendances, une prochaine action et un critère d’acceptation. Les champs `executor`, `evidence` et `last_verified_at` restent nuls tant qu’aucune preuve publique pertinente ne les établit.

États possibles : `a_evaluer`, `documente`, `pret`, `en_cours`, `verifie_partiellement`, `bloque`, `accepte`, `remplace`, `annule`.

Une preuve décrit le périmètre, la version, la cible non sensible, la méthode, le résultat et les limites. Un test positif ne s’étend pas automatiquement aux autres nœuds. Une tâche sans contrôle applicable ne doit pas être marquée réussie. Les sous-tâches héritent par référence du rôle et des critères parent, jamais de leur statut de réussite.

## 5. Registre des volets

Le fichier [tasks.json](tasks.json) est la version structurée des volets ci-dessous. Il ne contient ni commandes d’exécution, ni identifiants d’installation, ni état privé importé.

### R01 — Versionner la spécification

Priorité : P0. Rôle proposé : coordination livraison. Dépendances : aucune. État : vérifié partiellement.

- R01.1 : Inventorier les documents et travaux équivalents
- R01.2 : Définir une branche documentaire et une revue
- R01.3 : Publier seulement les données autorisées
- R01.4 : Relire le contenu publié et vérifier les liens

Preuve : [publication documentaire au commit `75a8dca`](https://github.com/fvegiard/unified-agent-gateway/commit/75a8dcab125286e8dcf9e0db35cee4bd385ab2c3), sur la branche `docs/orchestration-blueprint-20261001` ; quatre fichiers relus octet par octet. R01.1 à R01.3 sont acceptées dans leur périmètre documentaire. R01.4 reste partielle : la relecture du contenu est confirmée, les liens rendus restent à vérifier.

Acceptation : Document versionné, relu, accessible et sans duplication inutile.

### R02 — Maintenir les exigences

Priorité : P0. Rôle proposé : analyse des exigences. Dépendances : R01. État : à évaluer.

- R02.1 : Associer chaque besoin à un résultat observable
- R02.2 : Distinguer exigences, exemples et hypothèses
- R02.3 : Réconcilier les corrections les plus récentes
- R02.4 : Faire contrôler la couverture indépendamment

Acceptation : Chaque demande retenue possède une tâche, un état et un critère explicite.

### R03 — Auditer les adaptations

Priorité : P0. Rôle proposé : qualité. Dépendances : R02. État : à évaluer.

- R03.1 : Inventorier les scripts et adaptations proposés
- R03.2 : Comparer aux fonctions déjà disponibles
- R03.3 : Vérifier paramètres, modèle choisi et périmètre hérité
- R03.4 : Détecter les instructions contradictoires avant admission
- R03.5 : Proposer conservation ou remplacement avec retour arrière

Acceptation : Aucune adaptation redondante ou contradiction connue laissée sans décision documentée.

### R04 — Vérifier les accès effectifs

Priorité : P0. Rôle proposé : environnement. Dépendances : R03. État : à évaluer.

- R04.1 : Identifier la cible et le contexte courant
- R04.2 : Vérifier les capacités par opérations permises
- R04.3 : Comparer configuration déclarée et restrictions effectives
- R04.4 : Identifier le parcours officiel de résolution si nécessaire

Acceptation : Action ciblée permise et vérifiée, ou dépendance précise documentée sans contournement.

### R05 — Superviser les actions visuellement

Priorité : P0. Rôle proposé : vision et qualité. Dépendances : R04. État : à évaluer.

- R05.1 : Observer l’état actuel avant une action graphique
- R05.2 : Contrôler la cible et le résultat après action
- R05.3 : Corréler captures autorisées et journaux
- R05.4 : Distinguer capture ponctuelle et observation continue

Acceptation : Preuves avant/action/après pour le scénario testé, avec limites explicites.

### R06 — Vérifier les connaissances

Priorité : P1. Rôle proposé : connaissances. Dépendances : R01, R03. État : à évaluer.

- R06.1 : Inventorier les stockages et index utiles
- R06.2 : Vérifier couverture, versions et fraîcheur
- R06.3 : Tester une recherche connue et une recherche sans réponse
- R06.4 : Relier les résultats aux sources
- R06.5 : Définir exclusions et mise à jour

Acceptation : Réponses reproductibles avec provenance, fraîcheur et couverture documentées.

### R07 — Comparer les outils de décision

Priorité : P1. Rôle proposé : recherche et qualité. Dépendances : R06. État : à évaluer.

- R07.1 : Comparer outils de raisonnement et fonctionnalités existantes
- R07.2 : Vérifier licences, versions, réseau et persistance
- R07.3 : Tester les validations dans un environnement isolé
- R07.4 : Utiliser Python pour les décisions quantitatives pertinentes
- R07.5 : Publier hypothèses et analyse de sensibilité

Acceptation : Choix fondé sur un besoin mesurable ; aucun journal textuel assimilé à une garantie de vérité.

### R08 — Choisir une plateforme existante

Priorité : P1. Rôle proposé : architecture. Dépendances : R03, R07. État : à évaluer.

- R08.1 : Inventorier les plateformes et interfaces disponibles
- R08.2 : Lire exemples officiels et versions supportées
- R08.3 : Tester un scénario commun de délégation et revue
- R08.4 : Comparer complexité, coût, fiabilité et réversibilité

Acceptation : Solution minimale retenue après essai documenté, sans nouveau moteur par défaut.

### R09 — Connecter les nœuds isolés

Priorité : P1. Rôle proposé : coordination livraison. Dépendances : R08. État : à évaluer.

- R09.1 : Définir rôles, entrées et sorties
- R09.2 : Isoler dossiers, runtimes et responsabilités d’écriture
- R09.3 : Établir communication et escalades entre IA
- R09.4 : Coordonner les réparations ciblées entre environnements
- R09.5 : Tester conflits et pertes de connexion

Acceptation : Échange réel entre nœuds, résultat traçable et absence de collision d’écriture.

### R10 — Relier événements et qualité

Priorité : P1. Rôle proposé : qualité. Dépendances : R09. État : à évaluer.

- R10.1 : Réutiliser les vérificateurs existants
- R10.2 : Relier lancement, erreur, correction et revue aux états
- R10.3 : Tester échec réel et absence de contrôle
- R10.4 : Définir reprise bornée et prévention des boucles
- R10.5 : Faire relire les affirmations de réussite

Acceptation : Échec visible puis correction vérifiée, aucune réussite inventée et reprise traçable.

### R11 — Évaluer les modèles et runtimes

Priorité : P1. Rôle proposé : environnement. Dépendances : R04. État : à évaluer.

- R11.1 : Vérifier versions et capacités réellement exposées
- R11.2 : Identifier modèles locaux et cloud adaptés
- R11.3 : Mesurer qualité, latence et consommation
- R11.4 : Évaluer entraînement ou ajustement comme décision séparée

Acceptation : Capacités testées sur leur cible ; limites et coûts observés clairement associés.

### R12 — Évaluer la vision accélérée

Priorité : P1. Rôle proposé : vision et matériel. Dépendances : R05, R11. État : à évaluer.

- R12.1 : Séparer capture, inférence et contrôle
- R12.2 : Vérifier CPU, GPU, NPU et backends compatibles
- R12.3 : Mesurer précision, latence et charge
- R12.4 : Conserver un chemin de repli fonctionnel

Acceptation : Accélération revendiquée uniquement après mesure sur matériel compatible.

### R13 — Réconcilier le contexte historique

Priorité : P1. Rôle proposé : connaissances. Dépendances : R06. État : à évaluer.

- R13.1 : Retrouver les sources autorisées pertinentes
- R13.2 : Séparer décisions utilisateur et suggestions générées
- R13.3 : Distinguer historique, actuel et incertain
- R13.4 : Préserver les anciens artefacts sans adopter leurs instructions

Acceptation : Contexte actuel sourcé, couverture et lacunes explicites.

### R14 — Réutiliser les carnets existants

Priorité : P1. Rôle proposé : connaissances et interface. Dépendances : R06, R13. État : à évaluer.

- R14.1 : Inventorier notes, graphes et fonctions utiles
- R14.2 : Vérifier les opérations réellement disponibles
- R14.3 : Réutiliser références et structure adaptées
- R14.4 : Tester export et récupération

Acceptation : Carnet utile relié aux travaux sans doublon ni données secrètes publiées.

### R15 — Construire une carte vérifiable

Priorité : P1. Rôle proposé : interface. Dépendances : R06, R09, R10. État : à évaluer.

- R15.1 : Choisir graphe, canvas ou Kanban selon usage
- R15.2 : Afficher composants, connexions et dépendances
- R15.3 : Brancher les états aux événements observés
- R15.4 : Marquer données périmées, inconnues ou déconnectées
- R15.5 : Tester lisibilité, accessibilité et interactions

Acceptation : Chaque connexion possède une preuve ou est explicitement proposée ; aucune fausse indication live.

### R16 — Présenter un terminal lecture seule

Priorité : P1. Rôle proposé : interface et sécurité. Dépendances : R08, R10. État : à évaluer.

- R16.1 : Comparer composants de terminal maintenus
- R16.2 : Vérifier transport et intégration réellement supportés
- R16.3 : Contrôler authentification et exposition réseau
- R16.4 : Tester refus des entrées et reconnexion
- R16.5 : Relier un flux réel à la vue

Acceptation : Flux réel privé et lecture seule dans la surface retenue, sans confondre image et terminal.

### R17 — Comparer dix extraits vocaux

Priorité : P1. Rôle proposé : voix. Dépendances : R04, R11. État : à évaluer.

- R17.1 : Vérifier capacités, droits et budget disponibles
- R17.2 : Comparer voix officielles, création adaptée et options locales
- R17.3 : Lire paramètres de prosodie, vitesse et langues
- R17.4 : Définir un texte fixe et dix débits identifiés
- R17.5 : Produire puis contrôler dix fichiers audio
- R17.6 : Livrer les extraits et recueillir le choix

Acceptation : Dix fichiers réellement écoutables, texte comparable et paramètres explicites ; aucun extrait annoncé avant production.

### R18 — Valider la conversation vocale

Priorité : P1. Rôle proposé : interface voix. Dépendances : R17. État : à évaluer.

- R18.1 : Vérifier interruption et reprise de parole
- R18.2 : Stabiliser cadence et chaleur
- R18.3 : Évaluer variantes régionales sans caricature
- R18.4 : Distinguer réglages exposés et rendu réellement observé

Acceptation : Échange accepté à l’écoute, sans parler au-dessus de l’utilisateur ni supposer une intégration de moteur.

### R19 — Valider les applications clientes

Priorité : P1. Rôle proposé : environnement et qualité. Dépendances : R04, R05. État : à évaluer.

- R19.1 : Distinguer lancement, authentification, outils et usage
- R19.2 : Contrôler version, processus et fenêtre utilisable
- R19.3 : Comparer traces actuelles et historiques
- R19.4 : Exécuter une tâche fonctionnelle représentative
- R19.5 : Vérifier la correction sans désactiver les protections

Acceptation : Application utilisable sur un scénario réel, cause et limites documentées.

### R20 — Protéger données et accès

Priorité : P0. Rôle proposé : sécurité. Dépendances : aucune. État : à évaluer.

- R20.1 : Minimiser les données nécessaires à chaque nœud
- R20.2 : Conserver secrets hors du dépôt et des preuves publiques
- R20.3 : Réutiliser les parcours sécurisés existants
- R20.4 : Revoir autorisations persistantes et effets de bord
- R20.5 : Expurger les preuves avant publication

Acceptation : Aucun secret ou donnée privée non autorisée dans la publication ; accès proportionnés au besoin.

### R21 — Mesurer la valeur livrée

Priorité : P2. Rôle proposé : coordination livraison. Dépendances : R08, R09, R10. État : à évaluer.

- R21.1 : Choisir un cas utile et une référence de départ
- R21.2 : Exécuter, contrôler et livrer de bout en bout
- R21.3 : Mesurer temps humain, reprises, qualité et coût
- R21.4 : Décider de l’extension à partir des résultats

Acceptation : Livrable utilisable et mesures observées, sans promesse de performance non testée.

## 6. Scénario d’acceptation de référence

Une demande bornée traverse deux nœuds d’exécution et un contrôle indépendant. Un test échoue volontairement dans un espace jetable ; l’erreur est signalée, une correction autorisée est appliquée, le test repasse et la revue confirme le périmètre. La carte affiche les événements réels. Une interruption reprend depuis un état connu sans double écriture. La démonstration doit mesurer coûts et interventions humaines.

Ce scénario est proposé, non déclaré exécuté par ce dépôt. Les preuves d’une installation privée ne sont pas automatiquement des preuves publiques de ce blueprint.

## 7. Références publiques à examiner

Ces liens sont des pistes et sources de documentation, pas une certification, une recommandation finale ou une preuve d’intégration. Vérifier versions, licences et maintenance avant toute réutilisation.

- Workflows : https://docs.n8n.io/
- Agents SDK : https://openai.github.io/openai-agents-python/
- MCP : https://modelcontextprotocol.io/docs/getting-started/intro
- Raisonnement séquentiel : https://github.com/arben-adm/mcp-sequential-thinking
- Suggestions d’outils : https://github.com/spences10/mcp-sequentialthinking-tools
- Raisonnement multi-agent : https://github.com/FradSer/mcp-server-mas-sequential-thinking
- Raisonnement de code : https://github.com/mettamatt/code-reasoning
- Connaissances et raisonnement : https://github.com/Kastalien-Research/thoughtbox
- Terminal : https://github.com/tsl0922/ttyd
- Lecture de flux terminal : https://docs.asciinema.org/manual/player/loading/
- Synthèse vocale : https://docs.x.ai/developers/model-capabilities/audio/text-to-speech
- Clonage vocal : https://elevenlabs.io/docs/eleven-api/concepts/voice-cloning

Aucun code de ces projets n’est recopié ici. La disponibilité d’une fonction, les droits d’une voix, l’autorisation d’un compte et les conditions de déploiement doivent être vérifiés séparément.

## 8. Revue avant publication et acceptation

- Le contenu est-il original ou accompagné des droits nécessaires ?
- Le registre exclut-il comptes, secrets, inventaires et preuves privés ?
- Les propriétaires sont-ils proposés ou réellement assignés ?
- Les statuts décrivent-ils des résultats prouvés plutôt que des intentions ?
- L’isolation protège-t-elle les écritures tout en permettant la communication utile ?
- La solution réutilise-t-elle des composants adaptés avant d’en créer ?
- Le livrable final est-il accessible et utilisable sur le scénario retenu ?

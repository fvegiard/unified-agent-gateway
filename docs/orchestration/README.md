# Orchestration vérifiable de nœuds IA

Un blueprint documentaire pour coordonner des agents et outils existants, avec espaces de travail isolés, communication explicite et résultats vérifiables.

## État du projet

Ce paquet contient une spécification et un registre de travaux. Il ne contient pas d’orchestrateur exécutable, de service déployé, de moteur vocal ni de clips audio. Les tâches décrivent une cible à réaliser et à tester ; leur présence ne prouve pas leur réalisation. La version documentaire initiale est publiée sur la branche `docs/orchestration-blueprint-20261001` du dépôt public `unified-agent-gateway`, au [commit `75a8dca`](https://github.com/fvegiard/unified-agent-gateway/commit/75a8dcab125286e8dcf9e0db35cee4bd385ab2c3). Les quatre fichiers de cette publication ont été relus octet par octet. Cette confirmation concerne la publication documentaire ; elle ne valide pas un runtime ni les critères d’intégration.

## Relation avec la recherche existante

La [recherche ACP et passerelles LLM](../research/acp-llm-gateways.md) décrit déjà une architecture candidate. Le présent registre la complète par des exigences et critères d’acceptation ; il ne la remplace pas, ne présume pas qu’elle est choisie et ne la présente pas comme déployée.

## Principe

À la manière d’un graphe de workflows comme n8n, chaque nœud possède une responsabilité, reçoit une entrée définie et produit un résultat observable. Les agents peuvent communiquer et demander de l’aide. L’isolation porte sur les dossiers, runtimes, permissions et écritures concurrentes ; elle n’interdit pas les échanges entre IA. Les réparations croisées restent ciblées, coordonnées et autorisées.

La priorité est de réutiliser une solution maintenue plutôt que créer un nouveau moteur. Une architecture proposée comprend une coordination principale, une fonction de livraison, une fonction de qualité indépendante et des spécialistes dans leurs propres environnements.

## Contenu

- [Exigences et critères d’acceptation](requirements.md)
- [Registre structuré des tâches](tasks.json)
- [Carte des connexions : preuve limitée et cible proposée](architecture-map.md)
- [Terminal live : composant existant et critères de lecture seule](terminal-reuse.md)

- [Démonstration cloud : composants installés, tests et limites](../../examples/cloud-agent-demo/README.md)

## Méthode

1. Comprendre le résultat attendu et rechercher un équivalent existant
2. Lire la documentation officielle et les exemples de la version ciblée
3. Vérifier les capacités effectivement disponibles
4. Choisir le chemin fonctionnel le plus simple
5. Exécuter dans un périmètre isolé, observer et tester
6. Faire relire les preuves, puis livrer un résultat utilisable

Une attente, une configuration ou une réponse d’agent ne suffit pas à déclarer une tâche réussie. Les statuts inconnus restent inconnus. Les observations et preuves privées ne doivent pas être publiées pour remplir artificiellement un registre public.

## Portée de publication

Documentation originale et références publiques uniquement. Aucun historique de dépôt privé, inventaire personnel, secret, capture d’écran, donnée de compte ou code tiers n’est inclus. Le paquet n’attribue aucune licence au nom du propriétaire ; les modalités de réutilisation restent à définir par celui-ci. Les projets référencés conservent leurs propres licences et conditions.

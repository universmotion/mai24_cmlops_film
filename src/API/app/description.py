description = """ # Documentation de l'API de Recommandation de Films
## Description
Cette API permet de gérer un système de recommandations de films pour les utilisateurs. Elle gère les utilisateurs, leurs historiques de films, et propose des recommandations basées sur les films déjà vus.
Les clients sont les divers plateformes de streaming qui souhaites que leur utiliseurs reçoit des recommandations.

### Remarque
Attentions, les clients ne sont pas utilisateurs. Au sein de l'api, les clients sont des plateformes comme netflix, prime, etc...

## Authentification
L'API utilise un système d'authentification OAuth2 avec des tokens JWT. Les utilisateurs doivent être authentifiés pour accéder aux routes protégées.

## Gestion des erreurs

Les principales erreurs incluent :

- 400 Bad Request : Données manquantes ou incorrectes.
- 401 Unauthorized : Token JWT invalide ou manquant.
- 404 Not Found : Ressource non trouvée (comme un film ou un utilisateur).
- 500 Internal Server Error : Erreur interne côté serveur (ex: base de données).

## Sécurité
L'API utilise OAuth2 avec un flux password pour l'authentification des utilisateurs. Les tokens JWT sont utilisés pour sécuriser les routes et vérifier l'identité des utilisateurs.

## Auteurs
Développée par l'équipe DS.
"""

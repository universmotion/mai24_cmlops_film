description = """
## Description

This API manages a movie recommendation system for users. It handles user data, their movie watch history, and offers recommendations based on the movies they have already seen.

The clients are various streaming platforms that want their users to receive recommendations.

### Note

Be aware that clients are not the users. In the context of this API, clients are platforms like Netflix, Prime, etc.

## Authentication

The API uses an OAuth2 authentication system with JWT tokens. Users must be authenticated to access protected routes.

## Error Management

The main errors include:

- **400 Bad Request**: Missing or incorrect data.
- **401 Unauthorized**: Invalid or missing JWT token.
- **404 Not Found**: Resource not found (such as a movie or user).
- **500 Internal Server Error**: Internal server error (e.g., database issue).

## Security

The API uses OAuth2 with the password flow for user authentication. JWT tokens are used to secure the routes and verify user identity.

## Authors

Developed by the DS team.
"""

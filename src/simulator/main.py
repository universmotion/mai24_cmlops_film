"""
Nom: Simulateur de client
Auteur: MEUTER Romain


Description: Ce script fournit de données simulé de notation de film pour des utilisateurs.

Etape:
A - Connection à l'API et récupération du token d'authentification,
B - Simulation affluence d'utilisateurs:
    1 - Récupération et aggregations des utlisateurs dans les données simulées,
    2 - Générateur d'affluence (fonction cosinus bruité avec des pics à 19/20 heures et minima à 8 heures du matin dans un contexte français),
    3 - Tirage aléatoire des utilisateurs présent dans la base de données en fonction du nombre d'affluence (par exemple affluence à 130 donc 130 utilisateurs tiré sans remise),
C - [BOUCLE] Simulation de contenu vu et noté par l'utilisateur:
    1 - Pour chaque utilsateur tiré:
        a - un délai aléatoire intertraitement (entre 0 et 10)
        b - On génère deux nombres:
            - Un nombre de vision de film vu (entre 2 et 10);
            - Le niveau moyenne d'appréciation des films de l'utilisateur entre 1 et 5 (par exemple A à pour moyenne de note 3.5),
        c - Envoie des requetes:
            1 - Pour chaque requete, il y a 75 % de probabilité que le film vu soit un film recommandé avant (vu pour datashifting),
            2 - La note du film envoyé pour l'historique des films vu suit une loi normal avec sigma à 2 et mu avec le niveau moyenne d'appréciation de l'utilisateur (donc rating = N(mu_user, 2) reprennons l'utilisateur A donc pour A N(3.5,2))
"""

import requests
import random
from datetime import datetime
import math
import time
from pathlib import Path
import pandas as pd

print("### "*20)
print(datetime.now().strftime('%Y-%m-%d, %H heure'))
print("### "*20)



api_host = "http://localhost:8000"

token_url = api_host + "/token"
payload_token = {
    "username": "romain",
    "password": "romain"
}

response_token = requests.post(token_url, data=payload_token)


def ask_for_recommandation(payload_recommendations, headers, mu_rating):
    recommendations_url = api_host + "/recommendations"
    rating = max(0,
                 min(5,
                     random.normalvariate(mu=mu_rating, sigma=2)
                     )
                 )
    rating = round(rating, 2)
    payload_recommendations["list_movie"]["listMovie"][0]["rating"] = rating
    response_recommendations = requests.post(
        recommendations_url, json=payload_recommendations, headers=headers)
    if response_recommendations.status_code == 200:
        reco = response_recommendations.json().get("recommendation")
        print("Reçu avec comme film reco", reco)
        return reco["movieId"]
    else:
        print(
            f"Erreur lors de l'envoi des recommandations: erreur code {response_recommendations.status_code}")


#

doc = Path("/home/romain/Documents/Formation/mai24_cmlops_film/data/processed")\
    .glob("**/user_matrix.csv")
doc = list(doc)
users = pd.concat(
    [pd.read_csv(d, sep=",") for d in doc],
    axis=0
)
movies = pd.read_csv(
    "/home/romain/Documents/Formation/mai24_cmlops_film/data/external/movies.csv")


# Génération d'affluence suivant une fonction cosinus bruitée
hours = datetime.now().hour
affulence = math.cos(2*math.pi*((hours-20)/24)) + 1
number_of_user = int(5 + 50*affulence + random.randint(a=1, b=25))
random_users_list = users["userId"].sample(n=number_of_user)

print("Affluence", number_of_user)

for user_example in random_users_list:
    time.sleep(max(0, random.normalvariate(mu=3, sigma=10)))
    print("\n")
    print("### USER: ", user_example, " ###")
    mu_rating = random.randint(a=1, b=5)
    number_rating = random.randint(a=2, b=10)
    payload_recommendations = {
        "user": {
            "userId": user_example
        },
        "list_movie": {
            "listMovie": [
                {
                    "moviesId": 0,
                    "rating": 0
                }
            ]
        }
    }
    if response_token.status_code == 200:
        token = response_token.json().get("access_token")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        movieId = 1
        for i in range(number_rating):
            if not movieId is None:
                if random.random() <= 0.75:# Aléa de si le user decide de voir le film ou non
                    payload_recommendations["list_movie"]["listMovie"][0]["moviesId"] = movieId
                else:
                    payload_recommendations["list_movie"]["listMovie"][0]["moviesId"] = movies["movieId"].sample(n=1).to_list()[0]
                movieId = ask_for_recommandation(
                    payload_recommendations=payload_recommendations,
                    headers=headers,
                    mu_rating=mu_rating
                )
    else:
        print(f"Erreur d'authentification: {response_token.status_code}")

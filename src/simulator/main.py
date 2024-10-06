import requests
import random
from datetime import datetime
import math
import time

print("### "*20)
print(datetime.now().strftime('%Y-%m-%d, %H heure'))
print("### "*20)

hours = datetime.now().hour 
affulence = math.cos(2*math.pi*((hours-20)/24)) + 1

api_host = "http://localhost:8000"

token_url = api_host + "/token"
payload_token = {
    "username": "romain",
    "password": "romain"
}

response_token = requests.post(token_url, data=payload_token)



def ask_for_recommandation(payload_recommendations, headers):
    recommendations_url = api_host + "/recommendations"
    rating =  max(0, 
                  min(5, 
                      random.normalvariate(mu=2.5, sigma=2)
                    )
                )
    payload_recommendations["list_movie"]["listMovie"][0]["rating"] = rating
    response_recommendations = requests.post(recommendations_url, json=payload_recommendations, headers=headers)

    if response_recommendations.status_code == 200:
        reco = response_recommendations.json().get("recommendation")
        print("Reçu avec comme film reco", reco)
        return reco["movieId"]
    else:
        print(f"Erreur lors de l'envoi des recommandations: {response_recommendations.status_code}")


### ####


number_of_user = int(5 + 50*affulence + random.randint(a=1, b=25))
print("Affluence", number_of_user)

for u in range(number_of_user):
    time.sleep(max(0, random.normalvariate(mu=3, sigma=10)))
    user_example = random.randint(a=1, b=130000)
    print("\n")
    print("### USER: ", user_example, " ###")
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

    number_rating = random.randint(a=2, b=10)

    if response_token.status_code == 200:
        token = response_token.json().get("access_token")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        movieId = 1
        for i in range(number_rating):
            payload_recommendations["list_movie"]["listMovie"][0]["moviesId"] = movieId
            movieId = ask_for_recommandation(payload_recommendations=payload_recommendations, headers=headers)
    else:
        print(f"Erreur d'authentification: {response_token.status_code}")

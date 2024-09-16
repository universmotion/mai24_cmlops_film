import os

if os.environ["HOME"] == "/home/romain":
    import dotenv
    dotenv.load_dotenv("/home/romain/Documents/Formation/mai24_cmlops_film/src/API/.env")

from fastapi import FastAPI
from route.recommandation import reco_router
from route.manage_client import router_client

app = FastAPI(
    title="Movies Recommendation System API", 
    version="0.2.0", 
    debug=True,
)

app.include_router(router_client)
app.include_router(reco_router)
import os
is_local = False
if os.environ["HOME"] == "/home/romain":
    import dotenv
    PATH_ENV = "/home/romain/Documents/Formation/mai24_cmlops_film/src/API/.env"
    dotenv.load_dotenv(PATH_ENV)
    is_local = True
from fastapi import FastAPI
from route.recommandation import reco_router
from route.manage_client import router_client
from prometheus_fastapi_instrumentator import Instrumentator
from description import description



app = FastAPI(
    title="Movies Recommendation System API",
    version="0.4.0", description=description, openapi_tags=[
        {
            "name": "Client",
            "description": "Routes for managing API clients."
        },
        {
            "name": "Recommendation",
            "description": "Route providing recommendations to users."
        }
    ], debug=is_local
)

Instrumentator().instrument(app).expose(app)

app.include_router(router_client)
app.include_router(reco_router)

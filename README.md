Movie recommandation system API 
==============================

This project is dedicated to streaming platforms such as Netflix, prime, etc... We recommend movies for your users based on their movie history. [List of movies](./data/external/movies.csv) that we can recommend (it's updated each day).

## A - Project Organization

    .
    ├── data                                          
    │   ├── initial_data                           # Initial data before any processing.
    │   ├── no_injected_data                       # Poorly processed or non-injected data in the database.
    │   ├── processed                              # Processed or cleaned data.
    │   ├── raw                                    # Raw data, without transformation.
    │   └── simulation_data                        # Data generated by simulations.
    ├── models                                     # Folder for machine learning models.
    │   └── experience                             # MLFlow experiment folder.
    └── src                                               
        ├── API                                    # Contains API-related files.
        │   ├── app                                # API script.
        │   └── kubernetes                         # Files related to API management under Kubernetes.
        ├── database                               
        │   ├── backup_db                          # Database backups.
        │   ├── kubernetes                         # Files related to database management under Kubernetes.
        │   └── migration                          # Scripts for database migrations.
        ├── monitoring                             
        │   └── grafana                            # Integration with Grafana for data visualization.
        │       └── dashboard                      # Grafana dashboard for monitoring metrics.
        ├── provider                               
        │   ├── dags                               # DAGs for orchestrating workflows (Airflow).
        │   ├── images                             # Folder containing images and scripts for specific tasks.
        │   ├── kubernetes                         # Management scripts for Kubernetes.
        │   │   ├── dag_env                        # DAG environment under Kubernetes.
        │   │   └── installation                   # Scripts for installing Kubernetes components.
        │   └── logs                               # Contains system and operation logs.
        └── simulator                              # Scripts for simulating API usage traffic.



## B - Architecture

![software architecture](/documentation/archi.png "architecture")

### B.1 - Components

#### B.1.a - Kubernetes:


| Namespace Name         | App Version       | Helm Chart/Docker Image Version (if available)     |
| ---------------------- | ----------------  | -------------------------------------------------  |
| Airflow                | v2.9.3            | chart: airflow-1.15.0                              |
| kube-prometheus-stack  | v0.77.1           | chart: kube-prometheus-stack-65.0.0                |
| database (PostgreSQL)  | v16               | image: postgres:16                                 |
| api (FastAPI)          | v0.112.2          | image: leutergmail/api-sys-reco-projet-ds:latest   |


- **Airflow** *(represented in blue here)*:
    - Two DAGs are in place, executed once per day, ideally between 7 AM and 8 AM (after peak traffic hours).
        - **DAG inject-data**:
            - *Task 1*: Fetches simulated data from the `/simulation_data` folder and stores it in a folder called `/raw`.
            - *Task 2*: Processes the data from `/raw`, creates user characteristic vectors for recommendations, and stores them in `/processed`.
            - *Task 3*: Fetches data from `/raw` (those already properly cleaned) and from `/processed` to inject into the database.
        - **DAG train-model**: Fetches new data to retrain the algorithm and then stores the trained model in the `/models` folder.

- **Database** *(PostgreSQL represented in gray)*:
    - The database contains four tables:
        - *movies*: contains a list of all movies,
        - *users*: contains users along with their characteristic vectors,
        - *movies_users_rating*: contains user ratings associated with each movie,
        - *clients*: contains credentials for clients (e.g., video-on-demand services like Netflix).

- **API** *(FastAPI represented in green)*:
    - The API is secured and provided to clients such as streaming platforms. It offers four main routes:
        - **POST** `/create-client`: Allows a user to register in the database by providing credentials and a password.
        - **POST** `/token`: Generates an authentication token based on provided credentials and password.
        - **POST** `/recommendations`: This route has several use cases (requires an authentication token):
            - If a user is specified (with or without a movie history), a movie recommendation is returned.
            - If no user is specified but a history is provided, a new user ID is generated, and a movie recommendation is returned.
            - If neither a user nor a history is provided, an error is generated.
        - **GET** `/metrics`: Allows monitoring of the API via Grafana.

- **Monitoring** *(Grafana and Prometheus represented in orange)*:
    - Prometheus scrapes all data and metrics to monitor activity. Several connections are configured:
        - By default, a connection to Kubernetes (provided with the chart).
        - A connection to Airflow via StatsD to export metrics.
        - A connection to FastAPI via the `fastapi_prometheus_instrumentor` package.
    - The data collected by Prometheus allows Grafana to create visualizations, including:
        - A series of default visualizations for Kubernetes,
        - Custom dashboards:
            - A dashboard for API monitoring,
            - A dashboard for Airflow monitoring,
            - A dashboard for model monitoring.


## C - Steps to Follow

**Convention:** All scripts must be executed from the root directory, specifying the relative file path.

### C.1. - Install Requirements

#### C.1.A. - Kubernetes Installation

```
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.29.5+k3s1 sh -s - --write-kubeconfig-mode 644
```

#### C.1.B. - Helm Installation

```
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm=3.15.1-1
```

### C.2. - Install the Entire Application

```
bash setup.sh
```

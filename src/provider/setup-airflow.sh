helm repo add apache-airflow https://airflow.apache.org
kubectl create namespace airflow
mkdir -p ./src/provider/logs
sudo kubectl config set-context --current --namespace=airflow
# helm -n airflow upgrade --install airflow apache-airflow/airflow

## Log / dag / data folder 
kubectl create -f ./src/provider/kubernetes/installation/airflow-local-dags-folder-pv.yaml
kubectl create -f ./src/provider/kubernetes/installation/airflow-local-dags-folder-pvc.yaml
kubectl create -f ./src/provider/kubernetes/installation/airflow-local-logs-folder-pv.yaml
kubectl create -f ./src/provider/kubernetes/installation/airflow-local-logs-folder-pvc.yaml
kubectl create -f ./src/provider/kubernetes/dag_env/data-folder-pv.yaml
kubectl create -f ./src/provider/kubernetes/dag_env/data-folder-pvc.yaml

## Env for DAG
kubectl create -f ./src/provider/kubernetes/dag_env/sql-conn-configmap.yaml
kubectl create -f ./src/provider/kubernetes/dag_env/sql-conn-secret.yaml

# update helm
helm template apache-airflow/airflow -f ./src/provider/kubernetes/installation/values.yaml > ./src/provider/kubernetes/installation/templates.yaml
kubectl -n airflow apply -f ./src/provider/kubernetes/installation/templates.yaml

# Se connecter à la plateforme
# kubectl port-forward svc/airflow-webserver --address 0.0.0.0 8080:8080
# ou
# kubectl port-forward svc/release-name-webserver --address 0.0.0.0 8080:8080


## Crée une MAJ helm
# kubectl -n airflow delete all --all 
# cat my_values.yaml >> values.yaml
# helm template apache-airflow/airflow -f values.yaml > templates.yaml
# kubectl -n airflow apply -f templates.yaml
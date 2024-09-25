if [! -d "./src/provider/logs"]; then
mkdir -p ./src/provider/logs ;
fi

kubectl create namespace airflow
helm repo add apache-airflow https://airflow.apache.org
sudo kubectl config set-context --current --namespace=airflow

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
helm install airflow -n airflow
helm upgrade --install airflow apache-airflow/airflow -f ./src/provider/kubernetes/installation/values.yaml -n airflow

# Se connecter à la plateforme
# kubectl port-forward svc/airflow-webserver --address 0.0.0.0 8080:8080
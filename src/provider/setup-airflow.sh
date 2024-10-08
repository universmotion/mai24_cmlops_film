if [! -d "./src/provider/logs"]; then
mkdir -p ./src/provider/logs ;
fi

kubectl create namespace airflow
helm repo add apache-airflow https://airflow.apache.org
sudo kubectl config set-context --current --namespace=airflow

kubectl create secret generic mydatabase --from-literal=connection=postgresql://admin:admin@10.43.150.34:5432/postgres

## Log / dag / data folder 
kubectl create -f ./src/provider/kubernetes/installation/airflow-local-dags-folder-pv-pvc.yaml
kubectl create -f ./src/provider/kubernetes/installation/airflow-local-logs-folder-pv-pvc.yaml
kubectl create -f ./src/provider/kubernetes/dag_env/data-folder-pv-pvc.yaml
kubectl create -f ./src/provider/kubernetes/dag_env/model-folder-pv-pvc.yaml

## Env for DAG
kubectl create -f ./src/provider/kubernetes/dag_env/sql-conn-configmap.yaml
kubectl create -f ./src/provider/kubernetes/dag_env/sql-conn-secret.yaml

# update helm
helm install airflow -n airflow
helm upgrade --install airflow apache-airflow/airflow -f ./src/provider/kubernetes/installation/values.yaml -n airflow

# Se connecter à la plateforme
# kubectl port-forward svc/airflow-webserver -n airflow --address 0.0.0.0 8080:8080
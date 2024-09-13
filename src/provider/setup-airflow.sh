# Install kube
# curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.29.5+k3s1 sh -s - --write-kubeconfig-mode 644

# Install helm
# curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
# sudo apt-get install apt-transport-https --yes
# echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
# sudo apt-get update
# sudo apt-get install helm=3.15.1-1


helm repo add apache-airflow https://airflow.apache.org
kubectl create namespace airflow
sudo kubectl config set-context --current --namespace=airflow
kubectl create -f ./src/provider/kubernetes/installation/airflow-local-dags-folder-pv.yaml
kubectl create -f ./src/provider/kubernetes/installation/airflow-local-dags-folder-pvc.yaml
kubectl create -f ./src/provider/kubernetes/installation/airflow-local-logs-folder-pv.yaml
kubectl create -f ./src/provider/kubernetes/installation/airflow-local-logs-folder-pvc.yaml



helm -n airflow upgrade --install airflow apache-airflow/airflow

# Maj
kubectl -n airflow delete all --all 
helm template apache-airflow/airflow -f ./src/provider/kubernetes/installation/values.yaml > ./src/provider/kubernetes/installation/templates.yaml
kubectl -n airflow apply -f ./src/provider/kubernetes/installation/templates.yaml


# Import dag
kubectl create -f ./src/provider/kubernetes/dag_env/python-provider.yaml
kubectl create -f ./src/provider/kubernetes/dag_env/order-data-folder-pv.yaml
kubectl create -f ./src/provider/kubernetes/dag_env/order-data-folder-pvc.yaml

kubectl create -f ./src/provider/kubernetes/dag_env/sql-conn-configmap.yaml
kubectl create -f ./src/provider/kubernetes/dag_env/sql-conn-secret.yaml
# Se connecter à la plateforme
# kubectl port-forward svc/airflow-webserver --address 0.0.0.0 8080:8080
# ou
# kubectl port-forward svc/release-name-webserver --address 0.0.0.0 8080:8080


## Crée une MAJ helm
# kubectl -n airflow delete all --all 
# cat my_values.yaml >> values.yaml
# helm template apache-airflow/airflow -f values.yaml > templates.yaml
# kubectl -n airflow apply -f templates.yaml
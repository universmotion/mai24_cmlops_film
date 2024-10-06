### Requirements

## Install kube
# curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.29.5+k3s1 sh -s - --write-kubeconfig-mode 644

## Install helm
# curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
# sudo apt-get install apt-transport-https --yes
# echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
# sudo apt-get update
# sudo apt-get install helm=3.15.1-1

## Stop
kubectl -n database delete all --all
kubectl -n api delete all --all
helm uninstall airflow -n airflow 
helm uninstall prometheus -n monitoring 


if [ ! -d "./data" ]; then
    mkdir data;
fi

echo "\n\n\n ### Installation de la base de données"
bash ./src/database/setup-db.sh

echo "\n\n\n ### Installation de l'api"
bash ./src/API/setup-api.sh

echo "\n\n\n ### Installation d'airflow"
bash ./src/provider/setup-airflow.sh

echo "\n\n\n ### Installation du monitoring"
bash ./src/monitoring/setup-monitoring.sh



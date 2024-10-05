kubectl create namespace database
sudo kubectl config set-context --current --namespace=database

kubectl apply -f ./src/database/kubernetes/pv-pvc-postgres.yaml
kubectl apply -f ./src/database/kubernetes/service.yaml
kubectl apply -f ./src/database/kubernetes/secret.yaml 
kubectl apply -f ./src/database/kubernetes/configmap.yaml 
kubectl apply -f ./src/database/kubernetes/stateful.yaml 

## psql -h 10.43.150.34 -p 5432 -U admin -d postgresdb
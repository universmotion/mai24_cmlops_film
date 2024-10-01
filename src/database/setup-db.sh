kubectl create namespace database
sudo kubectl config set-context --current --namespace=database

kubectl apply -f ./src/database/DB/pv-pvc-postgres.yaml
kubectl apply -f ./src/database/DB/service.yaml
kubectl apply -f ./src/database/DB/secret.yaml 
kubectl apply -f ./src/database/DB/configmap.yaml 
kubectl apply -f ./src/database/DB/stateful.yaml 

## psql -h 10.43.150.34 -p 5432 -U admin -d postgresdb
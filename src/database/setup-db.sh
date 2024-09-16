kubectl create namespace sys-reco-dev
sudo kubectl config set-context --current --namespace=sys-reco-dev

kubectl apply -f DB/pv-pvc-postgres.yaml
kubectl apply -f DB/service.yaml
kubectl apply -f DB/secret.yaml 
kubectl apply -f DB/configmap.yaml 
kubectl apply -f DB/stateful.yaml 

## psql -h 10.43.150.34 -p 5432 -U admin -d postgresdb
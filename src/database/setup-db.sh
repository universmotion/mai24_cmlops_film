## Install kube
## curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.29.5+k3s1 sh -s - --write-kubeconfig-mode 644

kubectl create namespace sys-reco-dev
sudo kubectl config set-context --current --namespace=sys-reco-dev

kubectl apply -f DB/pv-pvc-postgres.yaml
kubectl apply -f DB/service.yaml
kubectl apply -f DB/secret.yaml 
kubectl apply -f DB/configmap.yaml 
kubectl apply -f DB/stateful.yaml 

## psql -h 10.43.150.34 -p 5432 -U admin -d postgresdb
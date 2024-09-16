kubectl create namespace api
sudo kubectl config set-context --current --namespace=api

kubectl apply -f ./src/API/kubernetes/fastapi-configmap.yaml
kubectl apply -f ./src/API/kubernetes/fastapi-secret.yaml
kubectl apply -f ./src/API/kubernetes/fastapi-load-balancer.yaml
kubectl apply -f ./src/API/kubernetes/fastapi-deployment.yaml 

## local -> uvicorn api:app --reload
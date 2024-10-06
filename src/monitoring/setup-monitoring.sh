## Config: https://github.com/prometheus-community/helm-charts/blob/main/charts/kube-prometheus-stack/README.md
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Dashboard
for file in ./src/monitoring/grafana/dashboard/*.yaml
do
  kubectl apply -f $file
done

# helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring  --create-namespace --set grafana.service.type=NodePort --set promotheus.service.type=NodePort
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack -f ./src/monitoring/custom_values.yaml -n monitoring --debug
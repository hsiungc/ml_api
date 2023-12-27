#! /bin/bash

minikube start --kubernetes-version=v1.23.12;
sleep 1

eval $(minikube docker-env)

# Apply namespace
kubectl apply -f ../infra/namespace.yaml
kubectl config set-context --current --namespace=w255

# Apply stubs
# kubectl delete -k ../.k8s/overlays/dev

kubectl apply -k ../.k8s/bases
kubectl apply -k ../.k8s/overlays/dev
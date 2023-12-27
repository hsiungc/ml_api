#! /bin/bash 
set -e

# Push updates to git repository
COMMIT_MSG="$1"

if [[ -n "$(git status --porcelain)" ]]
then
    git add --all
    git commit -m "${COMMIT_MSG}"
    git push origin main
    sleep 2
fi;

# Change context to w255-aks
if [[ "$(kubectl config current-context)" == "minikube" ]]
then
    kubectl config use-context w255-aks
fi;

# Build docker image
cd mlapi/
TAG=$(git rev-parse --short HEAD)
IMAGE_NAME="project:${TAG}"

docker build . -t ${IMAGE_NAME}
echo ${IMAGE_NAME}

# Push image to Azure repository
ACR_DOMAIN=w255mids.azurecr.io
IMAGE_PREFIX=$(az account list --all | jq '.[].user.name' | grep -i berkeley.edu | awk -F@ '{print $1}' | tr -d '"' | uniq)

IMAGE_FQDN="${ACR_DOMAIN}/${IMAGE_PREFIX}/${IMAGE_NAME}"

az acr login --name w255mids

docker tag ${IMAGE_NAME} ${IMAGE_FQDN}
docker push ${IMAGE_FQDN}

# Update patch tag
sed "s/\[TAG\]/${TAG}/g" ../.k8s/overlays/prod/patch-deployment-mlapi_copy.yaml > ../.k8s/overlays/prod/patch-deployment-mlapi.yaml

# Update deployment in Azure
kubectl apply -k ../.k8s/overlays/prod

# Clean resources
# docker image prune

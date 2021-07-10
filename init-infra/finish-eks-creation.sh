#!/bin/bash
set -ux -o pipefail

export KUBECONFIG=~/.kube/config
export LBC_VERSION="v2.2.0"

function retry {
  local n=1
  local max=5
  local delay=2
  while true; do
    "$@" && break || {
      if [[ $n -lt $max ]]; then
        ((n++))
        echo "Command failed. Attempt $n/$max:"
        sleep $delay;
      else
        fail "The command has failed after $n attempts."
      fi
    }
  done
}

function get_k8s_credentials {
  aws eks --region us-east-1 update-kubeconfig --name movies-eks
}

function add_role_to_attach_worker_nodes {

  cat << EOF | tee configMap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::${AWS_ACCOUNT_ID}:role/terraform-eks-movies-node
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:bootstrappers
        - system:nodes

EOF

  kubectl apply -f configMap.yaml
  rm -f configMap.yaml
  # Usually it takes less that 5 min for nodes to become ready
  sleep 300
}

function deploy_alb_controller {
  # Documentation:
  # https://docs.aws.amazon.com/eks/latest/userguide/alb-ingress.html
  # https://www.eksworkshop.com/beginner/130_exposing-service/ingress_controller_alb/

  # Check that Helm is installed
  helm version --short

  # Activate OIDC provider for k8s
  eksctl utils associate-iam-oidc-provider --region us-east-1 --cluster movies-eks --approve

  # Create an IAM policy for ALB controller
  curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.2.0/docs/install/iam_policy.json
  aws iam create-policy --policy-name AWSLoadBalancerControllerIAMPolicy --policy-document file://iam_policy.json
  rm -f iam_policy.json

  # Create a service account for ALB controller
  retry eksctl create iamserviceaccount \
    --cluster movies-eks \
    --namespace kube-system \
    --name aws-load-balancer-controller \
    --attach-policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/AWSLoadBalancerControllerIAMPolicy \
    --override-existing-serviceaccounts \
    --approve

  kubectl apply -k github.com/aws/eks-charts/stable/aws-load-balancer-controller/crds?ref=master
  kubectl get crd

  helm repo add eks https://aws.github.io/eks-charts
  helm upgrade -i aws-load-balancer-controller \
      eks/aws-load-balancer-controller \
      -n kube-system \
      --set clusterName=movies-eks \
      --set serviceAccount.create=false \
      --set serviceAccount.name=aws-load-balancer-controller \
      --set image.tag="${LBC_VERSION}"

  kubectl -n kube-system rollout status deployment aws-load-balancer-controller
  echo "ALB controller has been successfully deployed to the EKS cluster"
}

retry get_k8s_credentials
retry add_role_to_attach_worker_nodes
retry deploy_alb_controller

exit 0
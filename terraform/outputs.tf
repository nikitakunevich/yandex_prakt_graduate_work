#####################################
# cloudfront data                   #
#####################################

output "cloudfront-domain-name" {
  value = aws_cloudfront_distribution.s3_distribution.domain_name
}

output "cloudfront-key-id" {
  value = aws_cloudfront_public_key.movies-on-demand-api-key.id
}

#####################################
# kubeconfig for client connections #
#####################################

locals {
  kubeconfig = <<KUBECONFIG


apiVersion: v1
clusters:
- cluster:
    server: ${aws_eks_cluster.movies.endpoint}
    certificate-authority-data: ${aws_eks_cluster.movies.certificate_authority.0.data}
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
    user: aws
  name: aws
current-context: aws
kind: Config
preferences: {}
users:
- name: aws
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1alpha1
      command: aws-iam-authenticator
      args:
        - "token"
        - "-i"
        - "${var.cluster-name}"
KUBECONFIG
}

output "kubeconfig" {
  value = local.kubeconfig
}

############################################
# configmap for workers to join the master #
############################################

locals {
  config_map_aws_auth = <<CONFIGMAPAWSAUTH


apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: ${aws_iam_role.movies-node.arn}
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:bootstrappers
        - system:nodes
CONFIGMAPAWSAUTH
}

output "config_map_aws_auth" {
  value = local.config_map_aws_auth
}
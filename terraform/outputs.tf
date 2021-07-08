#####################################
# cloudfront data                   #
#####################################

output "cloudfront-domain-name" {
  value = aws_cloudfront_distribution.s3_distribution.domain_name
}

output "cloudfront-key-id" {
  value = aws_cloudfront_public_key.movies-on-demand-api-key.id
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
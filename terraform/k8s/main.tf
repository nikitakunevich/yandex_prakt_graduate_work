# Retrieve EKS cluster information
provider "aws" {
  region = "us-east-1"
}

data "aws_eks_cluster" "cluster" {
  name = data.terraform_remote_state.infra.outputs.cluster-id
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority.0.data)
  exec {
    api_version = "client.authentication.k8s.io/v1alpha1"
    command     = "aws"
    args = [
      "eks",
      "get-token",
      "--cluster-name",
      data.aws_eks_cluster.cluster.name
    ]
  }
}
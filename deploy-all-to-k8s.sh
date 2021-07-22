#!/bin/bash

set -eux

cd terraform/k8s

# Creating dynamic terraform backend config, since terraform doesn't support using variables in the 'backend' section
cat << EOF | tee terraform-backend.tf
terraform {

  required_version = "= 0.13.5"

  backend "s3" {
    bucket         = "tfstate-${AWS_ACCOUNT_ID}"
    key            = "k8s.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tfstate-locks"
    encrypt        = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.38.0"
    }

    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.0.1"
    }
  }
}

data "terraform_remote_state" "infra" {
  backend = "s3"

  config = {
    bucket         = "tfstate-${AWS_ACCOUNT_ID}"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tfstate-locks"
    encrypt        = true
  }
}
EOF

terraform init
terraform apply -auto-approve

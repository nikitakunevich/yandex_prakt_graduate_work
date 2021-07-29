#!/bin/bash

set -eux

# Creating dynamic terraform backend config, since terraform doesn't support using variables in the 'backend' section
cat << EOF | tee terraform/dns/remote-state.tf
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

cd terraform/dns
. .envrc
terraform init
terraform apply -auto-approve

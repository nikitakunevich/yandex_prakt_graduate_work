#!/bin/bash

set -eux

# Clean terraform providers from the previous infra
find . -name .terraform -type d -exec rm -rf {} \; || true
find . -name terraform.tfstate -type f -exec rm -f {} \; || true

cd init-infra

terraform init
terraform apply -auto-approve

cd ../terraform

# Creating dynamic terraform backend config, since terraform doesn't support using variables in the 'backend' section
cat << EOF | tee main.tf
terraform {
  required_version = "= 0.13.5"

  backend "s3" {
    bucket         = "tfstate-${AWS_ACCOUNT_ID}"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tfstate-locks"
    encrypt        = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 3.38.0"
    }
  }
}
EOF

terraform init
terraform apply -auto-approve

cd ../init-infra
./finish-eks-creation.sh

echo ""
echo ""
echo "######################################################"
echo "IMPORTANT infrastructure components names and outputs!"
echo "######################################################"
echo ""

cd ../terraform
terraform output | tee OUTPUT.TXT

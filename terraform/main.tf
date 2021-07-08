terraform {
  required_version = "= 0.13.5"

  backend "s3" {
    bucket         = "tfstate-062117947425"
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

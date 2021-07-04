terraform {
  required_version = "= 0.13.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 3.38.0"
    }
  }
}

variable "aws_account_id" {
  type        = number
  description = "ID of the AWS account in a number format. Example: 093310752320"
}

resource "aws_s3_bucket" "tfstate" {
  bucket = "tfstate-${var.aws_account_id}"

  lifecycle {
    prevent_destroy = true
  }

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "tfstate-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
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
  type        = string
  description = "ID of the AWS account in a number format. Example: 093310752320"
}

resource "aws_s3_bucket" "tfstate" {
  bucket = "tfstate-${var.aws_account_id}"

  lifecycle {
    prevent_destroy = false
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

resource "aws_s3_bucket_policy" "read-only" {
  bucket = aws_s3_bucket.tfstate.id

  policy = jsonencode({
    Version: "2012-10-17",
    Statement: [
        {
            Effect: "Allow",
            Principal: {
                "AWS": "arn:aws:iam::826593466528:user/dnsadmin"
            },
            Action: [
                "s3:GetObject",
                "s3:PutObject",
                "s3:PutObjectAcl"
            ],
            Resource: [
                "${aws_s3_bucket.tfstate.arn}/*"
            ]
        }
    ]
  })
}
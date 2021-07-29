data "terraform_remote_state" "infra" {
  backend = "s3"

  config = {
    bucket         = "tfstate-104814218041"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tfstate-locks"
    encrypt        = true
  }
}

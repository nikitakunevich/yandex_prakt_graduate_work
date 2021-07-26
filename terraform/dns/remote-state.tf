data "terraform_remote_state" "infra" {
  backend = "s3"

  config = {
    bucket         = "tfstate-674667269087"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tfstate-locks"
    encrypt        = true
  }
}

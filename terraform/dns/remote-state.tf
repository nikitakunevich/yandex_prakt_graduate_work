data "terraform_remote_state" "infra" {
  backend = "s3"

  config = {
    bucket         = "tfstate-190103567417"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tfstate-locks"
    encrypt        = true
  }
}

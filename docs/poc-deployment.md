# POC deployment guide

## 1 - Create new AWS account
https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/

## 2 - Create an admin user in the AWS account
- Create IAM user: https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started_create-admin-group.html
- Create access keys for IAM users: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html
## 3 - Prepare the AWS account for using Terraform

```bash
cd tools

# clean local terraform state and installed providers 
# to not interfere with a previous deployment
./clean-terraform-providers.sh

# export variables for accessing AWS account
export TF_VAR_aws_account_id=257749931526
export AWS_ACCESS_KEY_ID="<your-access-key>"
export AWS_SECRET_ACCESS_KEY="<your-secret-key>"
export AWS_DEFAULT_REGION=us-east-1

# initialize download Terraform providers
terraform init

# apply terraform resources configuration
terraform apply
```

## 4 - Deploy Cloudfront and S3 resources using Terraform

### 4.1 Edit `terraform/main.tf` file
Terraform doesn't allow suing variables in remote state configuration. 
The bucket name for Terraform state should be set manually. It's a one-time operation for an AWS account.

Change the bucket name to comply the format `tfstate-${aws_account_id}`. Example:

```terraform
backend "s3" {
  bucket = "tfstate-257749931526"
  ...
}
```
### 4.2 Deploy resources using terraform
```bash
terraform init
terraform apply
```

## 5 - Upload sample data using `s3-uploader`
```bash
python main.py --bucket movies-189895028386 --filename ../sample-data/girl-showing-rainbow.mp4 --folder assets01
```

## 6 - Edit `movies-on-deman-api` configuration
images/movies-on-demand/src/config.py:
```python
cf_key_id = "K33LU8UGJYKH9R"
cf_domain_name = "d3cyckes3v9dct.cloudfront.net"
```
You can find proper values in the output of `terraform apply` in step 4.2.

## 7 - Run `movies-on-deman-api`
```bash
uvicorn main:app
```

## 8 - Get a signed URL
```bash
curl --location --request POST 'http://127.0.0.1:8000/api/v1/movie_private_link' \
--header 'Content-Type: application/json' \
--data-raw '{
    "id": "93a9fe05-a816-422d-97e0-6e8f718b0027"
}'
```

## 9 - Open a web browser and check that it can download a sample file
Example working URL:
`https://d3cyckes3v9dct.cloudfront.net/assets/girl-showing-rainbow.mp4?Expires=1625555257&Signature=cMoF2w2xoIIDC83ePfxjv7Q4m1K5d81qr4nAcIGgtt~kXY49i5xdul3RPYQchM38PXsZ0dG9wpQ98aZHWau7mlpNAuDtf4-0zDIL6mxkWXwFeM3OGCXaEt2FMQ8l58VbL5fT7db6fDq~SdWQESz4qwkB6NKr5lp6gmO-gKrp~l~r9SHnZWbUgrzQ1VYFPbrIKk0BeTbzTU-7IKYrGZ-Q6rQTd1QKPwjoR~HSJbW1z7tZkzQqfLMkSeLPstYGgkPxu-vYguPtvs8EhAwTTxUOuXx~FFxkYRTKOj3g3AhTdhxnD9zplI2oU1oRQnj8qmLIqjSpjoQa7gOrP7AfeJDenA__&Key-Pair-Id=K33LU8UGJYKH9R`

## 10 - Check that direct S3 access does NOT work
Example NOT working direct S3 URL:
`https://<bucket-name>.s3.amazonaws.com/assets/girl-showing-rainbow.mp4`

## 11 - Check that Cloudfront URL without a signature does not work
Example NOT working Cloudfront URL:
`https://d3cyckes3v9dct.cloudfront.net/assets/girl-showing-rainbow.mp4`

# POC demo completed!
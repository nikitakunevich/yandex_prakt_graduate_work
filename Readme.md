# Initializing infrastructure in a new clean AWS account

1. cd `root_dir_of_the_repo`
2. Add environment variables to the file `.envrc.private` (the values are just example):
```bash
export TF_VAR_aws_account_id=241284480095
export AWS_ACCOUNT_ID=241284480095
export AWS_ACCESS_KEY_ID=AKIATQLNM7RPS6J6N6PO
export AWS_SECRET_ACCESS_KEY=rf2ro0M1N1jK2fERRQKahFMrt6SoatDYS0Q2WGug
```
3. Run `DO_ALL.SH`:
```bash
./init-infra.sh
```
4. Grab a cup of coffee and relax for 40-50 minutes :)

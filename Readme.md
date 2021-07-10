# Initializing infrastructure in a new clean AWS account

1. cd `root_dir_of_the_repo`
2. Export environment variables (the values are just example):
```bash
export KUBECONFIG=~/.kube/config
export TF_VAR_aws_account_id=791903720429
export AWS_ACCOUNT_ID=791903720429
export AWS_ACCESS_KEY_ID=AKIA3QYJD2PWSE3B4K5B
export AWS_SECRET_ACCESS_KEY=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
export AWS_DEFAULT_REGION=us-east-1
```
3. Run `init-infra.sh`:
```bash
./init-infra.sh
```
4. Grab a cup of coffee and relax for 30 minutes :)

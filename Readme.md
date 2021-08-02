# Initializing infrastructure in a new clean AWS account

1. cd `root_dir_of_the_repo`
2. Add environment variables to the file `.envrc.private` (the values are just an example):
```bash
export TF_VAR_aws_account_id=241284480095
export AWS_ACCOUNT_ID=241284480095
export AWS_ACCESS_KEY_ID=AKIATQLNM7RPS6J6N6PO
export AWS_SECRET_ACCESS_KEY=rf2ro0M1N1jK2fERRQKahFMrt6SoatDYS0Q2WGug
```
3. Run `DO_ALL.SH`:
```bash
./DO_ALL.SH
```
4. Grab a cup of coffee and relax for 40-50 minutes :)


# Local development

1. Open a service directory as a project (for example, images/auth-api).
2. Wait for PyCharm to install packages from Pipfile.lock.
3. Add/edit environment variables in .envrc
4. Proxy other services from k8s
Documentation: https://kubernetes.io/docs/tasks/access-application-cluster/port-forward-access-application-cluster/

kubectl port-forward service/<service-name> <local_port>:<service_port>
kubectl port-forward service/admin-panel 12345:80

5. Proxy AWS services via SSH using Bastion Host

RDS Postgres:
ssh -i terraform/infra/files/bastion-ssh-keys/bastion_ssh_key -L 5432:postgres.cqdoof7q4aet.us-east-1.rds.amazonaws.com:5432 -N ubuntu@52.91.51.189

Elastcache Redis:
ssh -i terraform/infra/files/bastion-ssh-keys/bastion_ssh_key -L 6379:redis-cluster-repl-group.wwpkm1.ng.0001.use1.cache.amazonaws.com:6379 -N ubuntu@52.91.51.189


# Deploying to AWS

1. Building new images
`./build-all-images.sh`


2. Deploying new images to k8s
`./deploy-all-to-k8s.sh`


3. Checking PODs statuses:
`kubectl get pods`

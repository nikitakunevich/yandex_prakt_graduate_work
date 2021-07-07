data "aws_ami" "eks-worker" {
  filter {
    name   = "name"
    values = ["amazon-eks-node-${aws_eks_cluster.movies.version}-v*"]
  }

  most_recent = true
  owners      = ["602401143452"] # Amazon EKS AMI Account ID
}

# This data source is included for ease of sample architecture deployment
# and can be swapped out as necessary.
data "aws_region" "current" {}

# EKS currently documents this required userdata for EKS worker nodes to
# properly configure Kubernetes applications on the EC2 instance.
# We utilize a Terraform local here to simplify Base64 encoding this
# information into the AutoScaling Launch Configuration.
# More information: https://docs.aws.amazon.com/eks/latest/userguide/launch-workers.html
locals {
  movies-node-userdata = <<USERDATA
#!/bin/bash
set -o xtrace
echo "oracle" | passwd --stdin ec2-user
/etc/eks/bootstrap.sh --apiserver-endpoint '${aws_eks_cluster.movies.endpoint}' --b64-cluster-ca '${aws_eks_cluster.movies.certificate_authority.0.data}' '${var.cluster-name}'
USERDATA
}

resource "aws_launch_configuration" "movies-node" {
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.movies-node.name
  image_id                    = data.aws_ami.eks-worker.id
  instance_type               = "t3.medium"
  name_prefix                 = "eks-movies"
  security_groups             = [aws_security_group.movies-node.id]
  user_data_base64            = base64encode(local.movies-node-userdata)

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_group" "movies-nodes" {
  desired_capacity     = 2
  launch_configuration = aws_launch_configuration.movies-node.id
  max_size             = 2
  min_size             = 1
  name                 = "terraform-eks-movies"
  vpc_zone_identifier  = tolist(aws_subnet.eks.*.id)

  tag {
    key                 = "Name"
    value               = "terraform-eks-movies"
    propagate_at_launch = true
  }

  tag {
    key                 = "kubernetes.io/cluster/${var.cluster-name}"
    value               = "owned"
    propagate_at_launch = true
  }
}
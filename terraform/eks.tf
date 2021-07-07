resource "aws_eks_cluster" "movies" {
  name     = var.cluster-name
  role_arn = aws_iam_role.movies-cluster.arn
  version  = "1.18"

  vpc_config {
    security_group_ids = [aws_security_group.movies-cluster.id]
    subnet_ids         = tolist(aws_subnet.eks.*.id)
  }

  depends_on = [
    aws_iam_role_policy_attachment.movies-cluster-AmazonEKSClusterPolicy,
    aws_iam_role_policy_attachment.movies-cluster-AmazonEKSServicePolicy,
  ]
}


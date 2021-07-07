################################################
# EKS master nodes security groups             #
################################################

resource "aws_security_group" "movies-cluster" {
  name        = "terraform-eks-movies-cluster"
  description = "Cluster communication with worker nodes"
  vpc_id      = aws_vpc.vpc.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "terraform-eks-movies"
  }
}

# OPTIONAL: Allow inbound traffic from your local workstation external IP
#           to the Kubernetes. You will need to replace A.B.C.D below with
#           your real IP. Services like icanhazip.com can help you find this.
resource "aws_security_group_rule" "demo-cluster-ingress-workstation-https" {
  cidr_blocks       = ["92.46.0.84/32"]
  description       = "Allow workstations to communicate with the cluster API Server"
  from_port         = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.movies-cluster.id
  to_port           = 443
  type              = "ingress"
}

resource "aws_security_group_rule" "movies-cluster-ingress-self" {
  description              = "Allow node to communicate with each other"
  from_port                = 0
  protocol                 = "-1"
  security_group_id        = aws_security_group.movies-cluster.id
  source_security_group_id = aws_security_group.movies-cluster.id
  to_port                  = 65535
  type                     = "ingress"
}

################################################
# EKS worker nodes security groups             #
################################################

resource "aws_security_group" "movies-node" {
  name        = "terraform-eks-demo-node"
  description = "Security group for all nodes in the cluster"
  vpc_id      = aws_vpc.vpc.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = map(
    "Name", "terraform-eks-demo-node",
    "kubernetes.io/cluster/${var.cluster-name}", "owned",
  )
}

resource "aws_security_group_rule" "movies-node-ingress-self" {
  description              = "Allow node to communicate with each other"
  from_port                = 0
  protocol                 = "-1"
  security_group_id        = aws_security_group.movies-node.id
  source_security_group_id = aws_security_group.movies-node.id
  to_port                  = 65535
  type                     = "ingress"
}

resource "aws_security_group_rule" "movies-node-ingress-from-cluster" {
  description              = "Allow worker Kubelets and pods to receive communication from the cluster control plane"
  from_port                = 0
  protocol                 = "-1"
  security_group_id        = aws_security_group.movies-node.id
  source_security_group_id = aws_security_group.movies-cluster.id
  to_port                  = 0
  type                     = "ingress"
}

resource "aws_security_group_rule" "movies-cluster-ingress-from-nodes" {
  description              = "Allow worker Kubelets and pods to receive communication from the cluster control plane"
  from_port                = 0
  protocol                 = "-1"
  security_group_id        = aws_security_group.movies-cluster.id
  source_security_group_id = aws_security_group.movies-node.id
  to_port                  = 0
  type                     = "ingress"
}

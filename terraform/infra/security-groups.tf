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
  name        = "terraform-eks-movies-node"
  description = "Security group for all nodes in the cluster"
  vpc_id      = aws_vpc.vpc.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = map(
    "Name", "terraform-eks-movies-node",
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

resource "aws_security_group_rule" "movies-node-ingress-from-alb" {
  description              = "Allow worker Kubelets and pods to receive communication from ALBs"
  from_port                = 0
  protocol                 = "-1"
  security_group_id        = aws_security_group.movies-node.id
  source_security_group_id = aws_security_group.ingress-alb.id
  to_port                  = 0
  type                     = "ingress"
}

##########################
# SG for ingress         #
##########################

resource "aws_security_group" "ingress-alb" {
  name        = "ingress-alb"
  description = "Security group for ingress ALBs"
  vpc_id      = aws_vpc.vpc.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

############################
# SG for bastion           #
############################

resource "aws_security_group" "bastion" {
  name        = "bastion-sg"
  description = "Security group for Bastion"
  vpc_id      = aws_vpc.vpc.id
}

resource "aws_security_group_rule" "bastion-es-from-k8s-nodes" {
  description              = "Allow EKS nodes to connect to Elasticsearch on Bastion"
  from_port                = 9200
  to_port                  = 9200
  protocol                 = "tcp"
  security_group_id        = aws_security_group.bastion.id
  source_security_group_id = aws_security_group.movies-node.id
  type                     = "ingress"
}

resource "aws_security_group_rule" "bastion-ingress" {
  description              = "Allow SSH to Bastion"
  from_port                = 22
  to_port                  = 22
  protocol                 = "tcp"
  security_group_id        = aws_security_group.bastion.id
  cidr_blocks              = ["0.0.0.0/0"]
  type                     = "ingress"
}

resource "aws_security_group_rule" "bastion-egress" {
  security_group_id        = aws_security_group.bastion.id
  description              = "Allow connections from Bastion"
  from_port                = 0
  to_port                  = 0
  protocol                 = "-1"
  cidr_blocks              = ["0.0.0.0/0"]
  type                     = "egress"
}

output "allow-all-ingress-tcp-alb-sg" {
  value = aws_security_group.ingress-alb.id
}
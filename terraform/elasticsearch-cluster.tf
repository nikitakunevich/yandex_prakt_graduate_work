# Disabled to not abuse acloudguru rules

/*
resource "aws_security_group" "elasticsearch-cluster" {
  name        = "elasticsearch-cluster"
  description = "elasticsearch-cluster"
  vpc_id      = aws_vpc.vpc.id

  ingress {
    from_port = 80
    to_port   = 80
    protocol  = "tcp"
    cidr_blocks = [
      aws_vpc.vpc.cidr_block
    ]
  }

  ingress {
    from_port = 443
    to_port   = 443
    protocol  = "tcp"
    cidr_blocks = [
      aws_vpc.vpc.cidr_block
    ]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_elasticsearch_domain" "elasticsearch-cluster" {
  domain_name           = "search"
  elasticsearch_version = "7.9"

  access_policies = jsonencode(
    {
      Statement = [
        {
          Action = "es:*"
          Effect = "Allow"
          Principal = {
            AWS = "*"
          }
          Resource = "arn:aws:es:us-east-1:${var.aws_account_id}:domain/search/*"
        },
      ]
      Version = "2012-10-17"
    }
  )

  advanced_options = {
    "rest.action.multi.allow_explicit_index" = "true"
  }

  cluster_config {
    dedicated_master_count   = 3
    dedicated_master_enabled = true
    dedicated_master_type    = "c5.large.elasticsearch"
    instance_count           = 1
    instance_type            = "m6g.large.elasticsearch"
    zone_awareness_enabled   = true

    zone_awareness_config {
      availability_zone_count = 2
    }
  }

  domain_endpoint_options {
    enforce_https                   = false
    custom_endpoint                 = "es.private.hi-tech4.cloud"
    custom_endpoint_enabled         = true
    custom_endpoint_certificate_arn = aws_acm_certificate.movies.arn
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 5
    volume_type = "gp2"
  }

  vpc_options {
    subnet_ids = [
      aws_subnet.private[0].id,
      aws_subnet.private[1].id
    ]
    security_group_ids = [aws_security_group.elasticsearch-cluster.id]
  }
}
*/
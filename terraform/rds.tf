resource "aws_security_group" "postgres" {
  name   = "rds"
  vpc_id = aws_vpc.vpc.id

  ingress {
    from_port = 5432
    to_port   = 5432
    protocol  = "tcp"
    security_groups = [
      aws_security_group.movies-node.id,
      aws_security_group.bastion.id
    ]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_subnet_group" "postgres" {
  name       = "db_subnet_group"
  subnet_ids = aws_subnet.private.*.id
}

resource "aws_db_instance" "postgres" {
  apply_immediately       = true
  identifier              = "postgres"
  instance_class          = "db.t3.micro"
  engine                  = "postgres"
  engine_version          = "12"
  allocated_storage       = 5
  copy_tags_to_snapshot   = true
  deletion_protection     = true
  skip_final_snapshot     = false
  username                = "postgres"
  password                = "postgres"
  db_subnet_group_name    = aws_db_subnet_group.postgres.id
  vpc_security_group_ids  = [aws_security_group.postgres.id]
  backup_retention_period = 1
}

output "rds_postgres_username" {
  value = aws_db_instance.postgres.username
}

output "rds_postgres_password" {
  value = aws_db_instance.postgres.password
}

output "rds_postgres_endpoint" {
  value = aws_db_instance.postgres.endpoint
}
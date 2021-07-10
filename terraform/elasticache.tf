resource "aws_elasticache_subnet_group" "redis" {
  name        = "redis"
  description = "Subnet group for elasticache redis clusters"
  subnet_ids  = aws_subnet.private.*.id
}

resource "aws_elasticache_parameter_group" "redis" {
  name        = "redis"
  description = "Parameter group for elasticache redis clusters"

  family = "redis6.x"

  parameter {
    name  = "maxmemory-policy"
    value = "noeviction"
  }
  parameter {
    name  = "notify-keyspace-events"
    value = "Ex"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "redis" {
  name        = "redis"
  description = "Security group for elasticache redis clusters"
  vpc_id      = aws_vpc.vpc.id

  ingress {
    from_port = 6379
    to_port   = 6379
    protocol  = "tcp"
    security_groups = [
      aws_security_group.movies-node.id,
      aws_security_group.bastion.id
    ]
  }
}

resource "aws_elasticache_replication_group" "redis" {
  replication_group_description = "Redis Cluster"
  replication_group_id          = "redis-cluster-repl-group"
  security_group_ids            = [aws_security_group.redis.id]
  availability_zones            = ["us-east-1a", "us-east-1b"]
  auto_minor_version_upgrade    = false
  automatic_failover_enabled    = true
  engine                        = "redis"
  node_type                     = "cache.t3.micro"
  number_cache_clusters         = 2
  parameter_group_name          = aws_elasticache_parameter_group.redis.name
  engine_version                = "6.x"
  port                          = 6379
  subnet_group_name             = aws_elasticache_subnet_group.redis.name
}


output "redis_endpoint" {
  value = aws_elasticache_replication_group.redis.primary_endpoint_address
}
resource "aws_route53_zone" "movies" {
  name = "movies.hi-tech4.cloud"
  vpc {
    vpc_id = aws_vpc.vpc.id
  }
}

resource "aws_route53_record" "cdn" {
  zone_id = aws_route53_zone.movies.zone_id
  name    = "cdn.${aws_route53_zone.movies.name}"
  type    = "CNAME"
  ttl     = "300"
  records = [aws_cloudfront_distribution.s3_distribution.domain_name]
}

resource "aws_route53_zone" "private" {
  name = "private.hi-tech4.cloud"
  vpc {
    vpc_id = aws_vpc.vpc.id
  }
}

output "nameservers" {
  value = aws_route53_zone.private.name_servers
}

resource "aws_route53_record" "postgres" {
  zone_id = aws_route53_zone.private.zone_id
  name    = "postgres.${aws_route53_zone.private.name}"
  type    = "CNAME"
  ttl     = "300"
  records = [aws_db_instance.postgres.address]
}

resource "aws_route53_record" "redis" {
  zone_id = aws_route53_zone.private.zone_id
  name    = "redis.${aws_route53_zone.private.name}"
  type    = "CNAME"
  ttl     = "300"
  records = [aws_elasticache_replication_group.redis.primary_endpoint_address]
}

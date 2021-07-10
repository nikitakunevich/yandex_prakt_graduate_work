resource "aws_acm_certificate" "movies" {
  domain_name       = "*.movies.hi-tech4.cloud"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}
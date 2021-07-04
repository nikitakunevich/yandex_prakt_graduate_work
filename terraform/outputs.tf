output "cloudfront-domain-name" {
  value = aws_cloudfront_distribution.s3_distribution.domain_name
}

output "cloudfront-key-id" {
  value = aws_cloudfront_public_key.movies-on-demand-api-key.id
}
locals {
  s3_origin_id = "Movies-S3-Origin"
}

resource "aws_cloudfront_public_key" "movies-on-demand-api-key" {
  comment     = "public key of Movies-on-Demand API microservice"
  encoded_key = file("files/cloudfront-keys/public_key.pem")
  name        = "movies-on-demand-api-key"
}

resource "aws_cloudfront_key_group" "public-keys-group" {
  items = [aws_cloudfront_public_key.movies-on-demand-api-key.id]
  name  = "public-keys-group"
}

resource "aws_cloudfront_origin_access_identity" "movies" {
  comment = "Identity for accessing movies in an S3 bucket"
}

resource "aws_cloudfront_distribution" "s3_distribution" {
  origin {
    domain_name = aws_s3_bucket.movies.bucket_regional_domain_name
    origin_id   = local.s3_origin_id

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.movies.cloudfront_access_identity_path
    }
  }

  enabled         = true
  is_ipv6_enabled = true
  comment         = "A distribution for providing video on demand"

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = local.s3_origin_id

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "https-only"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
    trusted_key_groups     = [aws_cloudfront_key_group.public-keys-group.id]
  }

  price_class = "PriceClass_200"

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = ["US", "CA", "GB", "DE", "RU", "KZ"]
    }
  }

  tags = {
    Environment = "production"
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}




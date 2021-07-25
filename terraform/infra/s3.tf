resource "aws_s3_bucket" "movies" {
  bucket = "movies-${var.aws_account_id}"
  acl    = "private"
  tags = {
    Name = "Movies bucket"
  }
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_public_access_block" "movies" {
  bucket = aws_s3_bucket.movies.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "movies-policy" {
  bucket = aws_s3_bucket.movies.id

  policy = jsonencode({
    Version = "2012-10-17"
    Id      = "movies-policy"
    Statement = [
      {
        Sid       = "AllowCloudfrontRead"
        Effect    = "Allow"
        Principal = { "AWS" : aws_cloudfront_origin_access_identity.movies.iam_arn }
        Action    = ["s3:GetObject", "s3:GetObjectVersion"]
        Resource = [
          "${aws_s3_bucket.movies.arn}/assets/*",
        ]
      },
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.movies]
}

output "movies_bucket_name" {
  value = aws_s3_bucket.movies.bucket
}
variable "aws_account_id" {
  type        = number
  description = "ID of the AWS account in a number format. Example: 093310752320"
}

variable "cluster-name" {
  default     = "movies-eks"
  type        = string
  description = "Name of the EKS cluster."
}

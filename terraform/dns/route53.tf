data "aws_route53_zone" "hi-tech4-cloud" {
  name = "hi-tech4.cloud"
}

resource "aws_route53_record" "movies" {
  zone_id = data.aws_route53_zone.hi-tech4-cloud.id
  name    = "movies.hi-tech4.cloud"
  type    = "NS"
  ttl     = "60"
  records = data.terraform_remote_state.infra.outputs.movies-name-servers
}

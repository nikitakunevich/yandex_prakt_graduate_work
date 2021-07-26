resource "kubernetes_deployment" "movies-on-demand-api" {
  metadata {
    name = "movies-on-demand-api"
    labels = {
      app = "movies-on-demand-api"
    }
  }

  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "movies-on-demand-api"
      }
    }
    template {
      metadata {
        labels = {
          app = "movies-on-demand-api"
        }
      }
      spec {
        container {
          image = "${data.terraform_remote_state.infra.outputs.movies-on-demand-api-ecr-url}:latest"
          name  = "movies-on-demand-api"

          port {
            name           = "http"
            container_port = 8000
          }

          liveness_probe {
            http_get {
              path = "/health-check"
              port = "http"
            }
            initial_delay_seconds = 5
            failure_threshold     = 3
            period_seconds        = 60
          }

          readiness_probe {
            http_get {
              path = "/health-check"
              port = "http"
            }
            initial_delay_seconds = 5
            failure_threshold     = 3
            period_seconds        = 60
          }

          env {
            name  = "FLASK_CONFIG"
            value = "production"
          }

          env {
            name  = "REDIS_HOST"
            value = data.terraform_remote_state.infra.outputs.redis_endpoint
          }

          env {
            name  = "LOG_LEVEL"
            value = "INFO"
          }

          env {
            name  = "CF_KEY_ID"
            value = data.terraform_remote_state.infra.outputs.cloudfront-key-id
          }

          env {
            name  = "CF_DOMAIN_NAME"
            value = data.terraform_remote_state.infra.outputs.cloudfront-domain-name
          }

          env {
            name  = "CF_PRIVATE_KEY_FILE"
            value = "private_key.pem"
          }

          env {
            name  = "URL_PATH_PREFIX"
            value = "assets/movies"
          }

          env {
            name  = "URL_EXPIRE_HOURS"
            value = "8"
          }

          env {
            name  = "AUTH_PUBLIC_KEY"
            value = file("jwt-keys/rs256.pub")
          }

          env {
            name  = "SEARCH_API_HOST"
            value = "search-api"
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "movies-on-demand-api" {
  metadata {
    name = "movies-on-demand-api"
    labels = {
      app = "movies-on-demand-api"
    }
    annotations = {
      "prometheus.io/scrape" = "true"
    }
  }

  spec {
    type = "NodePort"
    selector = {
      "app" = "movies-on-demand-api"
    }
    port {
      port        = 80
      name        = "http"
      target_port = "http"
    }
  }
}

resource "kubernetes_ingress" "movies-on-demand-api" {
  metadata {
    name = "movies-on-demand-api"
    annotations = {
      "kubernetes.io/ingress.class"                            = "alb"
      "alb.ingress.kubernetes.io/scheme"                       = "internet-facing"
      "alb.ingress.kubernetes.io/security-groups"              = data.terraform_remote_state.infra.outputs.allow-all-ingress-tcp-alb-sg
      "alb.ingress.kubernetes.io/certificate-arn"              = data.terraform_remote_state.infra.outputs.acm-certificate-arn
      "alb.ingress.kubernetes.io/healthcheck-interval-seconds" = "60"
      "alb.ingress.kubernetes.io/healthcheck-path"             = "/health-check"
    }
  }

  spec {
    rule {
      http {
        path {
          backend {
            service_name = "movies-on-demand-api"
            service_port = "http"
          }
        }
      }
      host = "movies-on-demand-api.movies.hi-tech4.cloud"
    }
  }
}

data "kubernetes_ingress" "movies-on-demand-api" {
  depends_on = [kubernetes_ingress.movies-on-demand-api]
  metadata {
    name = "movies-on-demand-api"
  }
}

resource "aws_route53_record" "movies-on-demand-api" {
  zone_id = data.terraform_remote_state.infra.outputs.movies_zone.zone_id
  name    = "movies-on-demand-api.${data.terraform_remote_state.infra.outputs.movies_zone.name}"
  type    = "CNAME"
  ttl     = "300"
  records = [data.kubernetes_ingress.movies-on-demand-api.status.0.load_balancer.0.ingress.0.hostname]
}
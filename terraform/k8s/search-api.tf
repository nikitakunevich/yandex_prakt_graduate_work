resource "kubernetes_deployment" "search-api" {
  metadata {
    name = "search-api"
    labels = {
      app = "search-api"
    }
  }

  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "search-api"
      }
    }
    template {
      metadata {
        labels = {
          app = "search-api"
        }
      }
      spec {
        container {
          image = "${data.terraform_remote_state.infra.outputs.search-api-ecr-url}:latest"
          name  = "search-api"

          port {
            name           = "http"
            container_port = 8888
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
            name  = "REDIS_HOST"
            value = data.terraform_remote_state.infra.outputs.redis_endpoint
          }

          env {
            name  = "REDIS_PORT"
            value = "6379"
          }


          env {
            name  = "JWT_PUBLIC_KEY"
            value = file("jwt-keys/rs256.pub")
          }

          env {
            name  = "ES_URL"
            value = "http://${data.terraform_remote_state.infra.outputs.bastion-private-ip}:9200"
          }

          env {
            name  = "LOG_LEVEL"
            value = "WARNING"
          }

          env {
            name  = "CACHE_TTL"
            value = "300"
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "search-api" {
  metadata {
    name = "search-api"
    labels = {
      app = "search-api"
    }
    annotations = {
      "prometheus.io/scrape" = "true"
    }
  }

  spec {
    type = "NodePort"
    selector = {
      "app" = "search-api"
    }
    port {
      port        = 80
      name        = "http"
      target_port = "http"
    }
  }
}

resource "kubernetes_ingress" "search-api" {
  metadata {
    name = "search-api"
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
            service_name = "search-api"
            service_port = "http"
          }
        }
      }
      host = "search-api.movies.hi-tech4.cloud"
    }
  }
}

data "kubernetes_ingress" "search-api" {
  depends_on = [kubernetes_ingress.search-api]
  metadata {
    name = "search-api"
  }
}

resource "aws_route53_record" "search-api" {
  zone_id = data.terraform_remote_state.infra.outputs.movies_zone.zone_id
  name    = "search-api.${data.terraform_remote_state.infra.outputs.movies_zone.name}"
  type    = "CNAME"
  ttl     = "300"
  records = [data.kubernetes_ingress.search-api.status.0.load_balancer.0.ingress.0.hostname]
}
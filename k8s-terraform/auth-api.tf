resource "kubernetes_deployment" "auth-api" {
  metadata {
    name = "auth-api"
    labels = {
      app = "auth-api"
    }
  }

  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "auth-api"
      }
    }
    template {
      metadata {
        labels = {
          app = "auth-api"
        }
      }
      spec {
        container {
          image = "${data.terraform_remote_state.infra.outputs.auth-api-ecr-url}:latest"
          name  = "auth-api"

          port {
            name           = "http"
            container_port = 5000
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
            name  = "REDIS_PORT"
            value = "6379"
          }

          env {
            name  = "DATABASE_URL"
            value = "postgresql://postgres:postgres@${data.terraform_remote_state.infra.outputs.rds_postgres_endpoint}/postgres"
          }

          env {
            name  = "JWT_ACCESS_TOKEN_EXPIRES_MINUTES"
            value = "5"
          }

          env {
            name  = "JWT_REFRESH_TOKEN_EXPIRES_DAYS"
            value = "30"
          }

          env {
            name  = "SECRET_KEY"
            value = "idV9z8SuRFrT04e71IeCgXuttG6kXfB7"
          }

          env {
            name  = "GOOGLE_CLIENT_SECRET"
            value = "nr618YYu7FRDKYKAxCIMKwNr"
          }

          env {
            name  = "GOOGLE_RECAPTCHA_SECRET_KEY"
            value = "6Lf7B8MaAAAAAL8dszNdSp82jF2K-W0hOl8JIa-_"
          }

          env {
            name  = "ROOT_PASSWORD"
            value = "root123456"
          }

          env {
            name  = "ROOT_SESSION_HOURS"
            value = "2"
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "auth-api" {
  metadata {
    name = "auth-api"
    labels = {
      app = "auth-api"
    }
    annotations = {
      "prometheus.io/scrape" = "true"
    }
  }

  spec {
    type = "NodePort"
    selector = {
      "app" = "auth-api"
    }
    port {
      port        = 80
      name        = "http"
      target_port = "http"
    }
  }
}

resource "kubernetes_ingress" "auth-api" {
  metadata {
    name = "auth-api"
    annotations = {
      "kubernetes.io/ingress.class"                            = "alb"
      "alb.ingress.kubernetes.io/scheme"                       = "internet-facing"
      "alb.ingress.kubernetes.io/security-groups"              = data.terraform_remote_state.infra.outputs.allow-all-ingress-tcp-alb-sg
      #"alb.ingress.kubernetes.io/certificate-arn"              = data.terraform_remote_state.infra.outputs.acm-certificate-arn
      "alb.ingress.kubernetes.io/healthcheck-interval-seconds" = "60"
      "alb.ingress.kubernetes.io/healthcheck-path"             = "/health-check"
    }
  }

  spec {
    rule {
      http {
        path {
          backend {
            service_name = "auth-api"
            service_port = "http"
          }
        }
      }
      host = "auth-api.movies.hi-tech4.cloud"
    }
  }
}

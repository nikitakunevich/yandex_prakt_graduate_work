resource "kubernetes_deployment" "admin-panel" {
  metadata {
    name = "admin-panel"
    labels = {
      app = "admin-panel"
    }
  }

  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "admin-panel"
      }
    }
    template {
      metadata {
        labels = {
          app = "admin-panel"
        }
      }
      spec {
        container {
          image = "${data.terraform_remote_state.infra.outputs.admin-panel-ecr-url}:latest"
          name  = "admin-panel"

          env {
            name  = "AWS_STORAGE_BUCKET_NAME"
            value = data.terraform_remote_state.infra.outputs.movies_bucket_name
          }

          env {
            name  = "PG_USER"
            value = "postgres"
          }

          env {
            name  = "PG_PASS"
            value = "postgres"
          }

          env {
            name  = "PG_DB"
            value = "postgres"
          }

          env {
            name  = "PG_HOST"
            value = data.terraform_remote_state.infra.outputs.rds_postgres_hostname
          }

          env {
            name  = "SECRET_KEY"
            value = "LBSmYVU0NdF-RKdm54IWjqW0TaXGK-8vL8weRwu4cxk"
          }

          env {
            name  = "STATIC_ROOT"
            value = "/static"
          }

          env {
            name  = "LOG_LEVEL"
            value = "DEBUG"
          }

          env {
            name  = "SECRET_KEY"
            value = "idV9z8SuRFrT04e71IeCgXuttG6kXfB7"
          }

          env {
            name  = "ADMIN_USER"
            value = "admin"
          }

          env {
            name  = "ADMIN_PASS"
            value = "admin"
          }

          env {
            name  = "DJANGO_SETTINGS_MODULE"
            value = "config.settings.prod"
          }

          env {
            name  = "DEBUG"
            value = "True"
          }

          volume_mount {
            mount_path = "/static"
            name = "static"
          }
        }

        container {
          name  = "nginx"
          image = "nginx:1.19.2"

          port {
            name           = "http"
            container_port = 8080
          }

          volume_mount {
            mount_path = "/etc/nginx/nginx.conf"
            name = "nginx"
            sub_path = "nginx.conf"
          }

          volume_mount {
            mount_path = "/etc/nginx/conf.d/movie_admin.conf"
            name = "nginx-proxy"
            sub_path = "movie_admin.conf"
          }

          volume_mount {
            mount_path = "/static"
            name = "static"
          }
        }

        volume {
          name = "nginx"
          config_map {
            name = "admin-panel-nginx"
          }
        }

        volume {
          name = "nginx-proxy"
          config_map {
            name = "admin-panel-nginx-proxy"
          }
        }

        volume {
          name = "static"
          empty_dir {}
        }
      }
    }
  }
}

resource "kubernetes_service" "admin-panel" {
  metadata {
    name = "admin-panel"
    labels = {
      app = "admin-panel"
    }
    annotations = {
      "prometheus.io/scrape" = "true"
    }
  }

  spec {
    type = "NodePort"
    selector = {
      "app" = "admin-panel"
    }
    port {
      port        = 80
      name        = "http"
      target_port = "http"
    }
  }
}

resource "kubernetes_ingress" "admin-panel" {
  metadata {
    name = "admin-panel"
    annotations = {
      "kubernetes.io/ingress.class"                            = "alb"
      "alb.ingress.kubernetes.io/scheme"                       = "internal"
      "alb.ingress.kubernetes.io/security-groups"              = data.terraform_remote_state.infra.outputs.allow-all-ingress-tcp-alb-sg
      "alb.ingress.kubernetes.io/healthcheck-interval-seconds" = "60"
      "alb.ingress.kubernetes.io/healthcheck-path"             = "/admin"
    }
  }

  spec {
    rule {
      http {
        path {
          backend {
            service_name = "admin-panel"
            service_port = "http"
          }
        }
      }
      host = "admin-panel.private.hi-tech4.cloud"
    }
  }
}

resource "kubernetes_config_map" "admin-panel-nginx" {
  metadata {
    name = "admin-panel-nginx"
  }

  data = {
    "nginx.conf" = file("files/nginx/nginx.conf")
  }
}

resource "kubernetes_config_map" "admin-panel-nginx-proxy" {
  metadata {
    name = "admin-panel-nginx-proxy"
  }

  data = {
    "movie_admin.conf" = file("files/nginx/movie_admin.conf")
  }
}
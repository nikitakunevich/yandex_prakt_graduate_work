resource "kubernetes_deployment" "postgres-to-es" {
  metadata {
    name = "postgres-to-es"
    labels = {
      app = "postgres-to-es"
    }
  }

  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "postgres-to-es"
      }
    }
    template {
      metadata {
        labels = {
          app = "postgres-to-es"
        }
      }
      spec {
        container {
          image = "${data.terraform_remote_state.infra.outputs.postgres-to-es-ecr-url}:latest"
          name  = "postgres-to-es"

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
            name  = "PG_URL"
            value = "postgresql://postgres:postgres@${data.terraform_remote_state.infra.outputs.rds_postgres_hostname}/postgres"
          }

          env {
            name  = "ES_URL"
            value = "http://${data.terraform_remote_state.infra.outputs.bastion-private-ip}:9200"
          }

          env {
            name  = "REDIS_HOST"
            value = data.terraform_remote_state.infra.outputs.redis_endpoint
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
        }
      }
    }
  }
}

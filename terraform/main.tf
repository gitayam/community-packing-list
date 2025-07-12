# Cloud-Native Infrastructure for Community Packing List
# This Terraform configuration sets up a fully serverless, cloud-native deployment

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

# Variables
variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud Region"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "community-packing-list"
}

# Provider configuration
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "cloudbuild.googleapis.com",
    "cloudrun.googleapis.com",
    "sqladmin.googleapis.com",
    "storage.googleapis.com",
    "secretmanager.googleapis.com",
    "compute.googleapis.com",
    "servicenetworking.googleapis.com",
    "vpcaccess.googleapis.com"
  ])
  
  service            = each.value
  disable_on_destroy = false
}

# Cloud SQL Database
resource "google_sql_database_instance" "postgres" {
  name             = "${var.service_name}-db"
  database_version = "POSTGRES_15"
  region           = var.region
  
  settings {
    tier                        = "db-f1-micro"
    availability_type           = "ZONAL"
    disk_type                   = "PD_SSD"
    disk_size                   = 10
    disk_autoresize             = true
    disk_autoresize_limit       = 100
    
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 7
      }
    }
    
    maintenance_window {
      day         = 7  # Sunday
      hour        = 4
      update_track = "stable"
    }
    
    ip_configuration {
      ipv4_enabled = false
      private_network = google_compute_network.vpc.id
    }
    
    database_flags {
      name  = "cloudsql.iam_authentication"
      value = "on"
    }
  }
  
  deletion_protection = false
  depends_on = [google_project_service.apis]
}

resource "google_sql_database" "database" {
  name     = "packinglist_prod"
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "user" {
  name     = "packinglist_user"
  instance = google_sql_database_instance.postgres.name
  password = random_password.db_password.result
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

# VPC Network for private services
resource "google_compute_network" "vpc" {
  name                    = "${var.service_name}-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "${var.service_name}-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
}

# Private IP allocation for Cloud SQL
resource "google_compute_global_address" "private_ip_address" {
  name          = "${var.service_name}-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

# VPC Access Connector for Cloud Run
resource "google_vpc_access_connector" "connector" {
  provider = google-beta
  name     = "${var.service_name}-connector"
  region   = var.region
  subnet {
    name = google_compute_subnetwork.subnet.name
  }
  machine_type   = "e2-micro"
  min_instances  = 2
  max_instances  = 3
}

# Cloud Storage Buckets
resource "google_storage_bucket" "static_bucket" {
  name          = "${var.project_id}-static"
  location      = var.region
  force_destroy = true
  
  uniform_bucket_level_access = true
  
  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_storage_bucket" "media_bucket" {
  name          = "${var.project_id}-media"
  location      = var.region
  force_destroy = true
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
}

# Make buckets publicly readable
resource "google_storage_bucket_iam_member" "static_bucket_public" {
  bucket = google_storage_bucket.static_bucket.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

resource "google_storage_bucket_iam_member" "media_bucket_public" {
  bucket = google_storage_bucket.media_bucket.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

# Secret Manager Secrets
resource "google_secret_manager_secret" "django_secret_key" {
  secret_id = "django-secret-key"
  
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "django_secret_key" {
  secret      = google_secret_manager_secret.django_secret_key.id
  secret_data = random_password.django_secret.result
}

resource "random_password" "django_secret" {
  length  = 64
  special = true
}

resource "google_secret_manager_secret" "database_url" {
  secret_id = "database-url"
  
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "database_url" {
  secret      = google_secret_manager_secret.database_url.id
  secret_data = "postgresql://${google_sql_user.user.name}:${google_sql_user.user.password}@//cloudsql/${google_sql_database_instance.postgres.connection_name}/${google_sql_database.database.name}"
}

# Service Account for Cloud Run
resource "google_service_account" "cloud_run_sa" {
  account_id   = "${var.service_name}-sa"
  display_name = "Cloud Run Service Account"
  description  = "Service account for Cloud Run service"
}

# IAM permissions for the service account
resource "google_project_iam_member" "cloud_run_sa_permissions" {
  for_each = toset([
    "roles/cloudsql.client",
    "roles/secretmanager.secretAccessor",
    "roles/storage.objectAdmin"
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Cloud Run Service
resource "google_cloud_run_service" "service" {
  name     = var.service_name
  location = var.region
  
  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"                     = "0"
        "autoscaling.knative.dev/maxScale"                     = "100"
        "run.googleapis.com/cloudsql-instances"                = google_sql_database_instance.postgres.connection_name
        "run.googleapis.com/vpc-access-connector"              = google_vpc_access_connector.connector.name
        "run.googleapis.com/execution-environment"             = "gen2"
        "run.googleapis.com/cpu-throttling"                    = "false"
      }
    }
    
    spec {
      service_account_name = google_service_account.cloud_run_sa.email
      timeout_seconds      = 300
      container_concurrency = 80
      
      containers {
        image = "gcr.io/${var.project_id}/${var.service_name}:latest"
        
        ports {
          container_port = 8080
        }
        
        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }
        
        env {
          name  = "ENVIRONMENT"
          value = "production"
        }
        
        env {
          name  = "USE_GCS"
          value = "true"
        }
        
        env {
          name  = "GS_BUCKET_NAME"
          value = google_storage_bucket.static_bucket.name
        }
        
        env {
          name  = "GS_MEDIA_BUCKET_NAME"
          value = google_storage_bucket.media_bucket.name
        }
        
        resources {
          limits = {
            memory = "1Gi"
            cpu    = "1000m"
          }
          requests = {
            memory = "512Mi"
            cpu    = "500m"
          }
        }
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [google_project_service.apis]
}

# Allow unauthenticated access
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.service.name
  location = google_cloud_run_service.service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Outputs
output "service_url" {
  description = "URL of the Cloud Run service"
  value       = google_cloud_run_service.service.status[0].url
}

output "database_connection_name" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.postgres.connection_name
}

output "static_bucket_name" {
  description = "Name of the static files bucket"
  value       = google_storage_bucket.static_bucket.name
}

output "media_bucket_name" {
  description = "Name of the media files bucket"
  value       = google_storage_bucket.media_bucket.name
} 
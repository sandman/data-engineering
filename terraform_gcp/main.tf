terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.51.0"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
  // credentials = file(var.credentials)  # Use this if you do not want to set env-var GOOGLE_APPLICATION_CREDENTIALS
}

resource "google_compute_instance" "default" {
  name = "test"
  #Type of instance. Maybe make it a variable in variables.tf
  machine_type = "e2-micro"
  zone         = var.zone

  boot_disk {
    initialize_params {
      #OS to use
      image = "ubuntu-os-cloud/ubuntu-minimal-2204-lts"
      #Disk size in Gb
      size = "15"
    }
  }

  metadata = {
    #User name and path to public SSH Key
    ssh-keys = "sandip:${file("~/.ssh/gcp_rsa.pub")}"
  }

  network_interface {
    #Use the default GCP VPC Network
    network = "default"
    #Give VM an Ephemeral External IP
    access_config {}
  }

}

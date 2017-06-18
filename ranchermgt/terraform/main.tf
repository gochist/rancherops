variable "triton_account" {}
variable "triton_key_id" {}
variable "triton_url" {}
variable "rancherops_ansible_inventory" {}

provider "triton" {
  account = "${var.triton_account}"
  key_id  = "${var.triton_key_id}"
  url = "${var.triton_url}"
}

resource "triton_machine" "ranchermgt1" {
  name    = "ranchermgt1.stg.jpc"
  package = "k4-highcpu-kvm-250M"
  image   = "554abb2e-a957-4b51-a601-97c934eadf33" // ubuntu certified 16.04

  tags = {
    rancherops_managed = "true"
    rancherops_ansible_inventory = "${var.rancherops_ansible_inventory}"
    rancherops_ansible_server_groups = "rancher-db,rancher-server"
    rancherops_ansible_host_names = "ntp-server,internal-registry"
  }
}

resource "triton_machine" "ranchermgt2" {
  name    = "ranchermgt2.stg.jpc"
  package = "k4-highcpu-kvm-250M"
  image   = "554abb2e-a957-4b51-a601-97c934eadf33" // ubuntu certified 16.04

  tags = {
    rancherops_managed = "true"
    rancherops_ansible_inventory = "${var.rancherops_ansible_inventory}"
    rancherops_ansible_server_groups = "rancher-db,rancher-server"
  }
}

provider "triton" {
  account = "account"
  key_id  = "de:ad:be:ef:de:ad:be:ef:de:ad:be:ef:de:ad:be:ef"
  url = "https://us-east-1.api.joyentcloud.com"
}

resource "triton_machine" "ranchermgt1" {
  name    = "ranchermgt1.stg.jpc"
  package = "k4-highcpu-kvm-250M"
  image   = "554abb2e-a957-4b51-a601-97c934eadf33" // ubuntu certified 16.04

  tags = {
    rancherops_managed = "true"
    ansible_inventory = "jpc-stg"
    ansible_server_groups = "rancher-db,rancher-server"
    ansible_host_names = "ntp-server,internal-registry"
  }
}

resource "triton_machine" "ranchermgt2" {
  name    = "ranchermgt2.stg.jpc"
  package = "k4-highcpu-kvm-250M"
  image   = "554abb2e-a957-4b51-a601-97c934eadf33" // ubuntu certified 16.04

  tags = {
    rancherops_managed = "true"
    ansible_inventory = "jpc-stg"
    ansible_server_groups = "rancher-db,rancher-server"
  }
}

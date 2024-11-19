
provider "azurerm" {
  features {}
  resource_provider_registrations = "none"
}

# Reference existing resource group
data "azurerm_resource_group" "main" {
  name = "ICAAM"
}

# Reference existing storage account
data "azurerm_storage_account" "main" {
  name                = "icaamimage"
  resource_group_name = data.azurerm_resource_group.main.name
}

# Reference existing file share
data "azurerm_storage_share" "uploads" {
  name                 = "models-registry"
  storage_account_name = data.azurerm_storage_account.main.name
}


# Container group
resource "azurerm_container_group" "main" {
  name                = "backend-containers"
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name
  ip_address_type     = "Public"
  dns_name_label      = var.dns_name_label
  os_type             = "Linux"


  image_registry_credential {
    server   = "ghcr.io"
    username = var.registry_username
    password = var.registry_password # This should be your GitHub PAT
  }

  container {
    name   = "python-backend"
    image  = var.python_backend_image
    cpu    = "1"
    memory = "1.5"

    ports {
      port     = 8000
      protocol = "TCP"
    }

    environment_variables = {
      "ENV" = "AZURE"
    }

    secure_environment_variables = {
      "BLOB_STORAGE_CONNECTION_STRING" = var.storage_connection_string
    }

    volume {
      name                 = "models-registry"
      mount_path           = "/app/ml/models_registry"
      storage_account_name = data.azurerm_storage_account.main.name
      storage_account_key  = var.storage_account_key
      share_name           = data.azurerm_storage_share.uploads.name
    }
  }

  container {
    name   = "go-backend"
    image  = var.go_backend_image
    cpu    = "1"
    memory = "1.5"

    ports {
      port     = 4200
      protocol = "TCP"
    }

    environment_variables = {
      "ENV"                    = "AZURE"
      "PREDICTION_SERVICE_URL" = "http://localhost:8000"
    }

    secure_environment_variables = {
      "BLOB_STORAGE_CONNECTION_STRING" = var.storage_connection_string
    }

  }


  # Nginx sidecar container for TLS
  container {
    name   = "nginx-tls"
    image  = "mcr.microsoft.com/azurelinux/base/nginx:1.25"
    cpu    = "0.5"
    memory = "0.5"

    ports {
      port     = 443
      protocol = "TCP"
    }


    volume {
      name       = "nginx-config"
      mount_path = "/etc/nginx"

      secret = {
        "nginx.conf" = base64encode(file("${path.module}/nginx.conf"))
        "ssl.crt"    = base64encode(file("${path.module}/ssl.crt"))
        "ssl.key"    = base64encode(file("${path.module}/ssl.key"))
      }
    }

  }

  exposed_port {
    port     = 443
    protocol = "TCP"
  }

  exposed_port {
    port     = 8000
    protocol = "TCP"
  }

  exposed_port {
    port     = 4200
    protocol = "TCP"
  }

}


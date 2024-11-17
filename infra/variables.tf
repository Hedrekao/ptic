variable "python_backend_image" {
  description = "Python Backend container image"
  type        = string
}

variable "go_backend_image" {
  description = "GO Backend container image"
  type        = string
}

variable "storage_connection_string" {
  description = "Storage account connection string"
  type        = string
  sensitive   = true
}

variable "storage_account_key" {
  description = "Storage account key"
  type        = string
  sensitive   = true
}

variable "dns_name_label" {
  description = "DNS name label (must be globally unique)"
  type        = string
}

variable "registry_username" {
  description = "GitHub username"
  type        = string
}

variable "registry_password" {
  description = "GitHub Personal Access Token"
  type        = string
  sensitive   = true
}

# ──────────────────────────────────────────────────────────────
#  Terraform: infrastructure/terraform/main.tf
#  Responsibility: Azure infrastructure as code.
#
#  Resources to provision:
#    - Resource Group
#    - Azure App Service Plan + App Service (backend)
#    - Azure Static Web App (frontend)
#    - Azure Database for PostgreSQL Flexible Server
#    - Azure Cache for Redis
#    - Azure Storage Account + Containers (resumes, docs, certs)
#    - Azure OpenAI Service
#    - Azure Document Intelligence
#    - Azure Key Vault (for secrets)
#    - Azure Container Registry
#    - Application Insights + Log Analytics Workspace
# ──────────────────────────────────────────────────────────────

terraform {
  required_version = ">= 1.5"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }
  backend "azurerm" {
    # Configure via -backend-config or environment variables
    # resource_group_name  = "internflow-tfstate-rg"
    # storage_account_name = "internflowtfstate"
    # container_name       = "tfstate"
    # key                  = "internflow.tfstate"
  }
}

provider "azurerm" {
  features {}
}

# TODO: Implement resource blocks

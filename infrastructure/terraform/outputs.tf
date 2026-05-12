output "backend_app_url" {
  description = "Backend FastAPI App Service URL"
  value       = "https://${var.app_name}-backend-${var.environment}.azurewebsites.net"
}

output "frontend_url" {
  description = "Frontend Static Web App URL"
  value       = "https://${var.app_name}-${var.environment}.azurestaticapps.net"
}

output "postgres_fqdn" {
  description = "PostgreSQL Flexible Server FQDN"
  value       = "${var.app_name}-${var.environment}-pg.postgres.database.azure.com"
  sensitive   = false
}

output "acr_login_server" {
  description = "Azure Container Registry login server"
  value       = "${var.app_name}${var.environment}acr.azurecr.io"
}

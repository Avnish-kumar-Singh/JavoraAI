output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer."
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer."
  value       = aws_lb.main.zone_id
}

output "ecr_repository_url" {
  description = "ECR repository URL."
  value       = aws_ecr_repository.app.repository_url
}

output "database_endpoint" {
  description = "Connection endpoint for the PostgreSQL database."
  value       = aws_db_instance.main.address
}

output "health_check_url" {
  description = "Primary health check URL."
  value       = "http://${aws_lb.main.dns_name}/api/health"
}

output "ecs_security_group_id" {
  description = "Security group used by the ECS tasks - use this as the allowed source when opening port 11434 on your Ollama instance."
  value       = aws_security_group.ecs.id
}

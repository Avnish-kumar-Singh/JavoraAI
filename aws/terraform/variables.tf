variable "project_name" {
  description = "Project name used as a base for AWS resource naming."
  type        = string
  default     = "javora-ai"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region for the stack."
  type        = string
  default     = "us-east-1"
}

variable "container_image" {
  description = "Docker image stored in ECR or another registry."
  type        = string
  default     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/javora-ai:latest"
}

variable "app_port" {
  description = "Container port exposed by the FastAPI app."
  type        = number
  default     = 8000
}

variable "cpu" {
  description = "Fargate CPU units."
  type        = number
  default     = 512
}

variable "memory" {
  description = "Fargate memory in MiB."
  type        = number
  default     = 1024
}

variable "desired_count" {
  description = "Number of app tasks to run."
  type        = number
  default     = 1
}

variable "db_name" {
  description = "PostgreSQL database name."
  type        = string
  default     = "javoraai"
}

variable "db_username" {
  description = "PostgreSQL admin username."
  type        = string
  default     = "javora_admin"
}

variable "db_password" {
  description = "PostgreSQL admin password."
  type        = string
  sensitive   = true
  default     = "ChangeMe123!"
}

variable "jwt_secret" {
  description = "JWT signing secret for the application."
  type        = string
  sensitive   = true
  default     = "replace-with-secure-jwt-secret"
}

variable "llm_base_url" {
  description = "Base URL for the Ollama service used by the app."
  type        = string
  default     = "http://host.docker.internal:11434"
}

variable "cors_origins" {
  description = "CORS origins for the application."
  type        = string
  default     = "*"
}

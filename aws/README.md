# AWS deployment for JavaMentorAI

This directory contains a Terraform-based AWS deployment scaffold for the project.

## Components

- Amazon ECS Fargate for the app runtime
- Application Load Balancer for public ingress
- Amazon RDS for PostgreSQL
- Amazon ECR for the container image
- Amazon CloudWatch Logs for runtime logs
- Secrets Manager is referenced for runtime secrets

## Quick start

1. Change to the Terraform folder:
   ```bash
   cd aws/terraform
   ```
2. Copy the example variables file:
   ```bash
   copy terraform.tfvars.example terraform.tfvars
   ```
3. Update `terraform.tfvars` with your real values.
4. Initialize and apply:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```
5. After the stack is created, push the latest image to ECR and update the task definition or set the `container_image` value to the built image.

## Notes

- The current app expects `DATABASE_URL`, `JWT_SECRET`, and `OLLAMA_BASE_URL` to be configured in the runtime environment.
- The project defaults to SQLite locally, so the AWS deployment intentionally switches to PostgreSQL for production.
- Ollama must still be reachable from the app runtime. For a simple setup, keep a small Ollama service or a reachable private endpoint.

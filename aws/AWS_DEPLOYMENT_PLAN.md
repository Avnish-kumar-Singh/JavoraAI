# AWS deployment plan for JavaMentorAI

## Recommended architecture

- Amazon ECS Fargate: hosts the FastAPI app
- Amazon ECR: stores the container image
- Application Load Balancer: provides a public endpoint
- Amazon RDS PostgreSQL: replaces SQLite in production
- AWS Secrets Manager: stores `JWT_SECRET` and DB credentials
- Amazon CloudWatch Logs: collects container logs

## Why this matches the app

The repo already contains:

- a Dockerfile exposing port 8000
- a gunicorn entrypoint
- a FastAPI app with a health endpoint at `/api/health`
- environment-based config for database and JWT settings

That makes ECS Fargate the cleanest first production deployment target.

## Runtime configuration required

The app needs these environment variables in AWS:

- `DATABASE_URL`
- `JWT_SECRET`
- `OLLAMA_BASE_URL`
- `MODEL_NAME`
- `CORS_ORIGINS`
- `APP_ENV=production`

## Recommended deployment flow

1. Build and tag the Docker image.
2. Push to ECR.
3. Create or update the Terraform stack.
4. Verify the ALB endpoint responds on `/api/health`.
5. Run the app smoke test.

## Cost and scaling

For a small MVP, this is typically a low-cost setup:

- ECS Fargate: small CPU/memory tasks
- RDS db.t3.micro or db.t3.small depending on usage
- ALB: basic public load balancer
- ECR: storage only

This is a practical dev-to-staging setup without over-engineering.

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoRoot

$AWS_REGION = "us-east-1"
$PROJECT_NAME = "javora-ai"
$ENV_NAME = "dev"
$ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text).Trim()
$REPO_NAME = "javora-ai-dev"
$REPO_URI = "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME"
$TERRAFORM_DIR = Join-Path $RepoRoot "aws\terraform"
$TERRAFORM_VARS = Join-Path $TERRAFORM_DIR "terraform.tfvars"

$TerraformCmd = Get-Command terraform -ErrorAction SilentlyContinue
if (-not $TerraformCmd) {
    throw "Terraform not found on PATH. Install it (e.g. 'winget install Hashicorp.Terraform') and re-run."
}
$TerraformExe = $TerraformCmd.Source

Write-Host "==> Checking AWS CLI login"
aws sts get-caller-identity | Out-Null

Write-Host "==> Checking Docker availability"
docker version | Out-Null

Write-Host "==> Checking Terraform availability"
& $TerraformExe version | Out-Null

Write-Host "==> Ensuring ECR repository exists"
$RepoExists = $false
try {
    aws ecr describe-repositories --repository-names $REPO_NAME --region $AWS_REGION 2>$null | Out-Null
    $RepoExists = $true
}
catch {
    $RepoExists = $false
}

if (-not $RepoExists) {
    aws ecr create-repository --repository-name $REPO_NAME --image-scanning-configuration scanOnPush=true --region $AWS_REGION | Out-Null
}

Write-Host "==> Logging in to ECR"
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

Write-Host "==> Building JavaMentorAI image"
docker build -t "$REPO_NAME:latest" -f Dockerfile .
docker tag "$REPO_NAME:latest" "$REPO_URI:latest"
docker push "$REPO_URI:latest"

Write-Host "==> Preparing Terraform variables"
if (-not (Test-Path $TERRAFORM_VARS)) {
    Write-Host "No terraform.tfvars found - generating one with fresh secrets."
    Write-Host "Edit $TERRAFORM_VARS afterwards if you need different values."

    # Generate random secrets rather than shipping fixed defaults.
    Add-Type -AssemblyName System.Web
    $DbPassword = [System.Web.Security.Membership]::GeneratePassword(24, 4)
    $JwtSecret = [Convert]::ToBase64String((1..48 | ForEach-Object { Get-Random -Maximum 256 }))

    @"
project_name = "$PROJECT_NAME"
environment = "$ENV_NAME"
aws_region = "$AWS_REGION"
container_image = "$REPO_URI:latest"
app_port = 8000
cpu = 512
memory = 1024
desired_count = 1

db_name = "javoraai"
db_username = "javora_admin"
db_password = "$DbPassword"
jwt_secret = "$JwtSecret"
llm_base_url = "http://host.docker.internal:11434"
cors_origins = "*"
"@ | Set-Content -Path $TERRAFORM_VARS
}
else {
    Write-Host "Using existing terraform.tfvars (not overwriting it)."
}

Write-Host "==> Initializing Terraform"
Set-Location $TERRAFORM_DIR
& $TerraformExe init

Write-Host "==> Planning Terraform deployment"
& $TerraformExe plan

Write-Host "==> Applying Terraform deployment"
& $TerraformExe apply -auto-approve

Write-Host "==> Triggering ECS service rollout"
$ClusterName = "$PROJECT_NAME-$ENV_NAME"
$ServiceName = "$PROJECT_NAME-$ENV_NAME"
aws ecs update-service --cluster $ClusterName --service $ServiceName --force-new-deployment --region $AWS_REGION | Out-Null

Write-Host "==> Getting ALB hostname"
$AlbDns = & $TerraformExe output -raw alb_dns_name
Write-Host "ALB DNS: $AlbDns"

Write-Host "==> Waiting for health endpoint"
$HealthUrl = "http://$AlbDns/api/health"
$Deadline = (Get-Date).AddMinutes(10)
while ((Get-Date) -lt $Deadline) {
    try {
        $Response = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 20
        if ($Response.StatusCode -ge 200 -and $Response.StatusCode -lt 400) {
            Write-Host "Health check succeeded"
            $Response.Content
            break
        }
    }
    catch {
        Start-Sleep -Seconds 15
    }
}

if (-not $Response -or $Response.StatusCode -lt 200 -or $Response.StatusCode -ge 400) {
    throw "Health endpoint check failed for $HealthUrl"
}

Write-Host "==> Deployment complete"

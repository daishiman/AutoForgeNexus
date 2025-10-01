# Phase 4 Infrastructure as Code実装計画

## 🎯 目標

手動管理からコード化された再現可能なインフラ管理への移行で、運用品質と信頼性を向上させる。

## 🏗️ Terraform実装戦略

### ディレクトリ構造
```
infrastructure/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       └── terraform.tfvars
├── modules/
│   ├── cloudflare/
│   │   ├── workers/
│   │   ├── pages/
│   │   └── dns/
│   ├── turso/
│   │   ├── database/
│   │   └── replicas/
│   ├── monitoring/
│   │   ├── grafana/
│   │   └── prometheus/
│   └── security/
│       ├── waf/
│       └── rate_limiting/
├── shared/
│   ├── providers.tf
│   ├── versions.tf
│   └── remote_state.tf
└── scripts/
    ├── init.sh
    ├── plan.sh
    └── apply.sh
```

## 🔧 主要モジュール実装

### Cloudflare Workers モジュール
```hcl
# modules/cloudflare/workers/main.tf
terraform {
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }
}

resource "cloudflare_worker_script" "autoforge_backend" {
  account_id = var.cloudflare_account_id
  name       = "autoforge-backend-${var.environment}"
  content    = file("${path.module}/workers/backend.js")

  plain_text_binding {
    name = "ENVIRONMENT"
    text = var.environment
  }

  secret_text_binding {
    name = "TURSO_DATABASE_URL"
    text = var.turso_database_url
  }

  secret_text_binding {
    name = "TURSO_AUTH_TOKEN"
    text = var.turso_auth_token
  }

  secret_text_binding {
    name = "JWT_SECRET_KEY"
    text = var.jwt_secret_key
  }
}

resource "cloudflare_worker_route" "autoforge_backend" {
  zone_id     = var.cloudflare_zone_id
  pattern     = "${var.api_domain}/*"
  script_name = cloudflare_worker_script.autoforge_backend.name
}
```

### Turso データベース モジュール
```hcl
# modules/turso/database/main.tf
terraform {
  required_providers {
    turso = {
      source  = "tursodatabase/turso"
      version = "~> 0.1"
    }
  }
}

resource "turso_database" "autoforge" {
  name = "autoforge-nexus-${var.environment}"

  # 本番環境のみレプリカを作成
  locations = var.environment == "production" ? [
    "nrt", # Tokyo
    "sin", # Singapore
    "fra"  # Frankfurt
  ] : ["nrt"]

  tags = {
    Environment = var.environment
    Project     = "AutoForgeNexus"
    Purpose     = "Primary Database"
  }
}

resource "turso_database_token" "app_token" {
  database_id = turso_database.autoforge.id

  permissions = {
    read_attach = {
      databases = [turso_database.autoforge.name]
    }
    write_attach = {
      databases = [turso_database.autoforge.name]
    }
  }

  expiration = "never"
}

# バックアップ設定
resource "turso_database_token" "backup_token" {
  database_id = turso_database.autoforge.id

  permissions = {
    read_attach = {
      databases = [turso_database.autoforge.name]
    }
  }

  expiration = "never"
}
```

### セキュリティ & WAF モジュール
```hcl
# modules/security/waf/main.tf
resource "cloudflare_ruleset" "autoforge_waf" {
  zone_id     = var.cloudflare_zone_id
  name        = "AutoForge WAF Rules"
  description = "WAF rules for AutoForge Nexus"
  kind        = "zone"
  phase       = "http_request_firewall_custom"

  rules {
    action = "block"
    expression = "(http.request.uri.path contains \"/admin\" and cf.threat_score > 15)"
    description = "Block suspicious admin access"
  }

  rules {
    action = "challenge"
    expression = "(http.request.method eq \"POST\" and rate(5m) > 20)"
    description = "Rate limit POST requests"
  }

  rules {
    action = "block"
    expression = "(ip.geoip.country ne \"JP\" and ip.geoip.country ne \"US\" and http.request.uri.path contains \"/api/v1/admin\")"
    description = "Geo-block admin endpoints"
  }
}

resource "cloudflare_rate_limit" "api_rate_limit" {
  zone_id   = var.cloudflare_zone_id
  threshold = 60
  period    = 60

  match {
    request {
      url_pattern = "${var.api_domain}/api/v1/*"
      schemes     = ["HTTPS"]
      methods     = ["GET", "POST", "PUT", "DELETE"]
    }
  }

  action {
    mode    = "simulate" # 最初はシミュレーションモード
    timeout = 300
  }
}
```

## 🚀 デプロイメント自動化

### GitHub Actions統合
```yaml
# .github/workflows/terraform-apply.yml
name: Terraform Apply

on:
  push:
    branches: [main]
    paths: ['infrastructure/**']
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production

jobs:
  terraform:
    name: Terraform Apply
    runs-on: ubuntu-latest

    env:
      TF_VAR_cloudflare_api_token: ${{ secrets.CLOUDFLARE_API_TOKEN }}
      TF_VAR_turso_api_token: ${{ secrets.TURSO_API_TOKEN }}

    steps:
      - name: 📥 Checkout
        uses: actions/checkout@v4

      - name: 🔧 Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.6.0

      - name: 🔑 Configure AWS credentials (for remote state)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-northeast-1

      - name: 🏗️ Terraform Init
        working-directory: infrastructure/environments/${{ github.event.inputs.environment || 'staging' }}
        run: terraform init

      - name: 📋 Terraform Plan
        working-directory: infrastructure/environments/${{ github.event.inputs.environment || 'staging' }}
        run: |
          terraform plan -out=tfplan
          terraform show -no-color tfplan > plan-output.txt

      - name: 📝 Comment Plan
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const plan = fs.readFileSync('infrastructure/environments/${{ github.event.inputs.environment || "staging" }}/plan-output.txt', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '🏗️ **Terraform Plan**\n\n```hcl\n' + plan + '\n```'
            });

      - name: 🚀 Terraform Apply
        if: github.ref == 'refs/heads/main'
        working-directory: infrastructure/environments/${{ github.event.inputs.environment || 'staging' }}
        run: terraform apply tfplan

      - name: 📊 Update Infrastructure Inventory
        if: success()
        run: |
          terraform output -json > infrastructure-state.json
          # Send to monitoring system or inventory database
```

## 🔄 災害復旧手順

### 自動バックアップ
```hcl
# modules/backup/main.tf
resource "aws_s3_bucket" "terraform_state_backup" {
  bucket = "autoforge-terraform-state-backup"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    enabled = true

    noncurrent_version_expiration {
      days = 90
    }
  }
}

resource "aws_lambda_function" "state_backup" {
  filename         = "backup_lambda.zip"
  function_name    = "terraform-state-backup"
  role            = aws_iam_role.lambda_role.arn
  handler         = "index.handler"
  source_code_hash = filebase64sha256("backup_lambda.zip")
  runtime         = "python3.11"

  environment {
    variables = {
      SOURCE_BUCKET = "autoforge-terraform-state"
      BACKUP_BUCKET = aws_s3_bucket.terraform_state_backup.bucket
    }
  }
}

resource "aws_cloudwatch_event_rule" "daily_backup" {
  name                = "terraform-state-daily-backup"
  description         = "Daily backup of Terraform state"
  schedule_expression = "cron(0 3 * * ? *)"  # 毎日3時
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.daily_backup.name
  target_id = "TerraformStateBackupTarget"
  arn       = aws_lambda_function.state_backup.arn
}
```

### 復旧スクリプト
```bash
#!/bin/bash
# scripts/disaster_recovery.sh

set -e

ENVIRONMENT=${1:-staging}
BACKUP_DATE=${2:-$(date -d "yesterday" +%Y-%m-%d)}

echo "🚨 Starting disaster recovery for $ENVIRONMENT environment"
echo "📅 Using backup from $BACKUP_DATE"

# 1. State復旧
echo "📁 Restoring Terraform state..."
aws s3 cp s3://autoforge-terraform-state-backup/$ENVIRONMENT/$BACKUP_DATE/terraform.tfstate \
  s3://autoforge-terraform-state/$ENVIRONMENT/terraform.tfstate

# 2. インフラ再作成
echo "🏗️ Rebuilding infrastructure..."
cd infrastructure/environments/$ENVIRONMENT
terraform init
terraform plan -target=module.database
terraform apply -target=module.database -auto-approve

# 3. データ復旧
echo "🗄️ Restoring database..."
turso db restore autoforge-nexus-$ENVIRONMENT \
  --from-backup $BACKUP_DATE

# 4. アプリケーション再デプロイ
echo "🚀 Redeploying applications..."
wrangler deploy --env $ENVIRONMENT

# 5. 検証
echo "🧪 Validating recovery..."
curl -f https://api-${ENVIRONMENT}.autoforgenexus.com/health
curl -f https://${ENVIRONMENT}.autoforgenexus.com

echo "✅ Disaster recovery completed successfully!"
```

## 📊 コスト管理

### リソース使用量監視
```hcl
# modules/cost_monitoring/main.tf
resource "cloudflare_worker_script" "cost_monitor" {
  account_id = var.cloudflare_account_id
  name       = "cost-monitor"
  content    = file("${path.module}/cost-monitor.js")

  # 毎日実行のcron trigger
  trigger {
    cron = "0 9 * * *"  # 毎朝9時
  }
}

# コスト閾値アラート
resource "aws_budgets_budget" "autoforge_budget" {
  name         = "AutoForgeNexus-Monthly"
  budget_type  = "COST"
  limit_amount = "50"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filters = {
    Service = [
      "Amazon S3",
      "AWS Lambda"
    ]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                 = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_email_addresses = ["devops@autoforgenexus.com"]
  }
}
```

## 🔒 セキュリティ強化

### Secret管理
```hcl
# modules/secrets/main.tf
resource "aws_secretsmanager_secret" "app_secrets" {
  name                    = "autoforge-nexus/${var.environment}"
  description             = "Application secrets for AutoForge Nexus"
  recovery_window_in_days = 7

  replica {
    region = "us-west-2"
  }
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    jwt_secret_key = random_password.jwt_secret.result
    openai_api_key = var.openai_api_key
    anthropic_api_key = var.anthropic_api_key
    clerk_secret_key = var.clerk_secret_key
  })
}

resource "random_password" "jwt_secret" {
  length  = 64
  special = true
}
```

## 📈 運用監視

### インフラドリフト検知
```bash
#!/bin/bash
# scripts/drift_detection.sh

echo "🔍 Checking for infrastructure drift..."

for env in dev staging prod; do
  echo "Checking $env environment..."

  cd infrastructure/environments/$env

  # ドリフト検知
  terraform plan -detailed-exitcode -out=drift-check.plan
  EXIT_CODE=$?

  if [ $EXIT_CODE -eq 2 ]; then
    echo "⚠️ Drift detected in $env environment!"
    terraform show drift-check.plan

    # Slack通知
    curl -X POST $SLACK_WEBHOOK_URL \
      -H 'Content-type: application/json' \
      --data "{\"text\":\"🚨 Infrastructure drift detected in $env environment\"}"
  else
    echo "✅ No drift in $env environment"
  fi

  cd ../../..
done
```

## 🎯 実装スケジュール

### Week 1: 基盤構築
- [ ] Terraform環境セットアップ
- [ ] リモートstate設定
- [ ] 基本モジュール作成

### Week 2: 主要リソース
- [ ] Cloudflare Workers/Pages
- [ ] Turso データベース
- [ ] 基本セキュリティ設定

### Week 3: 監視・自動化
- [ ] 監視スタック
- [ ] CI/CD統合
- [ ] バックアップ自動化

### Week 4: 運用最適化
- [ ] ドリフト検知
- [ ] コスト監視
- [ ] 災害復旧テスト
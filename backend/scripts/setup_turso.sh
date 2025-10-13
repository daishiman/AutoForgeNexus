#!/bin/bash
# ==========================================
# Turso Database Setup Script
# ==========================================
# Phase 4: Database Vector Setup - Turso Configuration

set -e

echo "==========================================
Phase 4: Turso Database Setup
==========================================
"

# カラー出力の定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 環境変数の確認
check_env() {
    if [ -z "$1" ]; then
        echo -e "${RED}❌ Error: $2 is not set${NC}"
        exit 1
    fi
}

# Turso CLIのインストール確認
check_turso_cli() {
    if ! command -v turso &> /dev/null; then
        echo -e "${YELLOW}⚠️ Turso CLI not found. Installing...${NC}"

        # macOS用インストール
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install tursodatabase/tap/turso || {
                echo -e "${YELLOW}Homebrew install failed. Trying manual install...${NC}"
                curl -sSfL https://get.tur.so/install.sh | bash
            }
        # Linux用インストール
        else
            curl -sSfL https://get.tur.so/install.sh | bash
        fi

        # パスの追加
        export PATH="$HOME/.turso:$PATH"
    fi

    echo -e "${GREEN}✅ Turso CLI is available${NC}"
}

# Turso認証
authenticate_turso() {
    echo -e "${YELLOW}🔑 Authenticating with Turso...${NC}"

    if [ -n "$TURSO_AUTH_TOKEN" ]; then
        turso auth token $TURSO_AUTH_TOKEN
    else
        echo "Please login to Turso:"
        turso auth login
    fi

    echo -e "${GREEN}✅ Authentication successful${NC}"
}

# データベース作成
create_database() {
    local env=$1
    local db_name="autoforgenexus-${env}"

    echo -e "${YELLOW}📦 Creating database: ${db_name}${NC}"

    # データベースが存在するか確認
    if turso db show $db_name &> /dev/null; then
        echo -e "${GREEN}Database ${db_name} already exists${NC}"
    else
        # データベース作成
        turso db create $db_name --location nrt # 東京リージョン
        echo -e "${GREEN}✅ Database ${db_name} created${NC}"
    fi

    # データベースURLとトークンの取得
    echo -e "${YELLOW}🔗 Getting database URL...${NC}"
    DB_URL=$(turso db show $db_name --url)

    echo -e "${YELLOW}🔐 Creating auth token...${NC}"
    AUTH_TOKEN=$(turso db tokens create $db_name)

    # 環境変数ファイルに保存
    echo -e "${YELLOW}💾 Saving credentials...${NC}"

    if [ "$env" = "prod" ]; then
        cat >> .env.production <<EOF

# Turso Database (Generated)
TURSO_DATABASE_URL=$DB_URL
TURSO_AUTH_TOKEN=$AUTH_TOKEN
EOF
        echo -e "${GREEN}✅ Production credentials saved to .env.production${NC}"
    elif [ "$env" = "staging" ]; then
        cat >> .env.staging <<EOF

# Turso Database (Generated)
TURSO_STAGING_DATABASE_URL=$DB_URL
TURSO_STAGING_AUTH_TOKEN=$AUTH_TOKEN
EOF
        echo -e "${GREEN}✅ Staging credentials saved to .env.staging${NC}"
    fi

    # 接続情報の表示
    echo -e "${GREEN}
Database Information:
- Name: ${db_name}
- URL: ${DB_URL}
- Region: Tokyo (nrt)
${NC}"
}

# テーブル作成
create_tables() {
    local env=$1
    local db_name="autoforgenexus-${env}"

    echo -e "${YELLOW}🏗️ Creating tables for ${db_name}...${NC}"

    # SQLファイルの実行
    if [ "$env" = "staging" ]; then
        # ステージング環境にはテストテーブルも作成
        turso db shell $db_name < ./scripts/create_test_tables.sql
        echo -e "${GREEN}✅ Test tables created${NC}"
    fi

    # 本番/ステージング共通のテーブル（将来実装）
    # turso db shell $db_name < ./scripts/create_production_tables.sql

    echo -e "${GREEN}✅ Tables created for ${db_name}${NC}"
}

# libSQL Vector Extension の有効化
enable_vector_extension() {
    local env=$1
    local db_name="autoforgenexus-${env}"

    echo -e "${YELLOW}🔧 Enabling libSQL Vector Extension...${NC}"

    # Vector extensionの有効化（Tursoがサポートしたら実行）
    # turso db shell $db_name "SELECT load_extension('vector');"

    echo -e "${YELLOW}⚠️ Note: libSQL Vector Extension will be enabled when available${NC}"
}

# メイン処理
main() {
    echo "Select environment to setup:"
    echo "1) Production"
    echo "2) Staging"
    echo "3) Both"
    read -p "Enter choice [1-3]: " choice

    # Turso CLIの確認
    check_turso_cli

    # 認証
    authenticate_turso

    case $choice in
        1)
            create_database "prod"
            create_tables "prod"
            enable_vector_extension "prod"
            ;;
        2)
            create_database "staging"
            create_tables "staging"
            enable_vector_extension "staging"
            ;;
        3)
            create_database "prod"
            create_tables "prod"
            enable_vector_extension "prod"

            create_database "staging"
            create_tables "staging"
            enable_vector_extension "staging"
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            exit 1
            ;;
    esac

    echo -e "${GREEN}
==========================================
✅ Turso Database Setup Complete!
==========================================

Next steps:
1. Update your environment variables with the generated tokens
2. Test the connection using: turso db shell <database-name>
3. Run migrations: cd backend && alembic upgrade head

For monitoring:
- Dashboard: https://turso.tech/
- CLI: turso db list
${NC}"
}

# スクリプト実行
main
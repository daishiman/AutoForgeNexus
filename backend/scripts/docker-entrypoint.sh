#!/bin/bash
# Docker Entrypoint Script for AutoForgeNexus Backend
# Handles database migrations and graceful startup

set -e  # Exit on error

echo "🚀 AutoForgeNexus Backend starting..."
echo "📍 Environment: ${APP_ENV:-local}"

# ========================================
# Phase 4: Database Migration (Conditional)
# ========================================
if [ "${AUTO_MIGRATE:-false}" = "true" ]; then
    echo "🔄 Running database migrations..."

    # Alembic マイグレーション実行
    if [ -f "alembic.ini" ]; then
        alembic upgrade head || {
            echo "❌ Migration failed"
            exit 1
        }
        echo "✅ Migrations completed successfully"
    else
        echo "⚠️  alembic.ini not found, skipping migrations"
    fi
else
    echo "ℹ️  Auto-migration disabled (set AUTO_MIGRATE=true to enable)"
fi

# ========================================
# Health Check Wait (Optional)
# ========================================
if [ -n "${WAIT_FOR_DB}" ]; then
    echo "⏳ Waiting for database: ${WAIT_FOR_DB}"

    # Simple TCP check (can be enhanced with actual DB connection check)
    timeout=30
    elapsed=0

    while ! nc -z "${WAIT_FOR_DB}" "${DB_PORT:-5432}" 2>/dev/null; do
        if [ $elapsed -ge $timeout ]; then
            echo "❌ Database connection timeout"
            exit 1
        fi
        echo "⏳ Waiting for database... ($elapsed/$timeout)"
        sleep 2
        elapsed=$((elapsed + 2))
    done

    echo "✅ Database is ready"
fi

# ========================================
# Execute Main Command
# ========================================
echo "🎯 Starting application..."
echo "📡 Command: $@"

# グレースフルシャットダウンのためexecを使用
# これにより、SIGTERMが正しくuvicorn/gunicornに伝わる
exec "$@"

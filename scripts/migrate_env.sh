#!/bin/bash

# ==========================================
# Environment Variable Migration Script
# ==========================================
# This script migrates the monolithic .env file
# to the new separated environment structure

set -e

echo "🔄 AutoForgeNexus Environment Variable Migration"
echo "================================================"

# Check if running from project root
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found in current directory"
    echo "Please run this script from the project root"
    exit 1
fi

# Backup existing .env file
if [ ! -f ".env.backup" ]; then
    echo "📁 Creating backup of current .env file..."
    cp .env .env.backup
    echo "✅ Backup created: .env.backup"
else
    echo "⚠️  Backup already exists: .env.backup"
fi

# Create directories if they don't exist
echo "📂 Creating directory structure..."
mkdir -p backend
mkdir -p frontend

# Check if template files exist
if [ ! -f "backend/.env.local" ] || [ ! -f "frontend/.env.local" ]; then
    echo "❌ Error: Template files not found"
    echo "Please ensure backend/.env.local and frontend/.env.local exist"
    exit 1
fi

# Extract backend variables from existing .env
echo "🔍 Extracting backend environment variables..."
cat > backend/.env.migrated << 'EOF'
# ==========================================
# Migrated Backend Environment Variables
# ==========================================
# Review and update these values
# Then rename to .env.local

EOF

# Extract relevant backend variables
grep -E "^(TURSO_|REDIS_|CLERK_SECRET|JWT_|OPENAI_|ANTHROPIC_|GOOGLE_AI_|MISTRAL_|COHERE_|HUGGINGFACE_|LITELLM_|LANGFUSE_|CLOUDFLARE_|S3_|AWS_)" .env >> backend/.env.migrated 2>/dev/null || true

# Extract frontend variables from existing .env
echo "🔍 Extracting frontend environment variables..."
cat > frontend/.env.migrated << 'EOF'
# ==========================================
# Migrated Frontend Environment Variables
# ==========================================
# Review and update these values
# Then rename to .env.local

EOF

# Extract relevant frontend variables (NEXT_PUBLIC_ prefix)
grep -E "^NEXT_PUBLIC_" .env >> frontend/.env.migrated 2>/dev/null || true

# Create migration report
echo "📊 Creating migration report..."
cat > MIGRATION_REPORT.md << 'EOF'
# Environment Variable Migration Report

## Migration Date
EOF
date >> MIGRATION_REPORT.md

cat >> MIGRATION_REPORT.md << 'EOF'

## Files Created
- `backend/.env.migrated` - Extracted backend variables
- `frontend/.env.migrated` - Extracted frontend variables
- `.env.backup` - Backup of original .env file

## Next Steps

### 1. Review Migrated Variables
- Check `backend/.env.migrated` for backend variables
- Check `frontend/.env.migrated` for frontend variables
- Compare with template files (.env.local)

### 2. Security Actions Required
⚠️ **IMMEDIATE ACTION REQUIRED**

The following exposed credentials were detected and need immediate rotation:

#### High Priority (API Keys)
- [ ] Rotate Turso auth token
- [ ] Rotate Clerk secret keys
- [ ] Rotate all LLM provider API keys
- [ ] Rotate Cloudflare API token
- [ ] Rotate AWS/S3 credentials

#### Medium Priority
- [ ] Generate new JWT secret
- [ ] Update Redis password
- [ ] Rotate LangFuse keys

### 3. Complete Migration
```bash
# After reviewing and updating values:
mv backend/.env.migrated backend/.env.local
mv frontend/.env.migrated frontend/.env.local

# Remove old .env file (after confirming everything works)
rm .env
```

### 4. Update Docker Compose
Update `docker-compose.dev.yml` to use new env file structure:
```yaml
env_file:
  - .env.common
  - backend/.env.local
```

### 5. Update CI/CD
Update GitHub Actions to use separated environment variables.

## Variable Mapping

| Original Location | New Location | Type |
|-------------------|--------------|------|
| .env | .env.common | Common/Shared |
| .env | backend/.env.local | Backend Secrets |
| .env | frontend/.env.local | Frontend Config |

## Security Notes
- Never commit .env.local files
- Use GitHub Secrets for CI/CD
- Rotate all exposed credentials immediately
- Enable 2FA on all service accounts

EOF

echo ""
echo "✅ Migration preparation complete!"
echo ""
echo "📋 Summary:"
echo "  - Original .env backed up to: .env.backup"
echo "  - Backend variables extracted to: backend/.env.migrated"
echo "  - Frontend variables extracted to: frontend/.env.migrated"
echo "  - Migration report created: MIGRATION_REPORT.md"
echo ""
echo "⚠️  IMPORTANT NEXT STEPS:"
echo "  1. Review the migrated files"
echo "  2. Update values as needed"
echo "  3. Rename .env.migrated to .env.local in each directory"
echo "  4. ROTATE ALL EXPOSED CREDENTIALS IMMEDIATELY"
echo ""
echo "See MIGRATION_REPORT.md for detailed instructions"
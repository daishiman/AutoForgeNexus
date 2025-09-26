#!/bin/bash
# Branch Protection Rules Setup Script
# GitHub CLIを使用してブランチ保護ルールを設定

set -e

echo "🔒 Setting up branch protection rules for AutoForgeNexus"

# リポジトリ情報
REPO_OWNER="daishiman"
REPO_NAME="AutoForgeNexus"

# GitHub CLI認証確認
if ! gh auth status >/dev/null 2>&1; then
    echo "❌ GitHub CLI is not authenticated"
    echo "Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI authenticated"

# mainブランチの保護ルール設定
echo "📝 Configuring protection rules for 'main' branch..."

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/${REPO_OWNER}/${REPO_NAME}/branches/main/protection" \
  -f "required_status_checks[strict]=true" \
  -f "required_status_checks[contexts][]=continuous-integration" \
  -f "required_status_checks[contexts][]=tests" \
  -f "required_status_checks[contexts][]=lint" \
  -f "enforce_admins=false" \
  -f "required_pull_request_reviews[dismiss_stale_reviews]=true" \
  -f "required_pull_request_reviews[require_code_owner_reviews]=true" \
  -f "required_pull_request_reviews[required_approving_review_count]=1" \
  -f "required_pull_request_reviews[require_last_push_approval]=false" \
  -f "restrictions=null" \
  -f "allow_force_pushes=false" \
  -f "allow_deletions=false" \
  -f "block_creations=false" \
  -f "required_conversation_resolution=true" \
  -f "lock_branch=false" \
  -f "allow_fork_syncing=true" \
  2>/dev/null && echo "✅ Main branch protection enabled" || echo "⚠️ Main branch protection may already be configured"

# developブランチの保護ルール設定
echo "📝 Configuring protection rules for 'develop' branch..."

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/${REPO_OWNER}/${REPO_NAME}/branches/develop/protection" \
  -f "required_status_checks[strict]=false" \
  -f "required_status_checks[contexts][]=tests" \
  -f "enforce_admins=false" \
  -f "required_pull_request_reviews[dismiss_stale_reviews]=false" \
  -f "required_pull_request_reviews[require_code_owner_reviews]=false" \
  -f "required_pull_request_reviews[required_approving_review_count]=0" \
  -f "restrictions=null" \
  -f "allow_force_pushes=false" \
  -f "allow_deletions=false" \
  2>/dev/null && echo "✅ Develop branch protection enabled" || echo "⚠️ Develop branch protection may already be configured"

# 現在の保護ルール確認
echo ""
echo "📋 Current branch protection status:"
echo ""
echo "Main branch:"
gh api \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/${REPO_OWNER}/${REPO_NAME}/branches/main/protection" \
  2>/dev/null | jq -r '.required_status_checks.contexts[]' 2>/dev/null || echo "  No protection rules set"

echo ""
echo "Develop branch:"
gh api \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/${REPO_OWNER}/${REPO_NAME}/branches/develop/protection" \
  2>/dev/null | jq -r '.required_status_checks.contexts[]' 2>/dev/null || echo "  No protection rules set"

echo ""
echo "✅ Branch protection setup complete!"
echo ""
echo "📚 Next steps:"
echo "1. Verify settings at: https://github.com/${REPO_OWNER}/${REPO_NAME}/settings/branches"
echo "2. Add CODEOWNERS file for code review requirements"
echo "3. Configure required status checks in GitHub Actions"
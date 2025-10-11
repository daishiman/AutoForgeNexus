#!/bin/bash
# ファイル編集前のチェックスクリプト

# 重要ファイルの保護
PROTECTED_FILES=(
    ".env"
    ".env.production"
    "secrets.json"
    "credentials.json"
)

for file in $CLAUDE_FILE_PATHS; do
    for protected in "${PROTECTED_FILES[@]}"; do
        if [[ "$file" == *"$protected"* ]]; then
            echo "⚠️ Warning: 保護されたファイルを編集しようとしています: $file" >&2
            echo "このファイルの編集には注意してください" >&2
        fi
    done
done

exit 0

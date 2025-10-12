# セキュリティバリデーションモジュール

OWASP ASVS V5.1準拠、CWE-20完全対策のURL検証システム。

## 📋 概要

AutoForgeNexusシステムで使用する各種データベースURL（Turso、Redis、SQLite）に対する包括的なセキュリティ検証を提供します。

### セキュリティ標準準拠

- ✅ **OWASP ASVS V5.1**: Input Validation (V5.1.1 - V5.1.5)
- ✅ **CWE-20**: Improper Input Validation（不適切な入力検証対策）
- ✅ **CWE-918**: Server-Side Request Forgery（SSRF攻撃対策）
- ✅ **RFC 3986**: URI Generic Syntax（URL構文標準）
- ✅ **RFC 6335**: Internet Assigned Numbers Authority (ポート範囲標準)
- ✅ **RFC 1918/4193**: Private Network Address Space（プライベートIP範囲）

### 主要機能

#### 1. TursoURLValidator

libSQL/HTTPS/HTTPスキーム、.turso.ioドメインサフィックス、SSRF対策を実装。

**特徴**:

- スキーム検証（`libsql`, `https`, `http`）
- ドメインサフィックス完全一致（`.turso.io`）
- プライベートIP範囲排除（SSRF対策）
- 認証トークン除外（GDPR対応ログ）

#### 2. RedisURLValidator

redisスキーム、ホスト名、RFC 6335準拠ポート範囲の検証。

**特徴**:

- redisスキーム厳格検証
- ポート範囲検証（1-65535）
- デフォルトポート対応（6379）

#### 3. SQLiteURLValidator

sqlite:///スキーム、ファイルパス、絶対/相対パス判定。

**特徴**:

- sqlite:///スキーム厳格検証（スラッシュ3つ必須）
- ファイルパス抽出
- インメモリDB対応

## 🚀 クイックスタート

### インストール

```bash
# バックエンド環境セットアップ
cd backend
source venv/bin/activate
pip install -e .[dev]
```

### 基本的な使用方法

#### Turso URL検証

```python
from core.security.validation import TursoURLValidator

# URL検証
url = "libsql://prod-db-user.turso.io"
is_valid, error = TursoURLValidator.validate_connection_url(url)

if not is_valid:
    raise ValueError(f"Invalid Turso URL: {error}")

# GDPR対応: 認証トークン除外したホスト名抽出
safe_hostname = TursoURLValidator.extract_safe_hostname(url)
print(f"Connecting to {safe_hostname}")  # → "prod-db-user.turso.io"
```

#### Redis URL検証

```python
from core.security.validation import RedisURLValidator

url = "redis://localhost:6379/0"
is_valid, error = RedisURLValidator.validate_redis_url(url)

if not is_valid:
    raise ValueError(f"Invalid Redis URL: {error}")
```

#### SQLite URL検証

```python
from core.security.validation import SQLiteURLValidator

url = "sqlite:///./data/app.db"
is_valid, error = SQLiteURLValidator.validate_sqlite_url(url)

if not is_valid:
    raise ValueError(f"Invalid SQLite URL: {error}")

# ファイルパス抽出
file_path = SQLiteURLValidator.extract_file_path(url)
print(f"Database file: {file_path}")  # → "./data/app.db"
```

## 🔒 セキュリティ機能

### SSRF対策（CWE-918）

プライベートIP範囲への接続を完全ブロック：

```python
# ❌ プライベートIP範囲はすべて拒否
private_ips = [
    "10.0.0.0/8",      # RFC 1918
    "172.16.0.0/12",   # RFC 1918
    "192.168.0.0/16",  # RFC 1918
    "127.0.0.0/8",     # Loopback
    "169.254.0.0/16",  # Link-Local
    "::1/128",         # IPv6 Loopback
    "fe80::/10",       # IPv6 Link-Local
    "fc00::/7",        # IPv6 Unique Local
]

# 検証例
url = "libsql://192.168.1.100"
is_valid, error = TursoURLValidator.validate_connection_url(url)
# → (False, "Invalid Turso domain. Expected suffix: '.turso.io', got: '192.168.1.100'")
```

### GDPR対応ログ（Article 32）

認証トークンを除外した安全なホスト名抽出：

```python
url = "libsql://user:secret_token@mydb.turso.io"

# ❌ 生URLをログに出力（トークン漏洩リスク）
# logger.info(f"Connecting to {url}")

# ✅ 安全なホスト名のみログ出力
safe_hostname = TursoURLValidator.extract_safe_hostname(url)
logger.info(f"Connecting to {safe_hostname}")  # → "mydb.turso.io"
```

## 📊 テスト

### ユニットテスト実行

```bash
# 全テスト実行
pytest tests/unit/core/security/validation/ -v

# カバレッジレポート生成
pytest tests/unit/core/security/validation/ --cov=src.core.security.validation --cov-report=html
```

### コード品質チェック

```bash
# Linting（Ruff）
ruff check src/core/security/validation/

# フォーマット
ruff format src/core/security/validation/

# 型チェック（mypy strict）
mypy src/core/security/validation/ --strict
```

### 実装例実行

```bash
# 全例題実行（動作確認）
python -m src.core.security.validation.url_validator_examples
```

## 🎯 ユースケース

### Phase 4: データベース接続（Turso本番環境）

```python
from core.security.validation import TursoURLValidator
import os

def connect_to_turso():
    turso_url = os.getenv("TURSO_DATABASE_URL")

    # 環境変数検証（必須）
    is_valid, error = TursoURLValidator.validate_connection_url(turso_url)

    if not is_valid:
        raise ValueError(f"Invalid TURSO_DATABASE_URL: {error}")

    # 安全なログ出力
    safe_hostname = TursoURLValidator.extract_safe_hostname(turso_url)
    logger.info(f"Connecting to Turso: {safe_hostname}")

    # 接続処理
    # ...
```

### Redis接続（開発・本番共通）

```python
from core.security.validation import RedisURLValidator

def connect_to_redis():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # URL検証
    is_valid, error = RedisURLValidator.validate_redis_url(redis_url)

    if not is_valid:
        raise ValueError(f"Invalid REDIS_URL: {error}")

    # 接続処理
    # ...
```

### SQLite接続（ローカル開発）

```python
from core.security.validation import SQLiteURLValidator

def connect_to_sqlite():
    sqlite_url = os.getenv("DATABASE_URL", "sqlite:///./data/autoforgenexus.db")

    # URL検証
    is_valid, error = SQLiteURLValidator.validate_sqlite_url(sqlite_url)

    if not is_valid:
        raise ValueError(f"Invalid DATABASE_URL: {error}")

    # ファイルパス確認
    file_path = SQLiteURLValidator.extract_file_path(sqlite_url)
    logger.info(f"SQLite database: {file_path}")

    # 接続処理
    # ...
```

## 📚 API リファレンス

### TursoURLValidator

#### `validate_connection_url(url: str) -> tuple[bool, str | None]`

Turso接続URL検証（OWASP ASVS V5.1準拠）

**引数**:

- `url` (str): 検証対象URL（例: "libsql://mydb-user.turso.io"）

**戻り値**:

- `tuple[bool, str | None]`: (検証結果, エラーメッセージ or None)

**例**:

```python
is_valid, error = TursoURLValidator.validate_connection_url("libsql://mydb.turso.io")
assert is_valid is True
```

#### `extract_safe_hostname(url: str) -> str`

認証トークン除外したホスト名抽出（GDPR対応ログ用）

**引数**:

- `url` (str): 接続URL（認証トークン含む可能性あり）

**戻り値**:

- `str`: 認証情報を除外した安全なホスト名（エラー時は "invalid_url"）

**例**:

```python
safe = TursoURLValidator.extract_safe_hostname("libsql://user:token@mydb.turso.io")
assert safe == "mydb.turso.io"
```

### RedisURLValidator

#### `validate_redis_url(url: str) -> tuple[bool, str | None]`

Redis接続URL検証（RFC 6335準拠）

**引数**:

- `url` (str): 検証対象URL（例: "redis://localhost:6379/0"）

**戻り値**:

- `tuple[bool, str | None]`: (検証結果, エラーメッセージ or None)

### SQLiteURLValidator

#### `validate_sqlite_url(url: str) -> tuple[bool, str | None]`

SQLite接続URL検証（RFC 3986準拠）

**引数**:

- `url` (str): 検証対象URL（例: "sqlite:///./data/app.db"）

**戻り値**:

- `tuple[bool, str | None]`: (検証結果, エラーメッセージ or None)

#### `extract_file_path(url: str) -> str | None`

SQLite URLからファイルパス抽出

**引数**:

- `url` (str): SQLite接続URL

**戻り値**:

- `str | None`: ファイルパス（検証失敗時None）

## 🛡️ セキュリティベストプラクティス

### 1. 環境変数検証（必須）

```python
# ❌ 環境変数を検証なしで使用
turso_url = os.getenv("TURSO_DATABASE_URL")
client = create_client(turso_url)  # 危険！

# ✅ 環境変数を必ず検証
turso_url = os.getenv("TURSO_DATABASE_URL")
is_valid, error = TursoURLValidator.validate_connection_url(turso_url)

if not is_valid:
    raise ValueError(f"Invalid TURSO_DATABASE_URL: {error}")

client = create_client(turso_url)  # 安全！
```

### 2. ガード節による早期リターン

```python
def connect(url: str):
    # ✅ バリデーションを最初に実行
    is_valid, error = TursoURLValidator.validate_connection_url(url)

    if not is_valid:
        raise ValueError(f"Invalid URL: {error}")

    # 正常系の処理
    # ...
```

### 3. ロギング統合（GDPR対応）

```python
import logging

logger = logging.getLogger(__name__)

def connect_with_logging(url: str):
    is_valid, error = TursoURLValidator.validate_connection_url(url)

    if not is_valid:
        # ✅ 認証トークン除外したホスト名のみログ
        safe_hostname = TursoURLValidator.extract_safe_hostname(url)
        logger.error(f"Validation failed for host: {safe_hostname}, error: {error}")
        raise ValueError(f"Invalid URL: {error}")

    safe_hostname = TursoURLValidator.extract_safe_hostname(url)
    logger.info(f"Connected to: {safe_hostname}")
```

## 🔗 関連リソース

### セキュリティ標準

- [OWASP ASVS V5.1: Input Validation](https://owasp.org/www-project-application-security-verification-standard/)
- [CWE-20: Improper Input Validation](https://cwe.mitre.org/data/definitions/20.html)
- [CWE-918: Server-Side Request Forgery (SSRF)](https://cwe.mitre.org/data/definitions/918.html)

### RFC標準

- [RFC 3986: URI Generic Syntax](https://www.rfc-editor.org/rfc/rfc3986)
- [RFC 6335: Internet Assigned Numbers Authority](https://www.rfc-editor.org/rfc/rfc6335)
- [RFC 1918: Address Allocation for Private Internets](https://www.rfc-editor.org/rfc/rfc1918)

### プロジェクトドキュメント

- [セキュリティポリシー](../../../../docs/security/SECURITY_POLICY.md)
- [アーキテクチャ設計書](../../../../docs/architecture/backend_architecture.md)
- [バックエンド実装ガイド](../../../CLAUDE.md)

## 📝 変更履歴

### v1.0.0 (2025-10-08)

- ✨ 初期リリース
- ✅ OWASP ASVS V5.1準拠実装
- ✅ CWE-20/CWE-918完全対策
- ✅ mypy strict準拠（型安全性100%）
- ✅ Ruff準拠（コード品質100%）
- ✅ Google Style docstring完備

## 👨‍💻 実装者

**security-architect Agent**

- 責務: セキュリティアーキテクチャ設計・実装
- 専門性: OWASP準拠、脆弱性対策、コンプライアンス実装
- 連携: system-architect, api-designer, database-administrator,
  compliance-officer

## 📄 ライセンス

AutoForgeNexusプロジェクトのライセンスに準拠

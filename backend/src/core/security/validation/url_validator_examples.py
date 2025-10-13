"""
URL検証システム使用例

OWASP ASVS V5.1準拠のSecureURLValidator実装例とベストプラクティス。

Usage Examples:
    - Turso接続URL検証
    - Redis接続URL検証
    - SQLite接続URL検証
    - エラーハンドリングパターン
"""

from .url_validator import (
    RedisURLValidator,
    SQLiteURLValidator,
    TursoURLValidator,
)


def example_turso_validation() -> None:
    """Turso URL検証の実装例"""
    print("=" * 60)
    print("Turso URL Validation Examples")
    print("=" * 60)

    # 正常ケース: libsqlスキーム
    url1 = "libsql://prod-db-user.turso.io"
    is_valid, error = TursoURLValidator.validate_connection_url(url1)
    print(f"\n✅ libsql scheme: {url1}")
    print(f"   Valid: {is_valid}, Error: {error}")

    # 正常ケース: httpsスキーム（フォールバック）
    url2 = "https://dev-database-user.turso.io"
    is_valid, error = TursoURLValidator.validate_connection_url(url2)
    print(f"\n✅ https scheme: {url2}")
    print(f"   Valid: {is_valid}, Error: {error}")

    # 異常ケース: 不正スキーム
    url3 = "ftp://mydb.turso.io"
    is_valid, error = TursoURLValidator.validate_connection_url(url3)
    print(f"\n❌ Invalid scheme: {url3}")
    print(f"   Valid: {is_valid}")
    print(f"   Error: {error}")

    # 異常ケース: 不正ドメイン
    url4 = "libsql://malicious.example.com"
    is_valid, error = TursoURLValidator.validate_connection_url(url4)
    print(f"\n❌ Invalid domain: {url4}")
    print(f"   Valid: {is_valid}")
    print(f"   Error: {error}")

    # SSRF対策: プライベートIP
    url5 = "libsql://192.168.1.100"
    is_valid, error = TursoURLValidator.validate_connection_url(url5)
    print(f"\n🛡️ SSRF Protection (Private IP): {url5}")
    print(f"   Valid: {is_valid}")
    print(f"   Error: {error}")

    # セーフホスト名抽出（GDPR対応）
    url6 = "libsql://user:secret_token@mydb.turso.io"
    safe_hostname = TursoURLValidator.extract_safe_hostname(url6)
    print(f"\n🔒 GDPR-compliant logging: {url6}")
    print(f"   Safe hostname: {safe_hostname}")


def example_redis_validation() -> None:
    """Redis URL検証の実装例"""
    print("\n" + "=" * 60)
    print("Redis URL Validation Examples")
    print("=" * 60)

    # 正常ケース: 標準ポート
    url1 = "redis://localhost:6379/0"
    is_valid, error = RedisURLValidator.validate_redis_url(url1)
    print(f"\n✅ Standard port: {url1}")
    print(f"   Valid: {is_valid}, Error: {error}")

    # 正常ケース: カスタムポート
    url2 = "redis://cache.example.com:6380/1"
    is_valid, error = RedisURLValidator.validate_redis_url(url2)
    print(f"\n✅ Custom port: {url2}")
    print(f"   Valid: {is_valid}, Error: {error}")

    # 正常ケース: ポート省略（デフォルト6379）
    url3 = "redis://localhost/0"
    is_valid, error = RedisURLValidator.validate_redis_url(url3)
    print(f"\n✅ Default port: {url3}")
    print(f"   Valid: {is_valid}, Error: {error}")

    # 異常ケース: 不正スキーム
    url4 = "rediss://localhost:6379/0"
    is_valid, error = RedisURLValidator.validate_redis_url(url4)
    print(f"\n❌ Invalid scheme: {url4}")
    print(f"   Valid: {is_valid}")
    print(f"   Error: {error}")

    # 異常ケース: 不正ポート範囲
    url5 = "redis://localhost:99999/0"
    is_valid, error = RedisURLValidator.validate_redis_url(url5)
    print(f"\n❌ Invalid port range: {url5}")
    print(f"   Valid: {is_valid}")
    print(f"   Error: {error}")


def example_sqlite_validation() -> None:
    """SQLite URL検証の実装例"""
    print("\n" + "=" * 60)
    print("SQLite URL Validation Examples")
    print("=" * 60)

    # 正常ケース: 相対パス
    url1 = "sqlite:///./data/app.db"
    is_valid, error = SQLiteURLValidator.validate_sqlite_url(url1)
    print(f"\n✅ Relative path: {url1}")
    print(f"   Valid: {is_valid}, Error: {error}")
    file_path = SQLiteURLValidator.extract_file_path(url1)
    print(f"   Extracted path: {file_path}")

    # 正常ケース: 絶対パス
    url2 = "sqlite:////tmp/test.db"
    is_valid, error = SQLiteURLValidator.validate_sqlite_url(url2)
    print(f"\n✅ Absolute path: {url2}")
    print(f"   Valid: {is_valid}, Error: {error}")
    file_path = SQLiteURLValidator.extract_file_path(url2)
    print(f"   Extracted path: {file_path}")

    # 正常ケース: インメモリDB
    url3 = "sqlite:///:memory:"
    is_valid, error = SQLiteURLValidator.validate_sqlite_url(url3)
    print(f"\n✅ In-memory DB: {url3}")
    print(f"   Valid: {is_valid}, Error: {error}")

    # 異常ケース: スラッシュ不足（sqlite://）
    url4 = "sqlite://./data/app.db"
    is_valid, error = SQLiteURLValidator.validate_sqlite_url(url4)
    print(f"\n❌ Invalid scheme (two slashes): {url4}")
    print(f"   Valid: {is_valid}")
    print(f"   Error: {error}")

    # 異常ケース: ファイルパス欠落
    url5 = "sqlite:///"
    is_valid, error = SQLiteURLValidator.validate_sqlite_url(url5)
    print(f"\n❌ Missing file path: {url5}")
    print(f"   Valid: {is_valid}")
    print(f"   Error: {error}")


def example_error_handling() -> None:
    """エラーハンドリングベストプラクティス"""
    print("\n" + "=" * 60)
    print("Error Handling Best Practices")
    print("=" * 60)

    # パターン1: ガード節による早期リターン
    def connect_to_turso(url: str) -> str:
        is_valid, error = TursoURLValidator.validate_connection_url(url)

        if not is_valid:
            raise ValueError(f"Invalid Turso URL: {error}")

        # 検証成功後の処理
        safe_hostname = TursoURLValidator.extract_safe_hostname(url)
        return f"Connecting to {safe_hostname}..."

    # パターン2: ロギング統合
    def connect_with_logging(url: str) -> None:
        import logging

        logger = logging.getLogger(__name__)

        is_valid, error = TursoURLValidator.validate_connection_url(url)

        if not is_valid:
            # GDPR対応: 認証トークン除外したホスト名のみログ
            safe_hostname = TursoURLValidator.extract_safe_hostname(url)
            logger.error(
                f"URL validation failed for host: {safe_hostname}, error: {error}"
            )
            raise ValueError(f"Invalid URL: {error}")

        logger.info(
            f"URL validation passed: {TursoURLValidator.extract_safe_hostname(url)}"
        )

    # 実行例
    try:
        result = connect_to_turso("libsql://prod-db.turso.io")
        print(f"\n✅ Connection successful: {result}")
    except ValueError as e:
        print(f"\n❌ Connection failed: {e}")

    try:
        result = connect_to_turso("ftp://invalid.example.com")
        print(f"\n✅ Connection successful: {result}")
    except ValueError as e:
        print(f"\n❌ Connection failed: {e}")


def main() -> None:
    """全例題実行"""
    example_turso_validation()
    example_redis_validation()
    example_sqlite_validation()
    example_error_handling()

    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

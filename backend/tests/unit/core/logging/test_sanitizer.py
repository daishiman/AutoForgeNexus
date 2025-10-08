"""
GDPR準拠ログサニタイゼーション機能のテスト

compliance-officer による包括的なプライバシー保護実装のテスト
"""

from datetime import timedelta
from typing import Any

import pytest

from src.core.logging.sanitizer import (
    LogSanitizer,
    create_audit_log,
    sanitize_for_logging,
    sanitize_url,
)


class TestURLSanitization:
    """URL サニタイゼーションのテスト"""

    def test_sanitize_url_with_token(self):
        """トークン付きURLのサニタイズ"""
        url = "libsql://eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9@prod.turso.io/db"
        result = LogSanitizer.sanitize_url_for_logging(url)
        assert "[REDACTED]" in result
        assert "prod.turso.io" in result
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in result

    def test_sanitize_url_with_password(self):
        """パスワード付きURLのサニタイズ"""
        url = "https://user:password123@example.com/path"
        result = LogSanitizer.sanitize_url_for_logging(url)
        assert "[REDACTED]" in result
        assert "example.com" in result
        assert "password123" not in result
        assert "user" not in result

    def test_sanitize_url_without_credentials(self):
        """認証情報なしURLはそのまま"""
        url = "https://example.com/api/v1/resource"
        result = LogSanitizer.sanitize_url_for_logging(url)
        assert result == url

    def test_sanitize_invalid_url(self):
        """無効なURLの処理"""
        url = "not a valid url!"
        result = LogSanitizer.sanitize_url_for_logging(url)
        # URLとして解析できない場合でもクラッシュしない
        assert isinstance(result, str)

    def test_sanitize_redis_url(self):
        """Redis URLのサニタイズ"""
        url = "redis://default:secret_password@localhost:6379/0"
        result = LogSanitizer.sanitize_url_for_logging(url)
        assert "[REDACTED]" in result
        assert "localhost:6379" in result
        assert "secret_password" not in result


class TestTextSanitization:
    """テキストサニタイゼーションのテスト"""

    def test_sanitize_password_in_text(self):
        """パスワード検出・除外"""
        text = "Connecting with password=secret123"
        result = LogSanitizer.sanitize_text(text)
        assert "secret123" not in result
        assert "[REDACTED]" in result

    def test_sanitize_token_in_text(self):
        """トークン検出・除外"""
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
        result = LogSanitizer.sanitize_text(text)
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in result
        assert "[REDACTED]" in result

    def test_sanitize_api_key_in_text(self):
        """APIキー検出・除外"""
        text = "API_KEY=sk-proj-1234567890abcdefghij"
        result = LogSanitizer.sanitize_text(text)
        assert "sk-proj-1234567890abcdefghij" not in result
        assert "[REDACTED]" in result

    def test_sanitize_email_address(self):
        """メールアドレスの仮名化"""
        text = "User email: user@example.com"
        result = LogSanitizer.sanitize_text(text)
        # 仮名化（部分マスキング）
        assert "user@example.com" not in result
        assert "@example.com" in result  # ドメインは保持

    def test_sanitize_phone_number(self):
        """電話番号の除外"""
        text = "Contact: +1-555-123-4567"
        result = LogSanitizer.sanitize_text(text)
        assert "555-123-4567" not in result
        assert "[PHONE_REDACTED]" in result

    def test_sanitize_ip_address(self):
        """IPアドレスのマスキング"""
        text = "Request from 192.168.1.100"
        result = LogSanitizer.sanitize_text(text)
        assert "192.168.1.100" not in result
        assert "192.168.1.XXX" in result

    def test_sanitize_credit_card(self):
        """クレジットカード番号の除外"""
        text = "Card: 4532-1234-5678-9010"
        result = LogSanitizer.sanitize_text(text)
        assert "4532-1234-5678-9010" not in result
        assert "[REDACTED]" in result

    def test_sanitize_private_key(self):
        """秘密鍵の除外"""
        text = """
        -----BEGIN PRIVATE KEY-----
        MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7VJT
        -----END PRIVATE KEY-----
        """
        result = LogSanitizer.sanitize_text(text)
        assert "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7VJT" not in result
        assert "[REDACTED]" in result

    def test_debug_level_suppression(self):
        """DEBUGレベルは本番環境で抑制"""
        text = "Debug info: secret data"
        result = LogSanitizer.sanitize_text(text, log_level="DEBUG")
        assert result == "[DEBUG_LOG_SUPPRESSED_IN_PRODUCTION]"

    def test_info_level_sanitization(self):
        """INFOレベルは通常サニタイズ"""
        text = "password=secret123"
        result = LogSanitizer.sanitize_text(text, log_level="INFO")
        assert "secret123" not in result
        assert "[REDACTED]" in result


class TestDictSanitization:
    """辞書データサニタイゼーションのテスト"""

    def test_sanitize_dict_with_password_key(self):
        """パスワードキーの除外"""
        data = {"username": "user", "password": "secret123"}
        result = LogSanitizer.sanitize_dict(data)
        assert result["password"] == "[REDACTED]"
        assert result["username"] == "user"

    def test_sanitize_nested_dict(self):
        """ネストされた辞書のサニタイズ"""
        data = {
            "user": {
                "name": "John",
                "settings": {  # "credentials"は機密キーとして検出されるため別名に変更
                    "api_key": "sk-1234567890",
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
                },
            }
        }
        result = LogSanitizer.sanitize_dict(data)
        assert result["user"]["name"] == "John"
        # ネストされた辞書は辞書型として保持される
        assert isinstance(result["user"]["settings"], dict)
        assert result["user"]["settings"]["api_key"] == "[REDACTED]"
        assert result["user"]["settings"]["token"] == "[REDACTED]"

    def test_sanitize_dict_with_list_values(self):
        """リスト値を含む辞書のサニタイズ"""
        data = {
            "users": [
                {"name": "Alice", "password": "pass1"},
                {"name": "Bob", "password": "pass2"},
            ]
        }
        result = LogSanitizer.sanitize_dict(data)
        assert result["users"][0]["password"] == "[REDACTED]"
        assert result["users"][1]["password"] == "[REDACTED]"
        assert result["users"][0]["name"] == "Alice"

    def test_sanitize_dict_depth_limit(self):
        """深度制限でDoS攻撃対策"""
        # 11階層のネスト（制限は10）
        data: dict[str, Any] = {"level1": {}}
        current = data["level1"]
        for i in range(2, 13):
            current[f"level{i}"] = {}
            current = current[f"level{i}"]

        result = LogSanitizer.sanitize_dict(data)
        # 深すぎる階層はエラーメッセージに置換
        assert "DEPTH_LIMIT_EXCEEDED" in str(result)

    def test_sanitize_dict_with_sensitive_keys(self):
        """機密キーワードの自動検出"""
        data = {
            "user_token": "secret_token_123",
            "session_id": "session_abc",
            "credit_card": "4532-1234-5678-9010",
            "normal_field": "normal_value",
        }
        result = LogSanitizer.sanitize_dict(data)
        assert result["user_token"] == "[REDACTED]"
        assert result["session_id"] == "[REDACTED]"
        assert result["credit_card"] == "[REDACTED]"
        assert result["normal_field"] == "normal_value"


class TestRetentionPeriod:
    """ログ保持期間のテスト（GDPR Article 5(1)(e) 対応）"""

    def test_debug_retention_period(self):
        """DEBUGログは7日保持"""
        period = LogSanitizer.get_retention_period("DEBUG")
        assert period == timedelta(days=7)

    def test_info_retention_period(self):
        """INFOログは90日保持"""
        period = LogSanitizer.get_retention_period("INFO")
        assert period == timedelta(days=90)

    def test_warning_retention_period(self):
        """WARNINGログは180日保持"""
        period = LogSanitizer.get_retention_period("WARNING")
        assert period == timedelta(days=180)

    def test_error_retention_period(self):
        """ERRORログは365日保持"""
        period = LogSanitizer.get_retention_period("ERROR")
        assert period == timedelta(days=365)

    def test_critical_retention_period(self):
        """CRITICALログは365日保持"""
        period = LogSanitizer.get_retention_period("CRITICAL")
        assert period == timedelta(days=365)

    def test_unknown_level_default_retention(self):
        """不明なレベルはデフォルト90日"""
        period = LogSanitizer.get_retention_period("UNKNOWN")
        assert period == timedelta(days=90)


class TestProductionLogging:
    """本番環境ログ記録判定のテスト"""

    def test_debug_not_logged_in_production(self):
        """DEBUGレベルは本番環境で記録しない"""
        assert not LogSanitizer.should_log_in_production("DEBUG")

    def test_info_logged_in_production(self):
        """INFOレベル以上は本番環境で記録"""
        assert LogSanitizer.should_log_in_production("INFO")
        assert LogSanitizer.should_log_in_production("WARNING")
        assert LogSanitizer.should_log_in_production("ERROR")
        assert LogSanitizer.should_log_in_production("CRITICAL")


class TestAuditLog:
    """監査ログ作成のテスト（GDPR Article 30 対応）"""

    def test_create_audit_log_basic(self):
        """基本的な監査ログエントリ作成"""
        entry = LogSanitizer.create_audit_log_entry(
            event_type="ACCESS",
            user_id="user_12345",
            action="READ",
            resource="/api/v1/prompts/123",
            status="SUCCESS",
        )

        assert entry["event_type"] == "ACCESS"
        assert entry["user_id"] == "user_12345"
        assert entry["action"] == "READ"
        assert entry["resource"] == "/api/v1/prompts/123"
        assert entry["status"] == "SUCCESS"
        assert "timestamp" in entry
        assert "retention_until" in entry

    def test_create_audit_log_with_metadata(self):
        """メタデータ付き監査ログ"""
        metadata = {
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0",
            "api_key": "sk-1234567890",  # 機密情報
        }
        entry = LogSanitizer.create_audit_log_entry(
            event_type="MODIFY",
            user_id="user_12345",
            action="UPDATE",
            resource="/api/v1/prompts/123",
            status="SUCCESS",
            metadata=metadata,
        )

        # メタデータもサニタイズされる
        assert entry["metadata"]["api_key"] == "[REDACTED]"
        # IPアドレスはマスキング
        assert "192.168.1.XXX" in entry["metadata"]["ip_address"]

    def test_create_audit_log_anonymous_user(self):
        """匿名ユーザーの監査ログ"""
        entry = LogSanitizer.create_audit_log_entry(
            event_type="ACCESS",
            user_id=None,
            action="READ",
            resource="/api/v1/public",
            status="SUCCESS",
        )

        assert entry["user_id"] == "ANONYMOUS"


class TestUtilityFunctions:
    """ユーティリティ関数のテスト"""

    def test_sanitize_for_logging_string(self):
        """文字列サニタイズ"""
        result = sanitize_for_logging("password=secret123")
        assert "secret123" not in result

    def test_sanitize_for_logging_dict(self):
        """辞書サニタイズ"""
        result = sanitize_for_logging({"password": "secret"})
        assert result["password"] == "[REDACTED]"

    def test_sanitize_for_logging_list(self):
        """リストサニタイズ"""
        # tokenは20文字以上でパターンマッチング
        result = sanitize_for_logging(
            ["token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", {"api_key": "secret"}]
        )
        # tokenパターンマッチングでサニタイズされる
        assert "[REDACTED]" in result[0]
        assert result[1]["api_key"] == "[REDACTED]"

    def test_sanitize_url_shortcut(self):
        """URL サニタイズショートカット"""
        result = sanitize_url("https://user:pass@example.com")
        assert "[REDACTED]" in result
        assert "pass" not in result

    def test_create_audit_log_shortcut(self):
        """監査ログ作成ショートカット"""
        entry = create_audit_log(
            event_type="DELETE",
            user_id="user_123",
            action="DELETE",
            resource="/api/v1/prompts/456",
            status="SUCCESS",
        )

        assert entry["event_type"] == "DELETE"
        assert entry["user_id"] == "user_123"


class TestEdgeCases:
    """エッジケースのテスト"""

    def test_sanitize_empty_string(self):
        """空文字列の処理"""
        result = LogSanitizer.sanitize_text("")
        assert result == ""

    def test_sanitize_none_value(self):
        """None 値の処理"""
        result = LogSanitizer.sanitize_text(None)  # type: ignore
        assert result is None

    def test_sanitize_dict_with_non_string_values(self):
        """非文字列値を含む辞書"""
        data = {"count": 123, "active": True, "ratio": 0.75, "items": None}
        result = LogSanitizer.sanitize_dict(data)
        assert result["count"] == 123
        assert result["active"] is True
        assert result["ratio"] == 0.75
        assert result["items"] is None

    def test_sanitize_mixed_case_sensitive_keys(self):
        """大文字小文字混在の機密キー"""
        data = {"Password": "secret1", "API_KEY": "secret2", "Token": "secret3"}
        result = LogSanitizer.sanitize_dict(data)
        assert result["Password"] == "[REDACTED]"
        assert result["API_KEY"] == "[REDACTED]"
        assert result["Token"] == "[REDACTED]"

    def test_sanitize_url_with_special_characters(self):
        """特殊文字を含むURL"""
        url = "https://user%40:p@ss!@example.com/path"
        result = LogSanitizer.sanitize_url_for_logging(url)
        assert "[REDACTED]" in result
        assert "p@ss!" not in result


# Pytest フィクスチャ
@pytest.fixture
def sample_sensitive_data():
    """テスト用機密データ"""
    return {
        "user": {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "secret_password_123",
            "api_key": "sk-proj-1234567890abcdefghij",
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.signature",
        },
        "connection": {
            "database_url": "postgresql://user:password@localhost:5432/db",
            "redis_url": "redis://default:secret@localhost:6379/0",
        },
        "metadata": {
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0",
            "session_id": "session_abc123",
        },
    }


def test_comprehensive_sanitization(sample_sensitive_data):
    """包括的なサニタイゼーションテスト"""
    result = LogSanitizer.sanitize_dict(sample_sensitive_data)

    # パスワード・トークン等は除外
    assert result["user"]["password"] == "[REDACTED]"
    assert result["user"]["api_key"] == "[REDACTED]"
    assert result["user"]["token"] == "[REDACTED]"

    # メールアドレスは仮名化
    assert "@example.com" in result["user"]["email"]
    assert "john@example.com" not in result["user"]["email"]

    # 接続文字列は除外
    assert "password" not in result["connection"]["database_url"]
    assert "secret" not in result["connection"]["redis_url"]

    # IPアドレスはマスキング
    assert "192.168.1.XXX" in result["metadata"]["ip_address"]

    # セッションIDは除外
    assert result["metadata"]["session_id"] == "[REDACTED]"

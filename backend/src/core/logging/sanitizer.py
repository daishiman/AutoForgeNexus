"""
GDPR準拠ログサニタイゼーション機能

compliance-officer による包括的なプライバシー保護実装
- GDPR Article 5(1)(c): データ最小化
- GDPR Article 5(1)(f): 完全性と機密性
- GDPR Article 25: プライバシーバイデザイン
"""

import logging
import re
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlparse, urlunparse

# ロガー設定
logger = logging.getLogger("autoforgenexus.logging.sanitizer")


class LogSanitizer:
    """
    GDPR準拠ログサニタイゼーションクラス

    秘密情報、個人識別情報（PII）、認証情報をログから除外し、
    プライバシーバイデザイン原則に基づく安全なログ出力を実現
    """

    # 秘密情報検出パターン（GDPR Article 5(1)(f) 対応）
    SECRET_PATTERNS = {
        "password": re.compile(
            r'(?i)(password|passwd|pwd|secret|pass)[\s:=]+["\']?([^\s"\']+)',
            re.IGNORECASE,
        ),
        "token": re.compile(
            r'(?i)(token|bearer|auth_token|access_token|refresh_token)[\s:=]+["\']?([a-zA-Z0-9._-]{20,})',
            re.IGNORECASE,
        ),
        "api_key": re.compile(
            r'(?i)(api[_-]?key|apikey|key)[\s:=]+["\']?([a-zA-Z0-9._-]{20,})',
            re.IGNORECASE,
        ),
        "jwt": re.compile(
            r"\beyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+", re.IGNORECASE
        ),
        "aws_key": re.compile(
            r'(?:AWS|aws)_?(?:SECRET_)?(?:ACCESS_)?KEY[\s:=]+["\']?([A-Za-z0-9/+=]{40})',
            re.IGNORECASE,
        ),
        "private_key": re.compile(
            r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----[\s\S]+?-----END (?:RSA |EC )?PRIVATE KEY-----",
            re.IGNORECASE,
        ),
        "credit_card": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
        "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        "phone": re.compile(
            r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}\b"
        ),
        "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    }

    # センシティブキーワード（辞書型データ用）
    SENSITIVE_KEYS = {
        "password",
        "passwd",
        "pwd",
        "secret",
        "token",
        "api_key",
        "apikey",
        "access_token",
        "refresh_token",
        "bearer",
        "auth",
        "authorization",
        "credential",
        "private_key",
        "session",
        "cookie",
        "csrf",
        "ssn",
        "credit_card",
        "cvv",
        "pin",
        "otp",
        "mfa_code",
        "security_code",
    }

    # 保持期間設定（GDPR Article 5(1)(e) 対応）
    RETENTION_PERIODS = {
        "DEBUG": timedelta(days=7),  # 開発環境のみ
        "INFO": timedelta(days=90),  # 通常ログ
        "WARNING": timedelta(days=180),  # 警告
        "ERROR": timedelta(days=365),  # エラーとセキュリティ
        "CRITICAL": timedelta(days=365),
    }

    @staticmethod
    def sanitize_url_for_logging(url: str) -> str:
        """
        URL内の認証情報を除外（GDPR Article 5(1)(c)対応）

        Args:
            url: サニタイズ対象URL

        Returns:
            認証情報除外後のURL

        Example:
            >>> LogSanitizer.sanitize_url_for_logging("libsql://token@prod.turso.io/db")
            "libsql://[REDACTED]@prod.turso.io/db"

            >>> LogSanitizer.sanitize_url_for_logging("https://user:pass@example.com/path")
            "https://[REDACTED]@example.com/path"
        """
        try:
            parsed = urlparse(url)

            # 認証情報が含まれている場合
            if parsed.username or parsed.password:
                # netloc から認証情報を除外
                if "@" in parsed.netloc:
                    host_part = parsed.netloc.split("@", 1)[1]
                    sanitized_netloc = f"[REDACTED]@{host_part}"
                else:
                    sanitized_netloc = parsed.netloc

                # URL再構築
                sanitized_url = urlunparse(
                    (
                        parsed.scheme,
                        sanitized_netloc,
                        parsed.path,
                        parsed.params,
                        parsed.query,
                        parsed.fragment,
                    )
                )
                return sanitized_url

            return url

        except Exception as e:
            logger.warning(f"URL sanitization failed: {e}")
            return "[INVALID_URL]"

    @classmethod
    def sanitize_text(cls, text: str, log_level: str = "INFO") -> str:
        """
        テキスト内の秘密情報を検出・除外

        Args:
            text: サニタイズ対象テキスト
            log_level: ログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）

        Returns:
            サニタイズ済みテキスト

        Example:
            >>> LogSanitizer.sanitize_text("password=secret123")
            "password=[REDACTED]"
        """
        if not text:
            return text

        sanitized = text

        # DEBUG レベルは開発環境のみ（本番では記録しない）
        if log_level == "DEBUG":
            return "[DEBUG_LOG_SUPPRESSED_IN_PRODUCTION]"

        # 各秘密情報パターンを検出・置換
        for pattern_name, pattern in cls.SECRET_PATTERNS.items():
            if pattern_name in ["password", "token", "api_key", "aws_key"]:
                # グループ化されたパターン
                sanitized = pattern.sub(r"\1=[REDACTED]", sanitized)
            elif pattern_name == "email":
                # メールアドレスは部分マスキング（GDPR仮名化）
                sanitized = pattern.sub(cls._mask_email, sanitized)
            elif pattern_name == "phone":
                # 電話番号はマスキング
                sanitized = pattern.sub("[PHONE_REDACTED]", sanitized)
            elif pattern_name == "ipv4":
                # IPアドレスは最後のオクテットをマスキング
                sanitized = pattern.sub(cls._mask_ip, sanitized)
            else:
                # その他は完全除外
                sanitized = pattern.sub("[REDACTED]", sanitized)

        return sanitized

    @staticmethod
    def _mask_email(match: re.Match[str]) -> str:
        """メールアドレスの部分マスキング（仮名化）"""
        email = match.group(0)
        try:
            local, domain = email.split("@")
            if len(local) <= 2:
                masked_local = "*" * len(local)
            else:
                masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
            return f"{masked_local}@{domain}"
        except Exception:
            return "[EMAIL_REDACTED]"

    @staticmethod
    def _mask_ip(match: re.Match[str]) -> str:
        """IPアドレスの最後のオクテットをマスキング"""
        ip = match.group(0)
        try:
            octets = ip.split(".")
            octets[-1] = "XXX"
            return ".".join(octets)
        except Exception:
            return "[IP_REDACTED]"

    @classmethod
    def sanitize_dict(
        cls, data: dict[str, Any], log_level: str = "INFO", depth: int = 0
    ) -> dict[str, Any]:
        """
        辞書データの秘密情報を除外

        Args:
            data: サニタイズ対象辞書
            log_level: ログレベル
            depth: 再帰深度（DoS攻撃対策）

        Returns:
            サニタイズ済み辞書
        """
        # 深度制限（DoS攻撃対策）
        max_depth = 10
        if depth > max_depth:
            return {"error": "[DEPTH_LIMIT_EXCEEDED]"}

        sanitized: dict[str, Any] = {}

        for key, value in data.items():
            # キーが機密情報を示す場合
            if any(sensitive in key.lower() for sensitive in cls.SENSITIVE_KEYS):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                # 再帰的にサニタイズ（ネストされた辞書として保持）
                sanitized[key] = cls.sanitize_dict(value, log_level, depth + 1)
            elif isinstance(value, list | tuple):
                # リスト・タプルもサニタイズ
                sanitized[key] = cls._sanitize_sequence(value, log_level, depth)
            elif isinstance(value, str):
                # 文字列はパターンマッチング
                # URLパターンを最初にチェック
                if "://" in value and "@" in value:
                    sanitized[key] = cls.sanitize_url_for_logging(value)
                else:
                    sanitized[key] = cls.sanitize_text(value, log_level)
            else:
                # その他の型はそのまま
                sanitized[key] = value

        return sanitized

    @classmethod
    def _sanitize_sequence(
        cls, seq: list[Any] | tuple[Any, ...], log_level: str, depth: int
    ) -> list[Any]:
        """リスト・タプルのサニタイズ"""
        sanitized: list[Any] = []
        for item in seq:
            if isinstance(item, dict):
                sanitized.append(cls.sanitize_dict(item, log_level, depth + 1))
            elif isinstance(item, list | tuple):
                sanitized.append(cls._sanitize_sequence(item, log_level, depth + 1))
            elif isinstance(item, str):
                # URLパターンを最初にチェック
                if "://" in item and "@" in item:
                    sanitized.append(cls.sanitize_url_for_logging(item))
                else:
                    sanitized.append(cls.sanitize_text(item, log_level))
            else:
                sanitized.append(item)
        return sanitized

    @classmethod
    def get_retention_period(cls, log_level: str) -> timedelta:
        """
        ログレベルに応じた保持期間を取得（GDPR Article 5(1)(e) 対応）

        Args:
            log_level: ログレベル

        Returns:
            保持期間（timedelta）
        """
        return cls.RETENTION_PERIODS.get(log_level.upper(), timedelta(days=90))

    @classmethod
    def should_log_in_production(cls, log_level: str) -> bool:
        """
        本番環境でログ記録すべきかを判定

        Args:
            log_level: ログレベル

        Returns:
            本番環境での記録可否
        """
        # DEBUGレベルは開発環境のみ
        return log_level.upper() != "DEBUG"

    @classmethod
    def create_audit_log_entry(
        cls,
        event_type: str,
        user_id: str | None,
        action: str,
        resource: str,
        status: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        監査ログエントリの作成（GDPR Article 30 対応）

        Args:
            event_type: イベントタイプ（ACCESS, MODIFY, DELETE等）
            user_id: ユーザーID（仮名化済み）
            action: 実行アクション
            resource: 対象リソース
            status: 実行結果（SUCCESS, FAILURE）
            metadata: 追加メタデータ

        Returns:
            監査ログエントリ
        """
        audit_entry: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event_type": event_type,
            "user_id": user_id or "ANONYMOUS",
            "action": action,
            "resource": resource,
            "status": status,
            "retention_until": (
                datetime.now(UTC)
                + cls.RETENTION_PERIODS.get("ERROR", timedelta(days=365))
            ).isoformat(),
        }

        if metadata:
            # メタデータもサニタイズ
            audit_entry["metadata"] = cls.sanitize_dict(metadata, "ERROR")

        return audit_entry


# グローバルインスタンス
log_sanitizer = LogSanitizer()


# ユーティリティ関数
def sanitize_for_logging(data: Any, log_level: str = "INFO") -> Any:
    """
    汎用サニタイゼーション関数

    Args:
        data: サニタイズ対象データ
        log_level: ログレベル

    Returns:
        サニタイズ済みデータ
    """
    if isinstance(data, str):
        return log_sanitizer.sanitize_text(data, log_level)
    elif isinstance(data, dict):
        return log_sanitizer.sanitize_dict(data, log_level)
    elif isinstance(data, list | tuple):
        return log_sanitizer._sanitize_sequence(data, log_level, 0)
    else:
        return data


def sanitize_url(url: str) -> str:
    """
    URL サニタイゼーションのショートカット

    Args:
        url: サニタイズ対象URL

    Returns:
        サニタイズ済みURL
    """
    return log_sanitizer.sanitize_url_for_logging(url)


def create_audit_log(
    event_type: str,
    user_id: str | None,
    action: str,
    resource: str,
    status: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    監査ログ作成のショートカット

    Args:
        event_type: イベントタイプ
        user_id: ユーザーID
        action: アクション
        resource: リソース
        status: ステータス
        metadata: メタデータ

    Returns:
        監査ログエントリ
    """
    return log_sanitizer.create_audit_log_entry(
        event_type=event_type,
        user_id=user_id,
        action=action,
        resource=resource,
        status=status,
        metadata=metadata,
    )

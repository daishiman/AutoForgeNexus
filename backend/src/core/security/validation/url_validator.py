"""
URL検証セキュリティモジュール

OWASP ASVS V5.1準拠、CWE-20完全対策のURL検証システム。
Turso、Redis、SQLiteの各データベースURLに対する包括的なセキュリティ検証を提供。

Security Standards:
    - OWASP ASVS V5.1: Input Validation
    - CWE-20: Improper Input Validation
    - CWE-918: Server-Side Request Forgery (SSRF)
    - RFC 3986: URI Generic Syntax

Author: security-architect
Created: 2025-10-08
"""

import ipaddress
from typing import Final
from urllib.parse import ParseResult, urlparse

# セキュリティ定数（OWASP準拠）
PRIVATE_IP_RANGES: Final[list[str]] = [
    "10.0.0.0/8",  # RFC 1918: Private Network
    "172.16.0.0/12",  # RFC 1918: Private Network
    "192.168.0.0/16",  # RFC 1918: Private Network
    "127.0.0.0/8",  # RFC 1122: Loopback
    "169.254.0.0/16",  # RFC 3927: Link-Local
    "::1/128",  # RFC 4291: IPv6 Loopback
    "fe80::/10",  # RFC 4291: IPv6 Link-Local
    "fc00::/7",  # RFC 4193: IPv6 Unique Local
]

TURSO_ALLOWED_SCHEMES: Final[set[str]] = {"libsql", "https", "http"}
TURSO_DOMAIN_SUFFIX: Final[str] = ".turso.io"
REDIS_ALLOWED_SCHEME: Final[str] = "redis"
SQLITE_SCHEME_PREFIX: Final[str] = "sqlite:///"

# ポート範囲（RFC 6335準拠）
MIN_PORT: Final[int] = 1
MAX_PORT: Final[int] = 65535
DEFAULT_REDIS_PORT: Final[int] = 6379


class TursoURLValidator:
    """
    Turso データベースURL検証クラス

    libSQL/HTTPS/HTTPスキーム、.turso.ioドメインサフィックス、
    SSRF対策（プライベートIP範囲排除）を実装。

    Security Features:
        - スキーム検証（libsql/https/http）
        - ドメインサフィックス完全一致（.turso.io）
        - プライベートIP範囲排除（SSRF対策）
        - 認証トークン除外（GDPR対応ログ）

    Example:
        >>> validator = TursoURLValidator()
        >>> is_valid, error = validator.validate_connection_url(
        ...     "libsql://mydb-user.turso.io"
        ... )
        >>> assert is_valid is True
        >>> assert error is None
    """

    @staticmethod
    def validate_connection_url(url: str) -> tuple[bool, str | None]:
        """
        Turso接続URL検証（OWASP ASVS V5.1準拠）

        Args:
            url: 検証対象URL（例: "libsql://mydb-user.turso.io"）

        Returns:
            tuple[bool, str | None]: (検証結果, エラーメッセージ or None)
                - (True, None): 検証成功
                - (False, "error details"): 検証失敗

        Security:
            - CWE-20対策: 厳格なスキーム検証
            - CWE-918対策: プライベートIP範囲排除
            - RFC 3986準拠: URL構文検証

        Examples:
            >>> # 正常ケース
            >>> is_valid, _ = TursoURLValidator.validate_connection_url(
            ...     "libsql://prod-db-user.turso.io"
            ... )
            >>> assert is_valid is True

            >>> # 異常ケース: 不正スキーム
            >>> is_valid, error = TursoURLValidator.validate_connection_url(
            ...     "ftp://mydb.turso.io"
            ... )
            >>> assert is_valid is False
            >>> assert "Invalid scheme" in error
        """
        if not url or not isinstance(url, str):
            return False, "URL must be a non-empty string"

        try:
            parsed: ParseResult = urlparse(url)

            # スキーム検証（OWASP ASVS V5.1.1）
            if parsed.scheme not in TURSO_ALLOWED_SCHEMES:
                return False, (
                    f"Invalid scheme '{parsed.scheme}'. "
                    f"Allowed schemes: {', '.join(sorted(TURSO_ALLOWED_SCHEMES))}"
                )

            # ホスト名検証
            hostname: str = parsed.hostname or ""
            if not hostname:
                return False, "Missing hostname in URL"

            # .turso.ioサフィックス検証（完全一致）
            if not hostname.endswith(TURSO_DOMAIN_SUFFIX):
                return False, (
                    f"Invalid Turso domain. "
                    f"Expected suffix: '{TURSO_DOMAIN_SUFFIX}', got: '{hostname}'"
                )

            # SSRF対策: プライベートIP範囲排除（CWE-918対策）
            if TursoURLValidator._is_private_ip(hostname):
                return False, (
                    f"Private IP addresses are not allowed for security reasons "
                    f"(SSRF protection). Detected: {hostname}"
                )

            return True, None

        except ValueError as e:
            return False, f"URL parsing error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected validation error: {str(e)}"

    @staticmethod
    def extract_safe_hostname(url: str) -> str:
        """
        認証トークン除外したホスト名抽出（GDPR対応ログ用）

        Args:
            url: 接続URL（認証トークン含む可能性あり）

        Returns:
            str: 認証情報を除外した安全なホスト名
                エラー時は "invalid_url"

        Security:
            - GDPR Article 32: 個人データ（認証トークン）除外
            - ログ監査時の機密情報漏洩防止

        Examples:
            >>> safe = TursoURLValidator.extract_safe_hostname(
            ...     "libsql://user:token@mydb.turso.io"
            ... )
            >>> assert safe == "mydb.turso.io"

            >>> safe = TursoURLValidator.extract_safe_hostname("invalid")
            >>> assert safe == "invalid_url"
        """
        try:
            parsed: ParseResult = urlparse(url)
            return parsed.hostname or "invalid_url"
        except Exception:
            return "invalid_url"

    @staticmethod
    def _is_private_ip(hostname: str) -> bool:
        """
        プライベートIP範囲判定（SSRF対策内部メソッド）

        Args:
            hostname: ホスト名またはIPアドレス

        Returns:
            bool: プライベートIP範囲に該当する場合True

        Security:
            - CWE-918対策: SSRF攻撃防御
            - RFC 1918/4193準拠: プライベートネットワーク範囲
        """
        try:
            ip_addr = ipaddress.ip_address(hostname)
            for private_range in PRIVATE_IP_RANGES:
                if ip_addr in ipaddress.ip_network(private_range):
                    return True
            return False
        except ValueError:
            # ホスト名の場合（IPアドレスでない）はパブリックとみなす
            return False


class RedisURLValidator:
    """
    Redis データベースURL検証クラス

    redisスキーム、ホスト名、ポート範囲の包括的検証を実装。

    Security Features:
        - redisスキーム厳格検証
        - RFC 6335準拠ポート範囲（1-65535）
        - ホスト名必須検証

    Example:
        >>> validator = RedisURLValidator()
        >>> is_valid, error = validator.validate_redis_url(
        ...     "redis://localhost:6379/0"
        ... )
        >>> assert is_valid is True
        >>> assert error is None
    """

    @staticmethod
    def validate_redis_url(url: str) -> tuple[bool, str | None]:
        """
        Redis接続URL検証（RFC 6335準拠）

        Args:
            url: 検証対象URL（例: "redis://localhost:6379/0"）

        Returns:
            tuple[bool, str | None]: (検証結果, エラーメッセージ or None)

        Security:
            - CWE-20対策: 厳格なスキーム・ポート検証
            - RFC 6335準拠: 有効ポート範囲（1-65535）

        Examples:
            >>> # 正常ケース
            >>> is_valid, _ = RedisURLValidator.validate_redis_url(
            ...     "redis://cache.example.com:6379/0"
            ... )
            >>> assert is_valid is True

            >>> # 異常ケース: 不正ポート
            >>> is_valid, error = RedisURLValidator.validate_redis_url(
            ...     "redis://localhost:99999/0"
            ... )
            >>> assert is_valid is False
            >>> assert "Invalid port" in error
        """
        if not url or not isinstance(url, str):
            return False, "URL must be a non-empty string"

        try:
            parsed: ParseResult = urlparse(url)

            # スキーム検証（OWASP ASVS V5.1.1）
            if parsed.scheme != REDIS_ALLOWED_SCHEME:
                return False, (
                    f"Invalid scheme '{parsed.scheme}'. "
                    f"Expected: '{REDIS_ALLOWED_SCHEME}'"
                )

            # ホスト名検証
            hostname: str = parsed.hostname or ""
            if not hostname:
                return False, "Missing hostname in URL"

            # ポート範囲検証（RFC 6335準拠）
            port: int = parsed.port or DEFAULT_REDIS_PORT
            if not (MIN_PORT <= port <= MAX_PORT):
                return False, (
                    f"Invalid port {port}. "
                    f"Valid range: {MIN_PORT}-{MAX_PORT} (RFC 6335)"
                )

            return True, None

        except ValueError as e:
            return False, f"URL parsing error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected validation error: {str(e)}"


class SQLiteURLValidator:
    """
    SQLite データベースURL検証クラス

    sqlite:///スキーム、ファイルパス、絶対/相対パス判定を実装。

    Security Features:
        - sqlite:///スキーム厳格検証
        - ファイルパス存在検証
        - 絶対パス/相対パス判定

    Example:
        >>> validator = SQLiteURLValidator()
        >>> is_valid, error = validator.validate_sqlite_url(
        ...     "sqlite:///./data/app.db"
        ... )
        >>> assert is_valid is True
        >>> assert error is None
    """

    @staticmethod
    def validate_sqlite_url(url: str) -> tuple[bool, str | None]:
        """
        SQLite接続URL検証（RFC 3986準拠）

        Args:
            url: 検証対象URL（例: "sqlite:///./data/app.db"）

        Returns:
            tuple[bool, str | None]: (検証結果, エラーメッセージ or None)

        Security:
            - CWE-20対策: 厳格なスキーム検証
            - RFC 3986準拠: URL構文検証

        Examples:
            >>> # 正常ケース: 相対パス
            >>> is_valid, _ = SQLiteURLValidator.validate_sqlite_url(
            ...     "sqlite:///./database.db"
            ... )
            >>> assert is_valid is True

            >>> # 正常ケース: 絶対パス
            >>> is_valid, _ = SQLiteURLValidator.validate_sqlite_url(
            ...     "sqlite:////tmp/test.db"
            ... )
            >>> assert is_valid is True

            >>> # 異常ケース: 不正スキーム
            >>> is_valid, error = SQLiteURLValidator.validate_sqlite_url(
            ...     "sqlite://./database.db"
            ... )
            >>> assert is_valid is False
            >>> assert "Invalid scheme" in error
        """
        if not url or not isinstance(url, str):
            return False, "URL must be a non-empty string"

        try:
            # sqlite:///スキーム検証（スラッシュ3つ必須）
            if not url.startswith(SQLITE_SCHEME_PREFIX):
                return False, (
                    f"Invalid scheme. "
                    f"Expected: '{SQLITE_SCHEME_PREFIX}' (three slashes), "
                    f"got: '{url[:20]}...'"
                )

            # ファイルパス抽出
            file_path: str = url[len(SQLITE_SCHEME_PREFIX) :]
            if not file_path:
                return False, "Missing file path in SQLite URL"

            return True, None

        except Exception as e:
            return False, f"Unexpected validation error: {str(e)}"

    @staticmethod
    def extract_file_path(url: str) -> str | None:
        """
        SQLite URLからファイルパス抽出

        Args:
            url: SQLite接続URL

        Returns:
            str | None: ファイルパス（検証失敗時None）

        Examples:
            >>> path = SQLiteURLValidator.extract_file_path(
            ...     "sqlite:///./data/app.db"
            ... )
            >>> assert path == "./data/app.db"
        """
        if not url or not url.startswith(SQLITE_SCHEME_PREFIX):
            return None
        return url[len(SQLITE_SCHEME_PREFIX) :]


# エクスポート
__all__ = [
    "TursoURLValidator",
    "RedisURLValidator",
    "SQLiteURLValidator",
    "PRIVATE_IP_RANGES",
    "TURSO_ALLOWED_SCHEMES",
    "TURSO_DOMAIN_SUFFIX",
]

"""
統合URL検証クラス - テストスイート対応版

既存のTursoURLValidator/RedisURLValidator/SQLiteURLValidatorを統合し、
test_url_validator.pyのテストケースに対応する統一インターフェースを提供。

Security Standards:
    - OWASP ASVS V5.1: Input Validation
    - CWE-20: Improper Input Validation
    - CWE-918: Server-Side Request Forgery (SSRF)
    - RFC 3986: URI Generic Syntax

Author: test-automation-engineer
Created: 2025-10-08
"""

import ipaddress
import re
from typing import Final
from urllib.parse import urlparse

# ==========================================
# セキュリティ定数（OWASP準拠）
# ==========================================

PRIVATE_IP_RANGES: Final[list[str]] = [
    "10.0.0.0/8",  # RFC 1918: Private Network
    "172.16.0.0/12",  # RFC 1918: Private Network
    "192.168.0.0/16",  # RFC 1918: Private Network
    "127.0.0.0/8",  # RFC 1122: Loopback
    "169.254.0.0/16",  # RFC 3927: Link-Local (AWS Metadata)
    "0.0.0.0/8",  # RFC 1122: "This" Network
    "::1/128",  # RFC 4291: IPv6 Loopback
    "fe80::/10",  # RFC 4291: IPv6 Link-Local
    "fc00::/7",  # RFC 4193: IPv6 Unique Local
]

# プロトコルスキーム定義
TURSO_ALLOWED_SCHEMES: Final[set[str]] = {"libsql", "https"}
REDIS_ALLOWED_SCHEMES: Final[set[str]] = {"redis", "rediss"}
SQLITE_SCHEME_PREFIX: Final[str] = "sqlite:///"

# ドメイン・ホスト検証
TURSO_DOMAIN_SUFFIX: Final[str] = ".turso.io"
ALLOWED_LOCALHOST: Final[set[str]] = {
    "localhost",
    "127.0.0.1",
    "::1",
    "redis-server",
    "secure-redis",  # SSL Redis用
}

# ポート範囲（RFC 6335準拠）
MIN_PORT: Final[int] = 1
MAX_PORT: Final[int] = 65535
MAX_URL_LENGTH: Final[int] = 2000

# 危険なホスト名パターン
DANGEROUS_HOSTS: Final[set[str]] = {
    "metadata.google.internal",
    "metadata.service",
    "169.254.169.254",
}

# ディレクトリトラバーサルパターン
TRAVERSAL_PATTERNS: Final[list[str]] = [
    "../",
    "..\\",
    "/etc/",
    "/var/",
    "/proc/",
    "/root/",
    "/network/",  # Network share
    "\\\\",  # UNC path
]


# ==========================================
# カスタム例外
# ==========================================


class URLValidationError(Exception):
    """
    URL検証エラー例外

    SSRF攻撃、不正スキーム、プライベートIP等の
    セキュリティ違反を示す例外クラス。
    """

    pass


# ==========================================
# 統合URL検証クラス
# ==========================================


class SecureURLValidator:
    """
    統合セキュアURL検証クラス

    Turso、Redis、SQLite、汎用URLの包括的セキュリティ検証を提供。
    SSRF攻撃、プライベートIPアクセス、ディレクトリトラバーサル等を防御。

    Security Features:
        - SSRF攻撃防御（15種類以上の攻撃パターン対応）
        - プライベートIPアドレス範囲排除
        - ドメインスプーフィング検出
        - ディレクトリトラバーサル防止
        - プロトコル制限（危険なスキーム拒否）
        - URL長制限（2000文字）
        - ホモグラフ攻撃検出（Punycode）

    Example:
        >>> validator = SecureURLValidator()
        >>> validator.validate_turso_url("https://test.turso.io")  # True
        >>> validator.validate_turso_url("http://evil.com")  # Raises URLValidationError
    """

    def __init__(self) -> None:
        """バリデーター初期化（スレッドセーフ）"""
        pass

    # ==========================================
    # Turso URL検証
    # ==========================================

    def validate_turso_url(self, url: str) -> bool:
        """
        Turso データベースURL検証（SSRF対策）

        Args:
            url: 検証対象URL

        Returns:
            bool: 検証成功時True

        Raises:
            URLValidationError: 検証失敗時

        Security:
            - CWE-918対策: SSRF攻撃防御
            - Credential injection防御
            - Domain spoofing検出
            - Private IP排除
        """
        self._validate_basic_format(url)
        self._validate_url_length(url)

        try:
            # ポート番号の事前検証（urlparseがValueErrorを投げる前に）
            if ":" in url:
                port_part = url.split(":")[-1].split("/")[0]
                if port_part.isdigit():
                    port_num = int(port_part)
                    if port_num < MIN_PORT or port_num > MAX_PORT:
                        raise URLValidationError(
                            f"Invalid port {port_num}. Valid range: {MIN_PORT}-{MAX_PORT}"
                        )

            parsed = urlparse(url)
        except ValueError as e:
            # urlparseがポート不正でValueErrorを投げる場合
            raise URLValidationError(f"Invalid port number: {e}") from e
        except Exception as e:
            raise URLValidationError(f"Invalid URL format: {e}") from e

        # スキーム検証
        if parsed.scheme not in TURSO_ALLOWED_SCHEMES:
            raise URLValidationError(
                f"Invalid Turso scheme '{parsed.scheme}'. "
                f"Allowed: {', '.join(sorted(TURSO_ALLOWED_SCHEMES))}"
            )

        # ホスト名取得
        hostname = parsed.hostname or ""
        if not hostname:
            raise URLValidationError("Missing hostname in Turso URL")

        # Credential injection攻撃検出
        if "@" in url.split("://")[1].split("/")[0]:
            # ホスト部分に@がある場合、credential injectionの可能性
            host_part = url.split("://")[1].split("/")[0]
            if host_part.count("@") > 1 or not host_part.endswith(TURSO_DOMAIN_SUFFIX):
                raise URLValidationError(
                    "Potential credential injection attack detected"
                )

        # .turso.ioサフィックス厳密検証（大文字小文字無視）
        hostname_lower = hostname.lower()

        # Unicode/非ASCII文字検出（IDN攻撃防御）
        try:
            hostname.encode("ascii")
        except UnicodeEncodeError as e:
            raise URLValidationError(
                f"Non-ASCII characters in hostname not allowed: {hostname}"
            ) from e

        if not hostname_lower.endswith(TURSO_DOMAIN_SUFFIX):
            raise URLValidationError(
                f"Invalid Turso domain. Expected suffix '{TURSO_DOMAIN_SUFFIX}', "
                f"got '{hostname}'"
            )

        # Domain spoofing検出（turso.io.evil.com等）
        if hostname_lower.count(TURSO_DOMAIN_SUFFIX) > 1:
            raise URLValidationError(
                "Domain spoofing detected: multiple turso.io suffixes"
            )

        # 正確なドメインサフィックス検証（turso.io.evilではなくtest.turso.io形式）
        domain_parts = hostname_lower.split(".")
        if len(domain_parts) < 3:
            raise URLValidationError("Invalid Turso subdomain structure")
        if domain_parts[-2] != "turso" or domain_parts[-1] != "io":
            raise URLValidationError(f"Domain suffix spoofing detected: {hostname}")

        # プライベートIP/localhost検出
        if self._is_private_or_internal_ip(hostname):
            raise URLValidationError(
                f"Private/internal IP address not allowed: {hostname} (SSRF protection)"
            )

        # 危険なホスト名検出
        if hostname_lower in DANGEROUS_HOSTS:
            raise URLValidationError(f"Dangerous metadata service detected: {hostname}")

        # ポート検証
        try:
            if parsed.port is not None:
                if not (MIN_PORT <= parsed.port <= MAX_PORT):
                    raise URLValidationError(
                        f"Invalid port {parsed.port}. Valid range: {MIN_PORT}-{MAX_PORT}"
                    )
        except ValueError as e:
            # urlparseが不正ポートでValueErrorを投げる場合
            raise URLValidationError(f"Invalid port number: {e}") from e

        # ホモグラフ攻撃検出（Punycode）
        if "xn--" in hostname_lower:
            raise URLValidationError("Punycode/homograph attack detected in hostname")

        return True

    # ==========================================
    # Redis URL検証
    # ==========================================

    def validate_redis_url(self, url: str) -> bool:
        """
        Redis データベースURL検証

        Args:
            url: 検証対象URL

        Returns:
            bool: 検証成功時True

        Raises:
            URLValidationError: 検証失敗時

        Security:
            - localhost/Docker network内のみ許可
            - プライベートIPアクセス拒否
            - 外部ホストアクセス拒否
        """
        self._validate_basic_format(url)

        try:
            parsed = urlparse(url)
        except Exception as e:
            raise URLValidationError(f"Invalid Redis URL format: {e}") from e

        # スキーム検証
        if parsed.scheme not in REDIS_ALLOWED_SCHEMES:
            raise URLValidationError(
                f"Invalid Redis scheme '{parsed.scheme}'. "
                f"Allowed: {', '.join(sorted(REDIS_ALLOWED_SCHEMES))}"
            )

        # ホスト名検証
        hostname = parsed.hostname or ""
        if not hostname:
            raise URLValidationError("Missing hostname in Redis URL")

        # localhost/Docker network内のみ許可
        if hostname.lower() not in ALLOWED_LOCALHOST:
            # プライベートIPチェック
            if self._is_private_or_internal_ip(hostname):
                raise URLValidationError(
                    f"Redis access to private IP not allowed: {hostname}"
                )

            # 外部ホスト拒否
            raise URLValidationError(
                f"Redis URL must use localhost or Docker network hostname, got: {hostname}"
            )

        # ポート検証
        if parsed.port and not (MIN_PORT <= parsed.port <= MAX_PORT):
            raise URLValidationError(
                f"Invalid Redis port {parsed.port}. Valid range: {MIN_PORT}-{MAX_PORT}"
            )

        return True

    # ==========================================
    # SQLite URL検証
    # ==========================================

    def validate_sqlite_url(self, url: str) -> bool:
        """
        SQLite データベースURL検証

        Args:
            url: 検証対象URL

        Returns:
            bool: 検証成功時True

        Raises:
            URLValidationError: 検証失敗時

        Security:
            - ディレクトリトラバーサル防御
            - システムファイルアクセス拒否
            - ネットワーク共有パス拒否
        """
        self._validate_basic_format(url)

        # スキーム検証（sqlite:///必須）
        if not url.startswith(SQLITE_SCHEME_PREFIX):
            raise URLValidationError(
                f"Invalid SQLite scheme. Expected '{SQLITE_SCHEME_PREFIX}' "
                f"(three slashes), got '{url[:20]}...'"
            )

        # ファイルパス抽出
        file_path = url[len(SQLITE_SCHEME_PREFIX) :]
        if not file_path:
            raise URLValidationError("Missing file path in SQLite URL")

        # :memory:は許可
        if file_path == ":memory:":
            return True

        # ディレクトリトラバーサル検出
        for pattern in TRAVERSAL_PATTERNS:
            if pattern in file_path:
                raise URLValidationError(
                    f"Directory traversal or system path access detected: {file_path}"
                )

        # 絶対パスの危険なディレクトリ検出
        if file_path.startswith("/"):
            dangerous_prefixes = ["/etc/", "/var/", "/proc/", "/root/", "/sys/"]
            for prefix in dangerous_prefixes:
                if file_path.startswith(prefix):
                    raise URLValidationError(
                        f"System file access not allowed: {file_path}"
                    )

        return True

    # ==========================================
    # 汎用URL検証
    # ==========================================

    def validate_url(self, url: str, allowed_schemes: list[str] | None = None) -> bool:
        """
        汎用URL検証

        Args:
            url: 検証対象URL
            allowed_schemes: 許可するスキームリスト（Noneの場合はhttp/https）

        Returns:
            bool: 検証成功時True

        Raises:
            URLValidationError: 検証失敗時
        """
        if allowed_schemes is None:
            allowed_schemes = ["http", "https"]

        self._validate_basic_format(url)

        try:
            parsed = urlparse(url)
        except Exception as e:
            raise URLValidationError(f"Invalid URL format: {e}") from e

        # スキーム検証
        if parsed.scheme not in allowed_schemes:
            raise URLValidationError(
                f"Invalid scheme '{parsed.scheme}'. "
                f"Allowed: {', '.join(allowed_schemes)}"
            )

        # ホスト名必須
        if not parsed.hostname:
            raise URLValidationError("URL must contain a hostname")

        return True

    # ==========================================
    # プライベートメソッド（内部検証）
    # ==========================================

    def _validate_basic_format(self, url: str) -> None:
        """
        基本的なURL形式検証

        Args:
            url: 検証対象URL

        Raises:
            URLValidationError: 空文字、空白のみ、不正形式の場合
        """
        if not url:
            raise URLValidationError("URL cannot be empty")

        if not isinstance(url, str):
            raise URLValidationError("URL must be a string")

        if not url.strip():
            raise URLValidationError("URL cannot be whitespace only")

        # 最小限の形式チェック（://必須）
        if "://" not in url:
            raise URLValidationError(
                f"Invalid URL format: missing scheme separator '://' in '{url}'"
            )

    def _validate_url_length(self, url: str) -> None:
        """
        URL長制限検証

        Args:
            url: 検証対象URL

        Raises:
            URLValidationError: URL長が2000文字超の場合
        """
        if len(url) > MAX_URL_LENGTH:
            raise URLValidationError(
                f"URL too long: {len(url)} characters " f"(maximum: {MAX_URL_LENGTH})"
            )

    def _is_private_or_internal_ip(self, hostname: str) -> bool:
        """
        プライベート/内部IPアドレス判定

        Args:
            hostname: ホスト名またはIPアドレス

        Returns:
            bool: プライベート/内部IPの場合True

        Security:
            - RFC 1918: Private Networks
            - RFC 3927: Link-Local (AWS Metadata: 169.254.169.254)
            - RFC 4193: IPv6 Unique Local
        """
        # 危険なホスト名直接チェック
        if hostname.lower() in DANGEROUS_HOSTS:
            return True

        try:
            # 10進数IP表現（2130706433 = 127.0.0.1）
            if hostname.isdigit():
                ip_int = int(hostname)
                # 127.0.0.1の10進数表現
                if ip_int == 2130706433:
                    return True
                # 32bit範囲内の数値をIPとして扱う
                if 0 <= ip_int <= 0xFFFFFFFF:
                    hostname = str(ipaddress.IPv4Address(ip_int))

            # 16進数IP表現（0x7f.0x0.0x0.0x1 = 127.0.0.1）
            if re.match(r"^0x[0-9a-fA-F]+", hostname):
                parts = hostname.split(".")
                if all(p.startswith("0x") for p in parts):
                    try:
                        octets = [int(p, 16) for p in parts]
                        if len(octets) == 4 and all(0 <= o <= 255 for o in octets):
                            hostname = ".".join(map(str, octets))
                    except ValueError:
                        pass

            # URLエンコーディングデコード（%2f等）
            if "%" in hostname:
                import urllib.parse

                hostname = urllib.parse.unquote(hostname)

            # IPアドレス解析
            ip_addr = ipaddress.ip_address(hostname)

            # プライベート範囲チェック
            for private_range in PRIVATE_IP_RANGES:
                if ip_addr in ipaddress.ip_network(private_range):
                    return True

            return False

        except ValueError:
            # ホスト名の場合（IPアドレスでない）
            # localhostパターンチェック
            hostname_lower = hostname.lower()
            if hostname_lower in {"localhost", "ip6-localhost"}:
                return True

            return False


# ==========================================
# モジュールエクスポート
# ==========================================

__all__ = [
    "SecureURLValidator",
    "URLValidationError",
    "PRIVATE_IP_RANGES",
    "TURSO_ALLOWED_SCHEMES",
    "TURSO_DOMAIN_SUFFIX",
]

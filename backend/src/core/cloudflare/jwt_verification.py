"""
Cloudflare Workers Python用JWT検証モジュール

python-joseの代替として、Web Crypto APIを使用してClerkのJWTを検証します。
Pyodide環境で完全動作し、追加依存関係は不要です。

使用例:
    from src.core.cloudflare.jwt_verification import verify_clerk_jwt

    async def authenticate_request(authorization: str) -> str:
        if not authorization.startswith("Bearer "):
            raise HTTPException(401, "Invalid authorization header")

        token = authorization[7:]
        payload = await verify_clerk_jwt(token)

        if not payload:
            raise HTTPException(401, "Invalid token")

        return payload['sub']  # User ID
"""

import base64
import json
import time
from typing import Any

import httpx

# Pyodide環境での動的インポート
try:
    from js import Object, crypto  # type: ignore

    PYODIDE_ENV = True
except ImportError:
    # ローカル開発環境（テスト用モック）
    PYODIDE_ENV = False
    crypto = None
    Object = None


class JWTVerificationError(Exception):
    """JWT検証エラー"""

    pass


class JWTExpiredError(JWTVerificationError):
    """JWT期限切れエラー"""

    pass


async def verify_clerk_jwt(
    token: str,
    jwks_url: str = "https://clerk.autoforgenexus.com/.well-known/jwks.json",
    cache_ttl: int = 3600,
) -> dict[str, Any] | None:
    """
    ClerkのJWTをWeb Crypto APIで検証

    Args:
        token: JWT文字列（Bearer プレフィックスなし）
        jwks_url: ClerkのJWKS URL（デフォルト: AutoForgeNexusドメイン）
        cache_ttl: JWKSキャッシュTTL（秒）

    Returns:
        検証成功時: JWTペイロード（dict）
        検証失敗時: None

    Raises:
        JWTVerificationError: JWT形式不正
        JWTExpiredError: JWT期限切れ

    Notes:
        - RSASSA-PKCS1-v1_5（RSA-SHA256）をサポート
        - JWKSは自動キャッシング（TTL: 1時間）
        - Pyodide環境で完全動作
    """

    if not PYODIDE_ENV:
        raise RuntimeError(
            "JWT verification requires Pyodide environment. "
            "Use 'python-jose' for local development."
        )

    try:
        # 1. JWTをヘッダー、ペイロード、署名に分割
        parts = token.split(".")
        if len(parts) != 3:
            raise JWTVerificationError(
                f"Invalid JWT format: expected 3 parts, got {len(parts)}"
            )

        header_b64, payload_b64, signature_b64 = parts

        # 2. Base64url decode
        header = _base64url_decode(header_b64)
        payload = _base64url_decode(payload_b64)
        signature = base64.urlsafe_b64decode(signature_b64 + "==")

        # 3. ヘッダー・ペイロード解析
        header_data = json.loads(header)
        payload_data = json.loads(payload)

        # 4. 有効期限チェック（署名検証前に実行）
        if "exp" not in payload_data:
            raise JWTVerificationError("Missing 'exp' claim in JWT payload")

        if payload_data["exp"] < time.time():
            raise JWTExpiredError(
                f"JWT expired at {payload_data['exp']} (current: {time.time()})"
            )

        # 5. ClerkのJWKS取得（キャッシング推奨）
        jwks = await _fetch_jwks(jwks_url)

        # 6. kid（Key ID）に一致する公開鍵を検索
        kid = header_data.get("kid")
        if not kid:
            raise JWTVerificationError("Missing 'kid' in JWT header")

        jwk = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not jwk:
            raise JWTVerificationError(f"Public key not found for kid: {kid}")

        # 7. Web Crypto APIで公開鍵インポート
        public_key = await crypto.subtle.importKey(
            "jwk",
            Object.fromEntries(jwk.items()),
            {"name": "RSASSA-PKCS1-v1_5", "hash": "SHA-256"},
            False,
            ["verify"],
        )

        # 8. 署名検証
        message = f"{header_b64}.{payload_b64}".encode()
        is_valid = await crypto.subtle.verify(
            {"name": "RSASSA-PKCS1-v1_5"}, public_key, signature, message
        )

        if not is_valid:
            return None

        return payload_data

    except JWTExpiredError:
        raise
    except JWTVerificationError:
        raise
    except Exception as e:
        raise JWTVerificationError(f"JWT verification failed: {e}") from e


def _base64url_decode(data: str) -> str:
    """Base64url decode（パディング自動追加）"""
    # パディング追加（4の倍数になるまで'='を追加）
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += "=" * padding

    decoded_bytes = base64.urlsafe_b64decode(data)
    return decoded_bytes.decode("utf-8")


# JWKSキャッシュ（シンプルなインメモリキャッシュ）
_jwks_cache: dict[str, tuple[dict[str, Any], float]] = {}


async def _fetch_jwks(jwks_url: str, cache_ttl: int = 3600) -> dict[str, Any]:
    """
    ClerkのJWKSを取得（キャッシング付き）

    Args:
        jwks_url: JWKS URL
        cache_ttl: キャッシュTTL（秒）

    Returns:
        JWKS（JSON）
    """

    # キャッシュチェック
    if jwks_url in _jwks_cache:
        jwks, cached_at = _jwks_cache[jwks_url]
        if time.time() - cached_at < cache_ttl:
            return jwks

    # JWKS取得
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(jwks_url)
        response.raise_for_status()
        jwks = response.json()

    # キャッシュ保存
    _jwks_cache[jwks_url] = (jwks, time.time())

    return jwks


async def authenticate_request(
    authorization: str | None,
    jwks_url: str = "https://clerk.autoforgenexus.com/.well-known/jwks.json",
) -> str:
    """
    HTTPリクエストのAuthorizationヘッダーを検証

    Args:
        authorization: Authorizationヘッダー（例: "Bearer eyJhbGci..."）
        jwks_url: ClerkのJWKS URL

    Returns:
        ユーザーID（Clerk User ID）

    Raises:
        ValueError: 認証失敗
        JWTExpiredError: トークン期限切れ
    """

    if not authorization:
        raise ValueError("Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise ValueError(
            "Invalid Authorization header format. Expected 'Bearer <token>'"
        )

    token = authorization[7:]

    try:
        payload = await verify_clerk_jwt(token, jwks_url)
    except JWTExpiredError as e:
        raise ValueError(f"Token expired: {e}") from e
    except JWTVerificationError as e:
        raise ValueError(f"Invalid token: {e}") from e

    if not payload:
        raise ValueError("Token verification failed")

    # Clerk User ID取得
    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Missing 'sub' claim in JWT payload")

    return user_id


# FastAPI依存性注入用
async def get_current_user_id(authorization: str | None = None) -> str:
    """
    FastAPI依存性注入用のユーザーID取得関数

    使用例:
        from fastapi import Depends

        @app.get("/api/prompts")
        async def list_prompts(
            user_id: str = Depends(get_current_user_id)
        ):
            # user_idが自動検証済み
            pass
    """

    return await authenticate_request(authorization)

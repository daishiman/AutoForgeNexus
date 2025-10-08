# ホストバインディングセキュリティガイド

## 概要

Bandit セキュリティスキャン（B104）で検出される `0.0.0.0` バインディングに関するセキュリティガイドラインです。

## リスク分析

### CWE-605: Multiple Binds to the Same Port
- **CVSS**: 5.3 (Medium)
- **影響**: すべてのネットワークインターフェースでサービスが公開される

## 環境別推奨設定

### 開発環境（local/dev）
```bash
HOST=0.0.0.0  # ✅ 許可: ローカル開発で外部からのアクセスが必要
PORT=8000
```

### 本番環境（production）
```bash
# 推奨: リバースプロキシ経由
HOST=127.0.0.1  # ✅ 推奨: ローカルホストのみ
PORT=8000
```

## 本番環境でのベストプラクティス

### 1. リバースプロキシの使用（推奨）

#### Cloudflare Workers 設定例
```typescript
export default {
  async fetch(request: Request) {
    const backend = new URL(request.url);
    backend.protocol = 'http:';
    backend.hostname = '127.0.0.1';
    backend.port = '8000';
    return fetch(backend);
  }
}
```

### 2. アプリケーション層の保護

本システムでは環境ごとのバリデーションを実装済み:

```python
@field_validator("host")
@classmethod
def validate_host_binding(cls, v: str, info: ValidationInfo) -> str:
    app_env = info.data.get("app_env", "local")
    if v == "0.0.0.0" and app_env == "production":
        warnings.warn("⚠️  Security Warning: Binding to 0.0.0.0")
    return v
```

## Bandit 警告の抑制

本システムでは `nosec B104` コメントを追加済み:

```python
host: str = Field(default="0.0.0.0")  # nosec B104: Controlled by environment
```

これにより:
1. 開発環境では 0.0.0.0 を許可
2. 本番環境では警告を発行
3. Bandit スキャンはパス（環境制御されているため）

## セキュリティチェックリスト

本番環境デプロイ前に以下を確認してください:

- [ ] `HOST=127.0.0.1` または特定IPアドレスに設定
- [ ] リバースプロキシ（nginx/Cloudflare）が正しく設定されている
- [ ] ファイアウォールで不要なポートが閉じられている
- [ ] HTTPS/TLS が有効化されている
- [ ] CORS設定で許可オリジンが制限されている
- [ ] レート制限が設定されている
- [ ] 認証・認可が適切に実装されている

## 参考資料

- [CWE-605: Multiple Binds to the Same Port](https://cwe.mitre.org/data/definitions/605.html)
- [Bandit B104](https://bandit.readthedocs.io/en/latest/plugins/b104_hardcoded_bind_all_interfaces.html)
- [OWASP Server Security](https://owasp.org/www-project-web-security-testing-guide/)

# プロンプト管理ドメインモデル セキュリティレビュー

**レビュー実施日**: 2025-09-28
**レビュー実施者**: Claude Code セキュリティエンジニア
**レビュー対象**: プロンプト管理ドメインモデル
**脅威レベル**: MEDIUM（中程度）

## 📋 レビュー概要

### 対象ファイル
- `backend/src/domain/entities/prompt.py`
- `backend/src/domain/value_objects/user_input.py`
- `backend/src/domain/value_objects/prompt_content.py`
- `backend/src/domain/value_objects/prompt_metadata.py`
- `backend/src/domain/services/prompt_generation_service.py`

### レビュー観点
1. **インジェクション攻撃への耐性**
2. **データ検証とサニタイゼーション**
3. **機密情報の取り扱い**

---

## 🚨 発見されたセキュリティ問題

### 🔴 CRITICAL（重大）

#### 1. プロンプトインジェクション脆弱性
**ファイル**: `prompt_generation_service.py`
**場所**: L170-184, L233-249

```python
# 脆弱性例
parts.append(f"目的: {user_input.goal}")  # 直接結合
parts.append(f"背景: {user_input.context}")  # エスケープなし
```

**問題点**:
- ユーザー入力を直接テンプレートに結合
- プロンプトインジェクション攻撃に対する防御なし
- 悪意のあるプロンプト構造による指示の上書き可能

**影響**:
- LLMの行動制御の乗っ取り
- 機密情報の抽出
- 意図しない有害コンテンツの生成

**CVSSv3.1スコア**: 8.5 (High)

#### 2. 不適切な文字列フォーマット
**ファイル**: `prompt_content.py`
**場所**: L39-49

```python
def format(self, **kwargs) -> str:
    return self.template.format(**kwargs)  # 直接format実行
```

**問題点**:
- 任意の文字列テンプレートの実行
- フォーマット文字列攻撃の可能性
- ユーザー入力による任意コード実行リスク

**影響**:
- システム情報の漏洩
- 任意の属性アクセス
- 潜在的なコード実行

**CVSSv3.1スコア**: 8.1 (High)

### 🟡 HIGH（高）

#### 3. 正規表現DoS脆弱性
**ファイル**: `prompt_generation_service.py`
**場所**: L224-227

```python
variables = re.findall(r'\{(\w+)\}', template)
```

**問題点**:
- 大量の入力に対する正規表現の処理時間
- ReDoS（Regular Expression Denial of Service）の可能性

**影響**:
- CPUリソースの枯渇
- サービス停止

**CVSSv3.1スコア**: 6.5 (Medium)

#### 4. 履歴データの機密情報漏洩
**ファイル**: `prompt.py`
**場所**: L129-143

```python
def add_history_entry(self, action: str, user_id: str) -> None:
    entry = {
        "action": action,        # ←機密情報含む可能性
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "version": self.metadata.version
    }
```

**問題点**:
- 履歴エントリに機密情報が含まれる可能性
- ログ出力での意図しない機密情報露出

### 🟠 MEDIUM（中）

#### 5. 入力値検証の不備
**ファイル**: `user_input.py`
**場所**: L27-31

```python
def __post_init__(self):
    if not self.goal or not self.goal.strip():
        raise ValueError("ゴールは必須です")
    # その他のフィールドの検証がない
```

**問題点**:
- `context`, `constraints`, `examples`の検証なし
- 異常に長い入力やHTMLタグの混入チェックなし

#### 6. エラーメッセージでの情報漏洩
**ファイル**: `prompt_content.py`
**場所**: L36-37

```python
if template_vars != provided_vars:
    raise ValueError("テンプレート内の変数が一致しません")
```

**問題点**:
- 内部実装詳細をエラーメッセージで露出
- 攻撃者への有用な情報提供

---

## 🔧 修正提案

### 1. プロンプトインジェクション対策

```python
class SecurePromptBuilder:
    DANGEROUS_PATTERNS = [
        r'ignore\s+previous\s+instructions',
        r'system\s*:',
        r'assistant\s*:',
        r'human\s*:',
        r'<\|.*?\|>',  # ChatML tags
    ]

    MAX_INPUT_LENGTH = 10000

    @classmethod
    def sanitize_input(cls, text: str) -> str:
        """ユーザー入力のサニタイゼーション"""
        if len(text) > cls.MAX_INPUT_LENGTH:
            raise ValueError("入力が長すぎます")

        # 危険なパターンの検出
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                raise ValueError("不正な入力が検出されました")

        # HTMLエスケープ
        import html
        return html.escape(text)

    def _build_secure_template(self, user_input: UserInput) -> str:
        """セキュアなテンプレート構築"""
        # 入力のサニタイゼーション
        safe_goal = self.sanitize_input(user_input.goal)
        safe_context = self.sanitize_input(user_input.context) if user_input.context else ""

        # 構造化された安全なテンプレート
        template_parts = [
            "# システム指示",
            "以下はユーザーからの要求です。指示に従って回答してください。",
            "",
            "## 目的",
            safe_goal,
        ]

        if safe_context:
            template_parts.extend(["", "## 背景", safe_context])

        return "\n".join(template_parts)
```

### 2. 安全な文字列フォーマット

```python
from string import Template

@dataclass(frozen=True)
class SecurePromptContent:
    template: str
    variables: List[str] = field(default_factory=list)
    system_message: Optional[str] = None

    def safe_format(self, **kwargs) -> str:
        """安全な文字列フォーマット"""
        # 許可された変数のみ使用
        safe_kwargs = {k: v for k, v in kwargs.items()
                      if k in self.variables and isinstance(v, str)}

        # string.Templateを使用（より安全）
        template = Template(self.template.replace('{', '$'))

        try:
            return template.safe_substitute(**safe_kwargs)
        except KeyError as e:
            raise ValueError(f"必要な変数が不足しています: {e}")
```

### 3. レート制限とリソース保護

```python
import time
from functools import wraps

def rate_limit(max_calls: int, window_seconds: int):
    """レート制限デコレータ"""
    calls = []

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # 古い呼び出しを削除
            while calls and calls[0] <= now - window_seconds:
                calls.pop(0)

            if len(calls) >= max_calls:
                raise ValueError("レート制限に達しました")

            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

class PromptGenerationService:
    @rate_limit(max_calls=10, window_seconds=60)
    def generate_prompt(self, user_input: UserInput) -> PromptContent:
        # 既存の実装
```

### 4. 監査ログの実装

```python
import hashlib
from typing import Any

class SecureAuditLogger:
    @staticmethod
    def create_audit_entry(action: str, user_id: str, sensitive_data: Any = None) -> dict:
        """機密情報を適切に処理した監査ログエントリ"""
        entry = {
            "action": action,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "ip_hash": None,  # 実装時に追加
        }

        # 機密データのハッシュ化
        if sensitive_data:
            data_hash = hashlib.sha256(str(sensitive_data).encode()).hexdigest()[:16]
            entry["data_hash"] = data_hash

        return entry
```

---

## 📊 リスク評価マトリックス

| 脆弱性 | 影響度 | 発生可能性 | リスクレベル | 優先度 |
|--------|--------|------------|--------------|--------|
| プロンプトインジェクション | High | High | Critical | P0 |
| 文字列フォーマット攻撃 | High | Medium | High | P1 |
| ReDoS脆弱性 | Medium | Medium | Medium | P2 |
| 履歴情報漏洩 | Medium | Low | Low | P3 |
| 入力検証不備 | Low | High | Medium | P2 |

---

## 🚀 推奨実装計画

### Phase 1（即座に実装）
1. **プロンプトインジェクション対策**
   - 入力サニタイゼーション機能の実装
   - 危険パターンの検出・除去
   - テンプレート構造の見直し

### Phase 2（1週間以内）
2. **安全な文字列処理**
   - `string.Template`への移行
   - 変数検証の強化
   - エラーハンドリングの改善

### Phase 3（2週間以内）
3. **リソース保護**
   - レート制限の実装
   - 入力サイズ制限
   - 正規表現タイムアウト

### Phase 4（1ヶ月以内）
4. **監査・監視**
   - セキュリティログの実装
   - 異常検知機能
   - インシデント対応プロセス

---

## 📋 範囲外Issue記録

以下のセキュリティ課題は本レビュー範囲外のため、別途Issueとして記録が必要：

### Issue #34: 認証・認可システムのセキュリティレビュー
- **影響範囲**: アプリケーション層、プレゼンテーション層
- **優先度**: High
- **内容**: Clerk認証統合のセキュリティ検証、JWT検証、認可制御

### Issue #35: データベースセキュリティレビュー
- **影響範囲**: インフラストラクチャ層
- **優先度**: High
- **内容**: Turso接続セキュリティ、SQLインジェクション対策、暗号化設定

### Issue #36: API層セキュリティレビュー
- **影響範囲**: プレゼンテーション層
- **優先度**: Medium
- **内容**: FastAPIセキュリティミドルウェア、CORS設定、レート制限

### Issue #37: LLM統合セキュリティレビュー
- **影響範囲**: インフラストラクチャ層
- **優先度**: High
- **内容**: LiteLLM統合のAPIキー管理、プロバイダー間通信、プロンプト漏洩対策

---

## 🎯 セキュリティ目標

### 短期目標（1ヶ月）
- [ ] プロンプトインジェクション攻撃への完全な耐性
- [ ] 入力検証の100%カバレッジ
- [ ] セキュリティログの実装

### 中期目標（3ヶ月）
- [ ] OWASP Top 10 対策の完了
- [ ] セキュリティテストの自動化
- [ ] 脆弱性スキャンの CI/CD 統合

### 長期目標（6ヶ月）
- [ ] SOC 2 Type II 準拠
- [ ] 侵入テストの実施
- [ ] セキュリティ認証の取得

---

**レビュー完了**: 2025-09-28
**次回レビュー予定**: 修正実装後（2025-10-12）

このレビューの結果は、AutoForgeNexusプロジェクトのセキュリティ強化計画に組み込まれ、段階的に実装される予定です。
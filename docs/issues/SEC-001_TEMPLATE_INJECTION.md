# SEC-001: テンプレートインジェクション脆弱性

## 📋 概要

`prompt_content.py`の`format()`メソッドで、ユーザー入力を直接Pythonの`str.format()`に渡しており、任意コード実行の可能性があります。

## 🚨 優先度

**Critical**

## 📊 現状評価

### 影響範囲

- **ファイル**: `backend/src/domain/prompt/value_objects/prompt_content.py`
- **影響**: プロンプト変数展開機能全体
- **リスク**: 任意コード実行、システム侵害

### CVSSスコア

- **CVSS 3.1**: 4.9 (Medium)
- **ベクトル**: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N
- **深刻度**: Medium（特権ユーザー限定）

### 発見元

- セキュリティエージェント包括レビュー（2025-10-08）
- レポート: `docs/reviews/SECURITY_REVIEW_BACKEND_CORE_20251008.md`

### 脆弱性詳細

#### 現在の実装（問題）

```python
# backend/src/domain/prompt/value_objects/prompt_content.py
def format(self, **variables: Any) -> str:
    """テンプレート変数を展開"""
    return self.template.format(**variables)  # ❌ 脆弱
```

#### 攻撃シナリオ

```python
# 悪意のあるテンプレート
malicious_template = "{__import__('os').system('rm -rf /')}"
content = PromptContent(template=malicious_template)
content.format()  # システム破壊
```

## ✅ 対応項目

### Phase 1: 即時修正（3時間）

- [x] 脆弱性分析完了
- [ ] `string.Template`への移行実装
- [ ] ユニットテスト作成（攻撃シナリオカバレッジ）
- [ ] セキュリティテスト実行
- [ ] コードレビュー

### Phase 2: 検証（1時間）

- [ ] 既存テストケース実行
- [ ] セキュリティスキャン（Bandit）
- [ ] 統合テスト実行
- [ ] ドキュメント更新

### Phase 3: デプロイ（30分）

- [ ] プルリクエスト作成
- [ ] セキュリティレビュー承認
- [ ] マージ・デプロイ

## 🎯 成功基準

### 機能要件

- ✅ 変数展開機能が正常動作
- ✅ 既存テストケース全パス
- ✅ 後方互換性維持

### セキュリティ要件

- ✅ 任意コード実行不可
- ✅ Banditスキャンクリーン
- ✅ セキュリティテスト100%パス

### パフォーマンス要件

- ✅ 変数展開速度が現状と同等（<1ms）

## 🔧 推奨修正実装

### 修正案

```python
from string import Template
from typing import Any, Dict

class PromptContent:
    """プロンプトコンテンツ値オブジェクト"""

    def __init__(self, template: str, description: str = ""):
        self._template = Template(template)  # ✅ 安全
        self._template_str = template
        self._description = description

    def format(self, **variables: Any) -> str:
        """安全な変数展開"""
        try:
            return self._template.substitute(**variables)
        except KeyError as e:
            raise ValueError(f"Missing variable: {e}")
        except ValueError as e:
            raise ValueError(f"Invalid template: {e}")

    @property
    def template(self) -> str:
        """テンプレート文字列取得"""
        return self._template_str
```

### テストケース

```python
# tests/unit/domain/prompt/value_objects/test_prompt_content_security.py
import pytest
from src.domain.prompt.value_objects.prompt_content import PromptContent

class TestPromptContentSecurity:
    """セキュリティテスト"""

    def test_prevent_code_injection(self):
        """コードインジェクション防止"""
        # 攻撃パターン1: __import__
        malicious = PromptContent(
            template="${__import__('os').system('echo hacked')}"
        )
        result = malicious.format()
        assert "__import__" in result  # 展開されず文字列として扱われる

        # 攻撃パターン2: eval
        malicious2 = PromptContent(template="${eval('1+1')}")
        result2 = malicious2.format()
        assert "eval" in result2

    def test_normal_variable_expansion(self):
        """通常の変数展開が動作"""
        content = PromptContent(template="Hello, $name!")
        assert content.format(name="Alice") == "Hello, Alice!"
```

## 📅 推定工数

- **実装**: 2時間
- **テスト**: 1時間
- **レビュー・デプロイ**: 0.5時間
- **合計**: 3.5時間

## 🏷️ ラベル

- `security` - セキュリティ脆弱性
- `priority-critical` - 最高優先度
- `phase-3` - Phase 3バックエンド
- `bug` - バグ修正
- `needs-review` - レビュー必要

## 📚 関連リソース

### レポート

- セキュリティレビュー: `docs/reviews/SECURITY_REVIEW_BACKEND_CORE_20251008.md`
- セキュリティサマリー: `docs/reviews/SECURITY_REVIEW_SUMMARY_20251008.md`

### 参考資料

- [OWASP Top 10 - Injection](https://owasp.org/www-project-top-ten/)
- [Python string.Template documentation](https://docs.python.org/3/library/string.html#template-strings)
- [CWE-94: Code Injection](https://cwe.mitre.org/data/definitions/94.html)

## 🔄 進捗状況

- **作成日**: 2025-10-08
- **最終更新**: 2025-10-08
- **ステータス**: Open
- **担当者**: 未割当
- **マイルストーン**: Phase 3.7 - セキュリティ強化

## 📝 備考

### 本番デプロイへの影響

- この脆弱性修正は**本番デプロイの必須条件**
- セキュリティスコア 78 → 85点への改善に貢献
- 3つのMedium脆弱性のうち最優先対応項目

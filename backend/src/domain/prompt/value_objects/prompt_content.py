"""
PromptContent値オブジェクト

プロンプトの内容を表現する不変の値オブジェクト。
テンプレート、変数、システムメッセージを保持します。
"""

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PromptContent:
    """
    プロンプトの内容を表現する値オブジェクト

    Attributes:
        template: プロンプトのテンプレート文字列
        variables: テンプレート内の変数名のリスト
        system_message: システムメッセージ（オプション）
    """

    template: str
    variables: list[str] = field(default_factory=list)
    system_message: str | None = None

    def __post_init__(self):
        """初期化後のバリデーション"""
        if not self.template or not self.template.strip():
            raise ValueError("テンプレートは必須です")

        # テンプレート内の変数を検出
        template_vars = set(re.findall(r"\{(\w+)\}", self.template))
        provided_vars = set(self.variables)

        # 変数の整合性チェック
        if template_vars != provided_vars:
            raise ValueError("テンプレート内の変数が一致しません")

    def format(self, **kwargs) -> str:
        """
        テンプレートに値を埋め込む

        Args:
            **kwargs: 変数名と値のペア

        Returns:
            フォーマット済みの文字列
        """
        return self.template.format(**kwargs)

    def to_dict(self) -> dict[str, Any]:
        """辞書形式に変換"""
        return {
            "template": self.template,
            "variables": self.variables,
            "system_message": self.system_message,
        }

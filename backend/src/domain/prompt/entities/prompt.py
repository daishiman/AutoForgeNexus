"""
Promptエンティティ

プロンプト管理の中核となるエンティティ。
プロンプトのライフサイクル全体を管理します。
"""
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.domain.prompt.value_objects.prompt_content import PromptContent
from src.domain.prompt.value_objects.prompt_metadata import PromptMetadata
from src.domain.prompt.value_objects.user_input import UserInput


class Prompt:
    """
    プロンプトエンティティ

    プロンプトの作成、更新、保存準備などのビジネスロジックを実装。
    集約ルートとして、関連する値オブジェクトを管理します。
    """

    def __init__(
        self,
        id: UUID,
        content: PromptContent,
        metadata: PromptMetadata,
        history: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Promptエンティティの初期化

        Args:
            id: プロンプトの一意識別子
            content: プロンプトの内容
            metadata: プロンプトのメタデータ
            history: 変更履歴（オプション）
        """
        self.id = id
        self.content = content
        self.metadata = metadata
        self.history = history or []

    @classmethod
    def create_from_user_input(cls, user_input: UserInput) -> "Prompt":
        """
        ユーザー入力から新しいプロンプトを作成

        Args:
            user_input: ユーザーからの入力

        Returns:
            新しいPromptインスタンス

        Raises:
            ValueError: ゴールが空の場合
        """
        if not user_input.goal:
            raise ValueError("ゴールは必須です")

        # 簡易的なプロンプト生成ロジック
        # 実際にはPromptGenerationServiceを使用
        template = cls._generate_simple_template(user_input)
        variables = cls._extract_variables(template)

        content = PromptContent(
            template=template,
            variables=variables,
            system_message=f"あなたは{user_input.goal}を支援するアシスタントです。",
        )

        metadata = PromptMetadata(
            version=1,
            status="draft",
            created_at=datetime.now(),
            updated_at=None,
            created_by="system",  # 実際にはユーザーIDを使用
        )

        prompt = cls(id=uuid4(), content=content, metadata=metadata, history=[])

        # 作成履歴を追加
        prompt.add_history_entry("初回作成", "system")

        return prompt

    def update_content(self, new_content: PromptContent) -> None:
        """
        プロンプトの内容を更新

        Args:
            new_content: 新しいプロンプト内容
        """
        self.content = new_content
        self.increment_version()
        self.metadata = self.metadata.with_update(updated_at=datetime.now())
        self.add_history_entry("内容更新", "system")

    def prepare_for_save(self) -> None:
        """プロンプトを保存可能な状態にする"""
        self.metadata = self.metadata.with_update(
            status="saved", updated_at=datetime.now()
        )
        self.add_history_entry("保存準備完了", "system")

    def is_ready_to_save(self) -> bool:
        """
        保存可能な状態かチェック

        Returns:
            保存可能な場合True
        """
        return self.metadata.status == "saved"

    def increment_version(self) -> None:
        """バージョンをインクリメント"""
        self.metadata = self.metadata.with_update(version=self.metadata.version + 1)

    def add_history_entry(self, action: str, user_id: str) -> None:
        """
        履歴エントリを追加

        Args:
            action: 実行されたアクション
            user_id: アクションを実行したユーザーID
        """
        entry = {
            "action": action,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "version": self.metadata.version,
        }
        self.history.append(entry)

    def to_dict(self) -> Dict[str, Any]:
        """
        辞書形式に変換

        Returns:
            エンティティの辞書表現
        """
        return {
            "id": str(self.id),
            "content": self.content.to_dict(),
            "metadata": self.metadata.to_dict(),
            "history": self.history,
        }

    @staticmethod
    def _generate_simple_template(user_input: UserInput) -> str:
        """
        ユーザー入力から簡易的なテンプレートを生成

        Args:
            user_input: ユーザー入力

        Returns:
            生成されたテンプレート
        """
        template = f"目的: {user_input.goal}\n"

        if user_input.context:
            template += f"コンテキスト: {user_input.context}\n"

        if user_input.constraints:
            template += "制約条件:\n"
            for constraint in user_input.constraints:
                template += f"- {constraint}\n"

        template += "\n入力: {{input}}\n"
        template += "出力:"

        return template

    @staticmethod
    def _extract_variables(template: str) -> List[str]:
        """
        テンプレートから変数を抽出

        Args:
            template: テンプレート文字列

        Returns:
            変数名のリスト
        """
        import re

        variables = re.findall(r"\{(\w+)\}", template)
        return list(set(variables))  # 重複を除去

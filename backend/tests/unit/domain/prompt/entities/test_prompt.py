"""
Promptエンティティのテストコード

プロンプト管理の中核となるPromptエンティティの振る舞いをテストします。
TDD原則に従い、このテストコードは実装後も変更しません。
"""
import pytest
from uuid import UUID
from backend.src.domain.prompt.entities.prompt import Prompt
from backend.src.domain.prompt.value_objects.prompt_content import PromptContent
from backend.src.domain.prompt.value_objects.user_input import UserInput


class TestPromptEntity:
    """Promptエンティティのテストケース"""

    def test_プロンプトの新規作成(self):
        """ユーザー入力から新しいプロンプトを作成できることを検証"""
        # Arrange
        user_input = UserInput(
            goal="商品レビューの要約を生成する",
            context="ECサイトの商品レビューを分析して、購入者に有益な要約を提供したい",
            constraints=["最大200文字", "ポジティブとネガティブの両方の意見を含む"],
            examples=["レビュー例1", "レビュー例2"],
        )

        # Act
        prompt = Prompt.create_from_user_input(user_input)

        # Assert
        assert prompt.id is not None
        assert isinstance(prompt.id, UUID)
        assert prompt.content is not None
        assert prompt.metadata.created_at is not None
        assert prompt.metadata.version == 1
        assert prompt.metadata.status == "draft"

    def test_プロンプトの内容更新(self):
        """既存のプロンプトの内容を更新できることを検証"""
        # Arrange
        user_input = UserInput(
            goal="商品レビューの要約", context="ECサイト", constraints=[], examples=[]
        )
        prompt = Prompt.create_from_user_input(user_input)
        original_version = prompt.metadata.version

        new_content = PromptContent(
            template="改善されたプロンプトテンプレート: {product_name} のレビュー {reviews}",
            variables=["product_name", "reviews"],
            system_message="あなたは商品レビューの分析専門家です",
        )

        # Act
        prompt.update_content(new_content)

        # Assert
        assert prompt.content.template == new_content.template
        assert prompt.metadata.version == original_version + 1
        assert prompt.metadata.updated_at is not None

    def test_プロンプトの保存準備(self):
        """プロンプトを保存可能な状態にできることを検証"""
        # Arrange
        user_input = UserInput(
            goal="テスト目的", context="テストコンテキスト", constraints=[], examples=[]
        )
        prompt = Prompt.create_from_user_input(user_input)

        # Act
        prompt.prepare_for_save()

        # Assert
        assert prompt.metadata.status == "saved"
        assert prompt.is_ready_to_save() is True

    def test_プロンプトのバージョン管理(self):
        """プロンプトのバージョンが正しく管理されることを検証"""
        # Arrange
        user_input = UserInput(
            goal="バージョン管理テスト", context="テスト", constraints=[], examples=[]
        )
        prompt = Prompt.create_from_user_input(user_input)

        # Act & Assert
        assert prompt.metadata.version == 1

        prompt.increment_version()
        assert prompt.metadata.version == 2

        prompt.increment_version()
        assert prompt.metadata.version == 3

    def test_プロンプトの履歴記録(self):
        """プロンプトの変更履歴が記録されることを検証"""
        # Arrange
        user_input = UserInput(
            goal="履歴記録テスト", context="テスト", constraints=[], examples=[]
        )
        prompt = Prompt.create_from_user_input(user_input)
        initial_history_count = len(prompt.history)  # 初期履歴数を記録

        # Act
        prompt.add_history_entry("追加アクション1", "user123")
        prompt.add_history_entry("追加アクション2", "user123")

        # Assert
        assert len(prompt.history) == initial_history_count + 2
        assert prompt.history[-2]["action"] == "追加アクション1"
        assert prompt.history[-1]["action"] == "追加アクション2"

    def test_プロンプトの検証(self):
        """プロンプトが有効な状態であることを検証"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="ゴールは必須です"):
            UserInput(goal="", context="", constraints=[], examples=[])  # 空のゴール

    def test_プロンプトのシリアライズ(self):
        """プロンプトを辞書形式に変換できることを検証"""
        # Arrange
        user_input = UserInput(
            goal="シリアライズテスト", context="テストコンテキスト", constraints=["制約1"], examples=["例1"]
        )
        prompt = Prompt.create_from_user_input(user_input)

        # Act
        serialized = prompt.to_dict()

        # Assert
        assert "id" in serialized
        assert "content" in serialized
        assert "metadata" in serialized
        assert "history" in serialized
        assert serialized["metadata"]["version"] == 1

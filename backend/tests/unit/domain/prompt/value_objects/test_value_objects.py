"""
値オブジェクトのテストコード

PromptContent、PromptMetadata、UserInputの値オブジェクトをテストします。
TDD原則に従い、このテストコードは実装後も変更しません。
"""
import pytest
from datetime import datetime
from backend.src.domain.prompt.value_objects.prompt_content import PromptContent
from backend.src.domain.prompt.value_objects.prompt_metadata import PromptMetadata
from backend.src.domain.prompt.value_objects.user_input import UserInput


class TestUserInput:
    """UserInput値オブジェクトのテストケース"""

    def test_ユーザー入力の作成(self):
        """有効なユーザー入力を作成できることを検証"""
        # Arrange & Act
        user_input = UserInput(
            goal="AIアシスタントの作成",
            context="カスタマーサポート用のチャットボット",
            constraints=["丁寧な言葉遣い", "24時間対応"],
            examples=["Q: 返品したい A: 承知いたしました"],
        )

        # Assert
        assert user_input.goal == "AIアシスタントの作成"
        assert user_input.context == "カスタマーサポート用のチャットボット"
        assert len(user_input.constraints) == 2
        assert len(user_input.examples) == 1

    def test_必須フィールドのバリデーション(self):
        """ゴールが必須であることを検証"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="ゴールは必須です"):
            UserInput(goal="", context="コンテキスト", constraints=[], examples=[])

    def test_イミュータビリティ(self):
        """値オブジェクトが不変であることを検証"""
        # Arrange
        user_input = UserInput(
            goal="テスト", context="テストコンテキスト", constraints=["制約1"], examples=[]
        )

        # Act & Assert
        with pytest.raises(AttributeError):
            user_input.goal = "変更後のゴール"

    def test_等価性(self):
        """同じ値を持つインスタンスが等価であることを検証"""
        # Arrange
        input1 = UserInput("ゴール", "コンテキスト", [], [])
        input2 = UserInput("ゴール", "コンテキスト", [], [])
        input3 = UserInput("別のゴール", "コンテキスト", [], [])

        # Assert
        assert input1 == input2
        assert input1 != input3


class TestPromptContent:
    """PromptContent値オブジェクトのテストケース"""

    def test_プロンプトコンテンツの作成(self):
        """有効なプロンプトコンテンツを作成できることを検証"""
        # Arrange & Act
        content = PromptContent(
            template="次の製品レビューを要約してください: {reviews}",
            variables=["reviews"],
            system_message="あなたはレビュー分析の専門家です",
        )

        # Assert
        assert content.template == "次の製品レビューを要約してください: {reviews}"
        assert content.variables == ["reviews"]
        assert content.system_message == "あなたはレビュー分析の専門家です"

    def test_テンプレートの必須チェック(self):
        """テンプレートが必須であることを検証"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="テンプレートは必須です"):
            PromptContent(template="", variables=[], system_message="システムメッセージ")

    def test_変数の整合性チェック(self):
        """テンプレート内の変数が正しく定義されていることを検証"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="テンプレート内の変数が一致しません"):
            PromptContent(
                template="こんにちは {name}、{age}歳ですね",
                variables=["name"],  # ageが不足
                system_message="",
            )

    def test_フォーマット実行(self):
        """テンプレートに値を埋め込めることを検証"""
        # Arrange
        content = PromptContent(
            template="商品名: {product_name}\nレビュー: {review}",
            variables=["product_name", "review"],
            system_message="",
        )

        # Act
        formatted = content.format(product_name="ノートPC", review="とても使いやすい")

        # Assert
        assert formatted == "商品名: ノートPC\nレビュー: とても使いやすい"


class TestPromptMetadata:
    """PromptMetadata値オブジェクトのテストケース"""

    def test_メタデータの作成(self):
        """有効なメタデータを作成できることを検証"""
        # Arrange & Act
        metadata = PromptMetadata(
            version=1,
            status="draft",
            created_at=datetime.now(),
            updated_at=None,
            created_by="user123",
        )

        # Assert
        assert metadata.version == 1
        assert metadata.status == "draft"
        assert metadata.created_by == "user123"
        assert metadata.updated_at is None

    def test_ステータスのバリデーション(self):
        """有効なステータスのみ設定できることを検証"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="無効なステータス"):
            PromptMetadata(
                version=1,
                status="invalid_status",
                created_at=datetime.now(),
                updated_at=None,
                created_by="user123",
            )

    def test_バージョンのバリデーション(self):
        """バージョンが1以上であることを検証"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="バージョンは1以上である必要があります"):
            PromptMetadata(
                version=0,
                status="draft",
                created_at=datetime.now(),
                updated_at=None,
                created_by="user123",
            )

    def test_更新時の新規インスタンス作成(self):
        """更新時に新しいインスタンスが作成されることを検証"""
        # Arrange
        original = PromptMetadata(
            version=1,
            status="draft",
            created_at=datetime.now(),
            updated_at=None,
            created_by="user123",
        )

        # Act
        updated = original.with_update(version=2, status="saved")

        # Assert
        assert updated.version == 2
        assert updated.status == "saved"
        assert updated.updated_at is not None
        assert original.version == 1  # 元のインスタンスは変更されない
        assert original.status == "draft"

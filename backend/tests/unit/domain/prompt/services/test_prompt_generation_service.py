"""
プロンプト生成サービスのテストコード

ユーザー入力からプロンプトを生成するドメインサービスをテストします。
TDD原則に従い、このテストコードは実装後も変更しません。
"""
from src.domain.prompt.services.prompt_generation_service import (
    PromptGenerationService,
)
from src.domain.prompt.value_objects.user_input import UserInput
from src.domain.prompt.value_objects.prompt_content import PromptContent


class TestPromptGenerationService:
    """プロンプト生成サービスのテストケース"""

    def setup_method(self):
        """各テストメソッドの前に実行"""
        self.service = PromptGenerationService()

    def test_基本的なプロンプト生成(self):
        """ユーザー入力から基本的なプロンプトを生成できることを検証"""
        # Arrange
        user_input = UserInput(
            goal="商品レビューの要約生成",
            context="ECサイトのレビューを購入検討者向けに要約",
            constraints=["最大200文字", "中立的な視点"],
            examples=["良い点：品質が高い、悪い点：価格が高い"],
        )

        # Act
        prompt_content = self.service.generate_prompt(user_input)

        # Assert
        assert isinstance(prompt_content, PromptContent)
        assert prompt_content.template is not None
        assert len(prompt_content.template) > 0
        assert prompt_content.system_message is not None
        assert "商品レビュー" in prompt_content.template or "レビュー" in prompt_content.template

    def test_制約条件の反映(self):
        """制約条件がプロンプトに反映されることを検証"""
        # Arrange
        user_input = UserInput(
            goal="メール返信の生成",
            context="カスタマーサポート",
            constraints=["丁寧語を使用", "100文字以内", "ポジティブなトーン"],
            examples=[],
        )

        # Act
        prompt_content = self.service.generate_prompt(user_input)

        # Assert
        assert "丁寧" in prompt_content.template or "敬語" in prompt_content.template
        assert "100文字" in prompt_content.template or "文字数" in prompt_content.template
        assert "ポジティブ" in prompt_content.template or "前向き" in prompt_content.template

    def test_例の組み込み(self):
        """提供された例がプロンプトに組み込まれることを検証"""
        # Arrange
        user_input = UserInput(
            goal="FAQ回答生成",
            context="製品サポート",
            constraints=[],
            examples=["Q: 返品可能ですか？ A: はい、30日以内なら可能です", "Q: 送料は？ A: 5000円以上で無料です"],
        )

        # Act
        prompt_content = self.service.generate_prompt(user_input)

        # Assert
        # テンプレートまたはシステムメッセージに例が含まれていることを確認
        combined_text = prompt_content.template + (prompt_content.system_message or "")
        assert "例" in combined_text or "Example" in combined_text.lower()

    def test_変数の自動検出(self):
        """プロンプトテンプレートから変数が自動検出されることを検証"""
        # Arrange
        user_input = UserInput(
            goal="製品説明文の生成",
            context="ECサイトの商品ページ",
            constraints=["SEOキーワードを含める"],
            examples=[],
        )

        # Act
        prompt_content = self.service.generate_prompt(user_input)

        # Assert
        assert prompt_content.variables is not None
        assert len(prompt_content.variables) > 0
        # 生成されたテンプレートに変数プレースホルダーが含まれている
        for var in prompt_content.variables:
            assert f"{{{var}}}" in prompt_content.template

    def test_OpenAI向け最適化(self):
        """OpenAI APIに最適化されたプロンプトが生成されることを検証"""
        # Arrange
        user_input = UserInput(
            goal="コード生成",
            context="Python関数の実装",
            constraints=["型ヒント付き", "docstring付き"],
            examples=[],
        )

        # Act
        prompt_content = self.service.generate_prompt_for_openai(user_input)

        # Assert
        assert prompt_content.system_message is not None
        assert len(prompt_content.system_message) > 0
        # OpenAIのベストプラクティスに従った構造
        assert prompt_content.template is not None

    def test_空の制約条件でも動作(self):
        """制約条件が空でも正常に動作することを検証"""
        # Arrange
        user_input = UserInput(
            goal="シンプルなテキスト生成", context="一般的な用途", constraints=[], examples=[]
        )

        # Act
        prompt_content = self.service.generate_prompt(user_input)

        # Assert
        assert prompt_content is not None
        assert prompt_content.template is not None
        assert len(prompt_content.template) > 0

    def test_プロンプト改善提案(self):
        """既存プロンプトの改善提案ができることを検証"""
        # Arrange
        original_content = PromptContent(
            template="レビューを要約してください: {review}",
            variables=["review"],
            system_message="要約を作成します",
        )
        user_feedback = "もっと具体的な指示が欲しい"

        # Act
        improved_content = self.service.improve_prompt(original_content, user_feedback)

        # Assert
        assert improved_content is not None
        assert improved_content != original_content
        assert len(improved_content.template) >= len(original_content.template)

    def test_プロンプトの検証(self):
        """生成されたプロンプトが有効であることを検証"""
        # Arrange
        user_input = UserInput(
            goal="テストプロンプト", context="検証用", constraints=["テスト制約"], examples=[]
        )

        # Act
        prompt_content = self.service.generate_prompt(user_input)
        is_valid = self.service.validate_prompt(prompt_content)

        # Assert
        assert is_valid is True

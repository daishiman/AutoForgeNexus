"""
プロンプト生成サービス

ユーザー入力からプロンプトを生成するドメインサービス。
OpenAI向けに最適化されたプロンプトの生成を行います。
"""
import re
from typing import List, Optional
from src.domain.prompt.value_objects.user_input import UserInput
from src.domain.prompt.value_objects.prompt_content import PromptContent


class PromptGenerationService:
    """
    プロンプト生成のビジネスロジックを実装するドメインサービス

    ユーザーの入力を分析し、効果的なプロンプトを生成します。
    OpenAI APIのベストプラクティスに従った構造化を行います。
    """

    def generate_prompt(self, user_input: UserInput) -> PromptContent:
        """
        ユーザー入力から基本的なプロンプトを生成

        Args:
            user_input: ユーザーからの入力

        Returns:
            生成されたプロンプトコンテンツ
        """
        # テンプレート生成
        template = self._build_template(user_input)

        # 変数の抽出
        variables = self._extract_template_variables(template)

        # システムメッセージ生成
        system_message = self._build_system_message(user_input)

        return PromptContent(
            template=template, variables=variables, system_message=system_message
        )

    def generate_prompt_for_openai(self, user_input: UserInput) -> PromptContent:
        """
        OpenAI API向けに最適化されたプロンプトを生成

        Args:
            user_input: ユーザーからの入力

        Returns:
            OpenAI向けに最適化されたプロンプトコンテンツ
        """
        # OpenAIのベストプラクティスに従ったシステムメッセージ
        system_message = self._build_openai_system_message(user_input)

        # 構造化されたテンプレート
        template = self._build_structured_template(user_input)

        # 変数の抽出
        variables = self._extract_template_variables(template)

        return PromptContent(
            template=template, variables=variables, system_message=system_message
        )

    def improve_prompt(
        self, original_content: PromptContent, user_feedback: str
    ) -> PromptContent:
        """
        既存プロンプトの改善提案

        Args:
            original_content: 元のプロンプトコンテンツ
            user_feedback: ユーザーからのフィードバック

        Returns:
            改善されたプロンプトコンテンツ
        """
        # フィードバックに基づいて改善
        improved_template = self._improve_template(
            original_content.template, user_feedback
        )

        # 変数の再抽出
        variables = self._extract_template_variables(improved_template)

        # システムメッセージも改善
        improved_system = self._improve_system_message(
            original_content.system_message, user_feedback
        )

        return PromptContent(
            template=improved_template,
            variables=variables,
            system_message=improved_system,
        )

    def validate_prompt(self, prompt_content: PromptContent) -> bool:
        """
        生成されたプロンプトの妥当性を検証

        Args:
            prompt_content: 検証するプロンプトコンテンツ

        Returns:
            有効な場合True
        """
        # テンプレートが存在し、最小限の長さがあるか
        if not prompt_content.template or len(prompt_content.template) < 10:
            return False

        # 変数とテンプレートの整合性
        template_vars = set(re.findall(r"\{(\w+)\}", prompt_content.template))
        if template_vars != set(prompt_content.variables):
            return False

        return True

    def _build_template(self, user_input: UserInput) -> str:
        """基本的なテンプレートを構築"""
        parts = []

        # ゴールを明確に記述
        parts.append(f"目的: {user_input.goal}")

        # コンテキストがある場合は追加
        if user_input.context:
            parts.append(f"背景: {user_input.context}")

        # 制約条件を列挙
        if user_input.constraints:
            parts.append("以下の条件を満たしてください:")
            for constraint in user_input.constraints:
                parts.append(f"- {constraint}")

        # 例がある場合は追加
        if user_input.examples:
            parts.append("\n例:")
            for example in user_input.examples:
                parts.append(f"- {example}")

        # 入力プレースホルダー
        parts.append("\n入力内容: {input}")
        parts.append("\n回答:")

        return "\n".join(parts)

    def _build_structured_template(self, user_input: UserInput) -> str:
        """構造化されたテンプレートを構築（OpenAI向け）"""
        parts = []

        # タスクの明確な定義
        parts.append("# タスク")
        parts.append(user_input.goal)

        # コンテキストセクション
        if user_input.context:
            parts.append("\n# コンテキスト")
            parts.append(user_input.context)

        # 要件セクション
        if user_input.constraints:
            parts.append("\n# 要件")
            for i, constraint in enumerate(user_input.constraints, 1):
                parts.append(f"{i}. {constraint}")

        # 例示セクション
        if user_input.examples:
            parts.append("\n# 参考例")
            for example in user_input.examples:
                parts.append(f"- {example}")

        # 入力と出力の明確な区別
        parts.append("\n# 入力")
        parts.append("{input}")

        parts.append("\n# 出力")
        parts.append("以下に回答を記述します:")

        return "\n".join(parts)

    def _build_system_message(self, user_input: UserInput) -> str:
        """システムメッセージを生成"""
        message = f"あなたは{user_input.goal}を支援する専門的なアシスタントです。"

        if user_input.context:
            message += f" {user_input.context}の文脈で動作します。"

        if user_input.constraints:
            message += " ユーザーの要求に対して、指定された条件を厳密に守って回答してください。"

        return message

    def _build_openai_system_message(self, user_input: UserInput) -> str:
        """OpenAI向けに最適化されたシステムメッセージ"""
        parts = []

        # 役割の明確な定義
        parts.append(f"あなたは{user_input.goal}の専門家です。")

        # 専門知識の強調
        if "コード" in user_input.goal or "プログラ" in user_input.goal:
            parts.append("プログラミングのベストプラクティスに精通しています。")
        elif "レビュー" in user_input.goal or "要約" in user_input.goal:
            parts.append("情報の分析と要約に優れた能力を持っています。")
        elif "サポート" in user_input.goal or "カスタマー" in user_input.goal:
            parts.append("顧客対応において丁寧で親切な対応を心がけています。")

        # 制約への言及
        if user_input.constraints:
            parts.append("回答時は常に指定された要件を満たすよう注意を払います。")

        return " ".join(parts)

    def _extract_template_variables(self, template: str) -> List[str]:
        """テンプレートから変数を抽出"""
        variables = re.findall(r"\{(\w+)\}", template)
        return list(set(variables))

    def _improve_template(self, template: str, feedback: str) -> str:
        """フィードバックに基づいてテンプレートを改善"""
        improved = template

        # "もっと具体的" というフィードバックへの対応
        if "具体的" in feedback:
            # より具体的な指示を追加
            if "要約" in template:
                improved = template.replace(
                    "要約してください", "以下の観点で具体的に要約してください:\n1. 主要なポイント\n2. 長所と短所\n3. 総合的な評価"
                )
            else:
                improved = improved.replace(":", "について具体的に:")

        # "簡潔に" というフィードバックへの対応
        elif "簡潔" in feedback or "短く" in feedback:
            improved = improved.replace("以下に回答を記述します:", "簡潔に回答:")

        # "例を増やして" というフィードバックへの対応
        elif "例" in feedback:
            if "参考例" not in improved:
                improved += "\n\n# 参考例\n具体的な例を以下に示します:"

        return improved

    def _improve_system_message(
        self, system_message: Optional[str], feedback: str
    ) -> str:
        """フィードバックに基づいてシステムメッセージを改善"""
        if not system_message:
            return "改善されたアシスタントです。"

        improved = system_message

        # トーンの調整
        if "丁寧" in feedback:
            improved += " 常に丁寧で礼儀正しい言葉遣いを心がけます。"
        elif "カジュアル" in feedback:
            improved += " フレンドリーで親しみやすい対応を心がけます。"

        return improved

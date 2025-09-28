"""
UserInput値オブジェクト

ユーザーからの入力を表現する不変の値オブジェクト。
プロンプト生成の入力として使用されます。
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class UserInput:
    """
    ユーザー入力を表現する値オブジェクト

    Attributes:
        goal: プロンプトで達成したい目的
        context: プロンプトが使用される文脈
        constraints: プロンプトに適用する制約条件
        examples: 参考となる例
    """

    goal: str
    context: str
    constraints: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)

    def __post_init__(self):
        """初期化後のバリデーション"""
        if not self.goal or not self.goal.strip():
            raise ValueError("ゴールは必須です")

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "goal": self.goal,
            "context": self.context,
            "constraints": self.constraints,
            "examples": self.examples,
        }

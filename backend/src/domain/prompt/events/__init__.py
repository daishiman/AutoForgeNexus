"""
プロンプト集約のドメインイベント

プロンプトのライフサイクルで発生するすべてのイベント
"""
from .prompt_created import PromptCreatedEvent
from .prompt_saved import PromptSavedEvent
from .prompt_updated import PromptUpdatedEvent

__all__ = [
    "PromptCreatedEvent",
    "PromptSavedEvent",
    "PromptUpdatedEvent",
]

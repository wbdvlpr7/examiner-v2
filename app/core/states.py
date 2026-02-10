from enum import IntEnum

class ConversationState(IntEnum):
    SELECTING_EXAM = 0
    SELECTING_SKILL = 1
    SELECTING_MODE = 2
    AWAITING_INPUT = 3
    IN_PARAPHRASE_LOOP = 10
    IN_VOCAB_LOOP = 11
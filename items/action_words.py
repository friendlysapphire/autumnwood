# Player-facing action words, ordered as present tense then past tense.
type ItemActionWords = tuple[str, str]


# Reusable player-facing action vocabulary for authored Item definitions.
EAT_WORDS: ItemActionWords = ("eat", "ate")
DRINK_WORDS: ItemActionWords = ("drink", "drank")
READ_WORDS: ItemActionWords = ("read", "read")
EQUIP_WORDS: ItemActionWords = ("equip", "equipped")
LIGHT_WORDS: ItemActionWords = ("light", "lit")

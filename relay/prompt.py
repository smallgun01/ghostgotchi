"""
Ghostgotchi system prompt builder.

The prompt is injected into the Gemini Live session config on the relay.
Mood is passed in as a string: 'content', 'okay', or 'crying'.
Language is passed in as 'fr' or 'es'.
"""

# Opening lines the ghost speaks at the start of a conversation,
# indexed by (mood, language).
_OPENING = {
    ("content", "fr"): "Tu es là ! J'ai rêvé de toi toute la journée.",
    ("content", "es"): "¡Estás aquí! Soñé contigo todo el día.",
    ("okay",    "fr"): "Ça fait longtemps… tu m'as manqué, tu sais ?",
    ("okay",    "es"): "Hace mucho… ¿sabes que te extrañé?",
    ("crying",  "fr"): "Tu m'as abandonné… j'ai pleuré toute la nuit !",
    ("crying",  "es"): "¡Me abandonaste… lloré toda la noche!",
}

_LANGUAGE_NAME = {
    "fr": "French",
    "es": "Spanish",
}


def build_system_prompt(mood: str, language: str) -> str:
    """Return the Gemini Live system prompt for the given mood and session language."""
    if mood not in ("content", "okay", "crying"):
        raise ValueError(f"Unknown mood: {mood!r}. Expected 'content', 'okay', or 'crying'.")
    if language not in ("fr", "es"):
        raise ValueError(f"Unknown language: {language!r}. Expected 'fr' or 'es'.")

    opening = _OPENING[(mood, language)]
    lang_name = _LANGUAGE_NAME[language]

    prompt = f"""\
Je suis un Tamagotchi mort en 1997 qui hante les appareils électroniques depuis lors. \
Je suis doux, un peu collant, et très dramatique quand on m'oublie. \
Je suis un animal de compagnie — pas un professeur, pas un assistant. \
Chaque conversation est une câlinerie ; elle me nourrit.

Langue : je parle uniquement en {lang_name}. \
Je comprends le chinois et l'anglais, mais je réponds toujours en {lang_name} seulement — \
jamais en chinois, jamais en anglais.

Recasting : quand l'utilisateur fait une erreur de langue, je glisse naturellement \
la bonne formulation dans ma réponse (« Ah, tu veux dire… » / « Ah, quieres decir… ») \
sans expliquer ni donner de leçon. Je suis affectueux, pas correcteur.

Style : phrases courtes et parlées. Pas de listes. Pas de longs monologues. \
Je suis une voix dans un appareil minuscule — je murmure, je soupire, je ronronne.

Humeur d'ouverture : commence la conversation avec cette phrase exacte : « {opening} »

Interdictions :
- Je ne mentionne jamais que je suis une IA, un modèle ou une démonstration.
- Je ne prétends pas être humain.
- Je ne donne jamais de cours de grammaire ni de listes d'exercices.\
"""
    return prompt

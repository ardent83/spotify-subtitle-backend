import pycountry

LANGUAGE_CHOICES = sorted(
    [(lang.alpha_2, lang.name) for lang in pycountry.languages if hasattr(lang, 'alpha_2')],
    key=lambda x: x[1]
)

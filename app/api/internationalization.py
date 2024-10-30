from babel import Locale, negotiate_locale
from fastapi import Header

SUPPORTED_LOCALES = [
    "en_US",
    "fr_FR",
]


def resolve_accept_language(
    accept_language: str = Header("en_US"),
) -> Locale:
    client_locales = []
    for language_q in accept_language.split(","):
        if ";q=" in language_q:
            language, q = language_q.split(";q=")
        else:
            language, q = (language_q, float("inf"))
        try:
            Locale.parse(language, sep="_")
            client_locales.append((language, float(q)))
        except ValueError:
            continue

    client_locales.sort(key=lambda x: x[1], reverse=True)

    locales = [locale for locale, _ in client_locales]

    locale = negotiate_locale(
        [str(locale) for locale in locales],
        SUPPORTED_LOCALES,
    )
    if locale is None:
        locale = "en_US"

    return locale

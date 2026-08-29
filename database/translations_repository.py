"""
MONJED Translations Repository

Stores approved deterministic translations
used by MONJED communication layers.

IMPORTANT:
- Does NOT use generative AI.
- Does NOT modify decisions.
- Does NOT modify risk.
- Each translation key + language pair must be unique.
"""


from datetime import datetime, timezone

from database.connection import get_database


# ============================================================
# COLLECTION
# ============================================================


def get_translations_collection():
    """
    Return translations collection safely.
    """

    return get_database()["translations"]


# ============================================================
# CREATE
# ============================================================


def create_translation(
    key: str,
    language: str,
    text: str,
):
    """
    Create one approved translation.
    """

    key = str(key).strip()
    language = str(language).strip().lower()
    text = str(text).strip()


    if not key:
        raise ValueError(
            "Translation key is required."
        )


    if not language:
        raise ValueError(
            "Translation language is required."
        )


    if not text:
        raise ValueError(
            "Translation text is required."
        )


    translation = {

        "key":
            key,

        "language":
            language,

        "text":
            text,

        "created_at":
            datetime.now(
                timezone.utc
            ),

        "updated_at":
            datetime.now(
                timezone.utc
            ),
    }


    collection = get_translations_collection()


    result = collection.insert_one(
        translation
    )


    return collection.find_one(
        {
            "_id":
                result.inserted_id
        }
    )


# ============================================================
# GET
# ============================================================


def get_translation(
    key: str,
    language: str,
):
    """
    Return one translation by key and language.
    """

    key = str(key).strip()
    language = str(language).strip().lower()


    if not key or not language:
        return None


    return get_translations_collection().find_one(
        {
            "key":
                key,

            "language":
                language,
        }
    )


# ============================================================
# GET BY LANGUAGE
# ============================================================


def get_translations_by_language(
    language: str,
):
    """
    Return all translations for one language.
    """

    language = str(
        language
    ).strip().lower()


    if not language:
        return []


    return list(
        get_translations_collection()
        .find(
            {
                "language":
                    language
            }
        )
        .sort(
            "key",
            1,
        )
    )


# ============================================================
# UPDATE
# ============================================================


def update_translation(
    key: str,
    language: str,
    text: str,
):
    """
    Update one approved translation.
    """

    key = str(key).strip()
    language = str(language).strip().lower()
    text = str(text).strip()


    if not key:
        raise ValueError(
            "Translation key is required."
        )


    if not language:
        raise ValueError(
            "Translation language is required."
        )


    if not text:
        raise ValueError(
            "Translation text is required."
        )


    get_translations_collection().update_one(

        {
            "key":
                key,

            "language":
                language,
        },

        {
            "$set": {

                "text":
                    text,

                "updated_at":
                    datetime.now(
                        timezone.utc
                    ),
            }
        },
    )


    return get_translation(
        key,
        language,
    )


# ============================================================
# DELETE
# ============================================================


def delete_translation(
    key: str,
    language: str,
) -> int:
    """
    Delete one translation.

    Returns number of deleted documents.
    """

    key = str(key).strip()
    language = str(language).strip().lower()


    if not key or not language:
        return 0


    result = (
        get_translations_collection()
        .delete_one(
            {
                "key":
                    key,

                "language":
                    language,
            }
        )
    )


    return result.deleted_count
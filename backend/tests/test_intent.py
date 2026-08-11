"""Checks that only actual image-change requests are intercepted."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.intent import is_image_request

REFUSED = [
    "change la photo du formateur",
    "mets un autre logo",
    "remplace l'image du hero",
    "modifie la photo",
    "peux-tu changer le logo ?",
    "génère une nouvelle illustration",
]

ALLOWED = [
    # An image is only mentioned to locate a text block.
    "raccourcis le sous-titre sous la photo",
    "change le titre au-dessus de la photo",
    "reformule le texte à côté du visuel",
    # Words that merely contain a keyword.
    "parle d'imagerie médicale dans le programme",
    "ajoute un logotype au programme",
    "rends le titre plus percutant",
]


def main():
    for message in REFUSED:
        assert is_image_request(message), message
    for message in ALLOWED:
        assert not is_image_request(message), message
    print("image edit requests are detected, text edits mentioning an image are not: OK")


if __name__ == "__main__":
    main()

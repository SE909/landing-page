"""Requests the chatbot must refuse before reaching OpenAI.

The trainer photo and the logo are uploaded through `/api/upload`; they are not
part of `page_state`, so no edit can ever change them. Answering directly avoids
an OpenAI round trip that would, at best, rewrite an unrelated text.

Only a request to *change an image* is intercepted: mentioning one to locate a
text block ("raccourcis le sous-titre sous la photo") is a normal edit.
"""

import re

_VERB = r"(?:change|changer|remplace|remplacer|modifie|modifier|met|mets|mettre|ajoute|ajouter|supprime|supprimer|enl[eè]ve|enlever|upload|t[ée]l[ée]verse|g[ée]n[eè]re|g[ée]n[ée]rer)"
_IMAGE = r"(?:images?|photos?|avatars?|logos?|illustrations?|visuels?)"

# The verb must target the image, with at most a determiner/adjective in between.
IMAGE_EDIT_PATTERN = re.compile(rf"\b{_VERB}\b(?:[\s'’]+\w+){{0,3}}[\s'’]+{_IMAGE}\b")

IMAGE_REQUEST_REPLY = (
    "Je ne peux pas changer les images depuis le chat : la photo du formateur et le logo "
    "ne font pas partie du contenu éditable de la page. Utilisez l'upload d'image à l'étape "
    "« informations du formateur » du formulaire. Dites-moi en revanche quel texte vous "
    "souhaitez modifier et je m'en occupe."
)


def is_image_request(message: str) -> bool:
    return bool(IMAGE_EDIT_PATTERN.search(message.lower()))

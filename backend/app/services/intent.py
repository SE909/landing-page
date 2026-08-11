"""Requests the chatbot must refuse before reaching OpenAI.

The trainer photo and the logo are uploaded through `/api/upload`; they are not
part of `page_state`, so no edit can ever change them. Answering directly avoids
an OpenAI round trip that would, at best, rewrite an unrelated text.
"""

import re

IMAGE_PATTERN = re.compile(r"\b(image|images|photo|photos|avatar|logo|illustration|visuel)\b")

IMAGE_REQUEST_REPLY = (
    "Je ne peux pas changer les images depuis le chat : la photo du formateur et le logo "
    "ne font pas partie du contenu éditable de la page. Utilisez l'upload d'image à l'étape "
    "« informations du formateur » du formulaire."
)


def is_image_request(message: str) -> bool:
    return bool(IMAGE_PATTERN.search(message.lower()))

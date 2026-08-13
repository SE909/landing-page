from copy import deepcopy

TOOL_NAME = "add_section"
SECTION_NAMES = {"features", "benefits", "testimonials", "faq", "footer"}


def tool_definition() -> dict:
    return {
        "type": "function",
        "function": {
            "name": TOOL_NAME,
            "description": "Ajoute ou remplace le contenu d'une section optionnelle de la landing page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "section": {
                        "type": "string",
                        "enum": sorted(SECTION_NAMES),
                        "description": "Section à ajouter.",
                    },
                    "content": {
                        "type": ["object", "array"],
                        "description": "Contenu structuré de la section demandée.",
                    },
                },
                "required": ["section", "content"],
                "additionalProperties": False,
            },
        },
    }


def validate(arguments: dict) -> bool:
    return (
        isinstance(arguments, dict)
        and set(arguments) == {"section", "content"}
        and arguments.get("section") in SECTION_NAMES
        and isinstance(arguments.get("content"), (dict, list))
        and bool(arguments["content"])
    )


def apply(page_state: dict, arguments: dict) -> dict:
    if not validate(arguments):
        return page_state
    updated = deepcopy(page_state)
    updated[arguments["section"]] = deepcopy(arguments["content"])
    return updated


def execute(page_state: dict, arguments: dict) -> dict:
    if not validate(arguments):
        return {
            "ok": False,
            "error": "La section demandée est inconnue ou son contenu est vide. Les sections possibles sont features, benefits, testimonials, faq et footer.",
        }

    section = arguments["section"]
    return {
        "ok": True,
        "page_state": apply(page_state, arguments),
        "changes": {section: arguments["content"]},
        "summary": f"La section {section} a été ajoutée.",
    }

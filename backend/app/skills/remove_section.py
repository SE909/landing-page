from copy import deepcopy

TOOL_NAME = "remove_section"
SECTION_NAMES = {"features", "benefits", "testimonials", "faq", "footer"}


def tool_definition() -> dict:
    return {
        "type": "function",
        "function": {
            "name": TOOL_NAME,
            "description": "Supprime une section optionnelle de la landing page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "section": {
                        "type": "string",
                        "enum": sorted(SECTION_NAMES),
                        "description": "Section à supprimer.",
                    },
                },
                "required": ["section"],
                "additionalProperties": False,
            },
        },
    }


def validate(arguments: dict) -> bool:
    return isinstance(arguments, dict) and set(arguments) == {"section"} and arguments.get("section") in SECTION_NAMES


def apply(page_state: dict, arguments: dict) -> dict:
    if not validate(arguments):
        return page_state
    updated = deepcopy(page_state)
    updated[arguments["section"]] = []
    return updated


def execute(page_state: dict, arguments: dict) -> dict:
    if not validate(arguments):
        return {
            "ok": False,
            "error": "La section demandée est inconnue. Les sections supprimables sont features, benefits, testimonials, faq et footer.",
        }

    section = arguments["section"]
    if not page_state.get(section):
        return {"ok": False, "error": f"La section {section} n'est pas présente sur cette landing page."}

    return {
        "ok": True,
        "page_state": apply(page_state, arguments),
        "changes": {section: []},
        "summary": f"La section {section} a été supprimée.",
    }

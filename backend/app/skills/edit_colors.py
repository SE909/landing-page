from copy import deepcopy
import re

TOOL_NAME = "edit_colors"
ALLOWED_FIELDS = {"primary_color", "secondary_color"}
HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")


def tool_definition() -> dict:
    return {
        "type": "function",
        "function": {
            "name": TOOL_NAME,
            "description": "Modifie les deux couleurs principales de la landing page. Utiliser des couleurs hexadécimales au format #RRGGBB.",
            "parameters": {
                "type": "object",
                "properties": {
                    "primary_color": {"type": "string", "description": "Couleur principale au format #RRGGBB."},
                    "secondary_color": {"type": "string", "description": "Couleur secondaire au format #RRGGBB."},
                },
                "additionalProperties": False,
            },
        },
    }


def validate(changes: dict) -> bool:
    return (
        isinstance(changes, dict)
        and bool(changes)
        and set(changes).issubset(ALLOWED_FIELDS)
        and all(isinstance(value, str) and HEX_COLOR.fullmatch(value.strip()) for value in changes.values())
    )


def apply(page_state: dict, changes: dict) -> dict:
    if not validate(changes):
        return page_state
    updated = deepcopy(page_state)
    branding = dict(updated.get("branding", {}))
    branding.update({key: value.strip().upper() for key, value in changes.items()})
    updated["branding"] = branding
    return updated


def execute(page_state: dict, arguments: dict) -> dict:
    if not validate(arguments):
        return {
            "ok": False,
            "error": "Les couleurs doivent être au format hexadécimal #RRGGBB, par exemple #2563EB.",
        }

    changes = {key: value.strip().upper() for key, value in arguments.items()}
    return {
        "ok": True,
        "page_state": apply(page_state, changes),
        "changes": {"branding": changes},
        "summary": "La palette de couleurs a été mise à jour.",
    }

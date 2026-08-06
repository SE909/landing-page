from fastapi import APIRouter

router = APIRouter(prefix="/api/templates", tags=["templates"])

@router.get("")
async def get_templates():
    return [
        {
            "id": "formation-default",
            "name": "Template Supervisor Formation",
            "description": "Template optimisé avec Hero, Problème/Solution, Programme, Preuve Sociale, Prix et Formateur.",
            "category": "Formation"
        }
    ]

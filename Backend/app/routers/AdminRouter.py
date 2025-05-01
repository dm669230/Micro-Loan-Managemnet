from fastapi import APIRouter

router = APIRouter()

@router.get("/admin")
def admin_action():
    return "hi this is admin page !"

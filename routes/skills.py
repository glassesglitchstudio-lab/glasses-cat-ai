from fastapi import APIRouter, HTTPException

router = APIRouter()

def get_skill_manager():
    try:
        from skill_system import SkillManager
        return SkillManager.get_instance()
    except:
        return None

@router.get("")
async def list_skills():
    """Tüm skill'leri listele"""
    sm = get_skill_manager()
    if not sm:
        return {"success": False, "error": "Skill sistemi yüklü değil", "skills": [], "enabled": []}
    try:
        all_skills = sm.get_all_skills()
        enabled = sm.get_enabled_skills()
        skills_list = [s.to_dict() for s in all_skills.values()]
        enabled_names = list(enabled.keys())
        return {"success": True, "skills": skills_list, "enabled": enabled_names}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/{name}/toggle")
async def toggle_skill(name: str):
    """Skill'i aç/kapa"""
    sm = get_skill_manager()
    if not sm:
        raise HTTPException(status_code=501, detail="Skill sistemi yüklü değil")
    try:
        sm.toggle_skill(name)
        is_enabled = sm.is_skill_enabled(name)
        return {"success": True, "enabled": is_enabled}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

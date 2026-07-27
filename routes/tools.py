from fastapi import APIRouter

router = APIRouter()

def get_toolformer():
    try:
        from toolformer import Toolformer
        return Toolformer()
    except:
        return None

@router.get("")
async def list_tools():
    """Tüm araçları listele"""
    tf = get_toolformer()
    if not tf:
        return {"success": False, "error": "Toolformer yüklü değil", "tools": []}
    try:
        tools = tf.list_tools()
        return {"success": True, "tools": tools}
    except Exception as e:
        return {"success": False, "error": str(e)}

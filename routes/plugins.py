from fastapi import APIRouter, HTTPException

router = APIRouter()

def get_plugin_manager():
    try:
        from plugin_system import PluginManager
        pm = PluginManager.get_instance()
        if pm:
            pm.discover_plugins()
            pm.load_all_plugins()
        return pm
    except:
        return None

@router.get("")
async def list_plugins():
    """Tüm pluginleri listele"""
    pm = get_plugin_manager()
    if not pm:
        return {"success": False, "error": "Plugin sistemi yüklü değil", "plugins": [], "active": []}
    try:
        names = pm.get_plugin_names()
        active_names = [p.name for p in pm.get_active_plugins()]
        plugins_data = []
        for name in names:
            p = pm.get_plugin(name)
            if p:
                meta = p.metadata
                is_active = p.is_enabled if hasattr(p, 'is_enabled') else (p.state == 'enabled' or p.name in active_names)
                plugins_data.append({
                    "name": meta.name if hasattr(meta, 'name') else name,
                    "description": meta.description if hasattr(meta, 'description') else "",
                    "version": meta.version if hasattr(meta, 'version') else "1.0",
                    "enabled": is_active,
                    "status": "enabled" if is_active else "disabled",
                    "metadata": {
                        "name": meta.name if hasattr(meta, 'name') else name,
                        "description": meta.description if hasattr(meta, 'description') else "",
                        "version": meta.version if hasattr(meta, 'version') else "1.0",
                        "author": meta.author if hasattr(meta, 'author') else "",
                        "tags": meta.tags if hasattr(meta, 'tags') else [],
                    }
                })
        return {
            "success": True,
            "plugins": plugins_data,
            "active": active_names,
            "status": f"Sistem: PluginManager v1.0 · {len(plugins_data)} eklenti"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/{name}/toggle")
async def toggle_plugin(name: str):
    """Plugin'i aç/kapa"""
    pm = get_plugin_manager()
    if not pm:
        raise HTTPException(status_code=501, detail="Plugin sistemi yüklü değil")
    try:
        plugin = pm.get_plugin(name)
        if not plugin:
            raise HTTPException(status_code=404, detail=f"Plugin '{name}' bulunamadı")
        if plugin.is_enabled:
            ok = pm.disable_plugin(name)
        else:
            ok = pm.enable_plugin(name)
        return {"success": ok, "enabled": plugin.is_enabled}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

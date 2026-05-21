# V5_Ultra_Agent - glassesglitchstudio/gulmzcetiner:V5

**Glassesglitch Studio / GlassesSoftware** — Kurucu: Berkay Patron

## Yenilikler

### V5 Ultra Agent (21 Mayis 2026)

1. **NEXUS MOTOR**: Pollinations.ai Flux ile yazidan gorsele
2. **SIBER AJAN**: subprocess/os tabanli sistem komut motoru
3. **GEMINI VISYON**: Minimalist mavi yildizli kullanici arayuzu
4. **PATRON LOGLAMA**: Tum mesajlar Turkce, siber temali, Berkay Patron'a hitaben
5. **OBSIDIAN HAFIZA**: Sinirsiz .md tabanli uzun sureli bellek

### Mimari

Bu model **Qwen 2.5 Coder 14B** kodlama yetenekleri ile **Google Gemma 4** muhakeme gucunun birlesiminden olusturulmustur (hybrid architecture).

V5_Ultra_Agent combines Qwen 2.5 Coder 14B's coding capabilities with Google Gemma 4's reasoning power in a hybrid architecture.

### Teknik Parametreler

| Parametre | Deger |
|-----------|-------|
| temperature | 0.6 |
| top_p | 0.80 |
| top_k | 30 |
| num_ctx | 16384 |
| num_predict | 2048 |
| repeat_penalty | 1.1 |

### Kullanim

```bash
# CLI ile calistirma
python glasses_vibe.py

# Ollama dogrudan
ollama run glassesglitchstudio/gulmzcetiner:V5

# Python'dan gorsel uretme
from glasses_vibe import v5_gorsel_olustur
v5_gorsel_olustur("bir kedi")

# Python'dan siber komut
from glasses_vibe import v5_siber_komut
v5_siber_komut("echo merhaba")
```

---

**Architecture**: Qwen 2.5 Coder 14B + Google Gemma 4 Hybrid
**Lisans**: Apache License 2.0

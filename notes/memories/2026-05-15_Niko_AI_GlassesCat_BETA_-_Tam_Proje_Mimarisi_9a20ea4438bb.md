---
title: "Glassescat AI GlassesCat BETA - Tam Proje Mimarisi"
memory_id: "9a20ea4438bb"
created: 2026-05-15T17:45:36.333447
modified: 2026-05-15T17:45:36.333447
type: memory
date: 2026-05-15
tags:
  - proje
  - mimari
  - niko-ai
  - glassescat
  - SWA-1.6
  - ollama
  - local-ai
  - desktop-assistant
aliases: ["proje", "mimari", "niko-ai"]
cssclass: memory-note
---

# 💭 Glassescat AI GlassesCat BETA - Tam Proje Mimarisi

**Oluşturulma:** 2026-05-15 17:45:36
**ID:** `9a20ea4438bb`

---

# Glassescat AI / GlassesCat BETA - Proje Ozeti

## Kimlik
Glassescat AI (kod adi: GlassesCat BETA, Mimari: SWA 1.6) - Jarvis/Hermes ilhamli evrensel sistem ajani ve kisisel masaustu AI asistani.

## Temel Yetenekler
- Yerel LLM cikarimi (Ollama ile tamamen offline)
- Otonom kod uretimi ve guvenli calistirma
- Masaustu otomasyonu ve dosya yonetimi
- Web arama entegrasyonu
- RAG bilgi erisimi (PDF, TXT, MD, HTML, CSV)
- Plugin/Skill genisletilebilirlik sistemi
- Godot oyun fabrikasi (otomatik oyun uretimi)
- Vision/OCR (LLaVA)
- Text-to-Speech (gTTS)
- Gorev zamanlama (APScheduler)

## AI Model Yonlendirme
- llama3.1: Genel konusma, muhakeme
- llama3.2: Hizli/hafif chat
- qwen2.5-coder:14b: Kod uretimi, debug
- deepseek-r1:8b: Matematik, mantik, analiz
- llava: Vision, OCR, gorsel anlama

## Ana Moduller
- main.py: FastAPI backend
- server.py: Flask backend
- niko_agent.py: Cekirdek ajan mantigi
- niko_ai_engine.py: AI motoru
- glassescat_engine.py: Ozel motor
- niko_gui.py: Masaustu UI (CustomTkinter)
- niko_factory.py: Godot oyun fabrikasi
- memory.py + obsidian_memory.py: Hafiza sistemi
- model_router.py: Model yonlendirme
- rag_system.py: RAG pipeline
- plugin_system.py + skill_system.py: Genisletilebilirlik
- toolformer.py + tools.py: Tool calling
- code_sandbox.py: Guvenli kod calistirma
- code_agent.py: Kod ajani
- vision.py: Gorsel anlama
- tts.py: Ses sentezi
- web_search.py: Web arama
- task_scheduler.py: Gorev zamanlama
- terminal.py: Terminal emulasyonu
- command_parser.py: Komut ayristirma
- file_ops.py: Dosya islemleri
- actions.py: Aksiyon tanimlari
- conversation_summarizer.py: Konusma ozetleme
- utils.py: Yardimci fonksiyonlar

## UI Sistemleri
- Masaustu: CustomTkinter (glassmorphism tasarim)
- Web: Vanilla HTML/CSS/JS + Flask/FastAPI

## Guvenlik
- Sandbox kod calistirma
- Modul izin listesi
- Yasakli pattern engelleme
- Calistirma zaman asimi
- Kaynak kisitlamalari

## Teknoloji Yigini
Backend: FastAPI, Flask
AI: Ollama (yerel modeller)
UI: CustomTkinter, HTML/CSS/JS
Hafiza: Obsidian Markdown vault
RAG: sentence-transformers + FAISS
Zamanlama: APScheduler
TTS: gTTS + pygame


---
## 🔗 İlgili Bağlantılar
- [[daily/2026-05-15|📅 Günlük Not - 2026-05-15]]

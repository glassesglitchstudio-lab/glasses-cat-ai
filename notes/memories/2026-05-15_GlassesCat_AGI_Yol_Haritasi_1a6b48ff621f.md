---
title: "GlassesCat AGI Yol Haritasi"
memory_id: "1a6b48ff621f"
created: 2026-05-15T21:20:01.534648
modified: 2026-05-15T21:20:01.534648
type: memory
date: 2026-05-15
tags:
  - agi
  - glasses-cat
  - yol-haritasi
  - plan
  - deepseek
aliases: ["agi", "glasses-cat", "yol-haritasi"]
cssclass: memory-note
---

# 💭 GlassesCat AGI Yol Haritasi

**Oluşturulma:** 2026-05-15 21:20:01
**ID:** `1a6b48ff621f`

---

# GlassesCat AGI Geliştirme Planı

## Mevcut Durum (v1.0)
- ErrorFix Engine (otomatik hata düzeltme)
- WebSocket real-time iletişim
- Godot entegrasyonu
- Intent Parser ([G]ame, [A]gent, [S]ystem)
- Obsidian Memory (sınırsız hafıza)
- NikoFactory (Godot proje üretimi)

## AGI İçin Eksikler
1. Multi-Model Router (DeepSeek + Qwen + Ollama)
2. Self-Evaluation (öz-değerlendirme)
3. Learning Loop (deneyimlerden öğrenme)
4. Multi-Agent Orkestrasyonu
5. Strategic Planning (görev parçalama)

## Geliştirme Adımları (Öncelik Sırası)

### 1. DeepSeek V4 Flash API Entegrasyonu (~30dk)
- glassescat_deepseek.py oluştur
- API client + error handling
- Streaming support

### 2. Multi-Model Router (~45dk)
- DeepSeek V4 → Ana düşünme, analiz, planlama
- Qwen 14B → Kod üretme
- Ollama Local → Hızlı yanıtlar
- Akıllı routing: görev tipine göre model seç

### 3. Self-Evaluation Sistemi (~30dk)
- Çıktı kalitesini değerlendir (0-1 skor)
- "Bu çözüm doğru mu?" self-check
- Düşük skor → tekrar dene

### 4. Learning Loop + Obsidian (~45dk)
- Başarılı/başarısız deneyimleri kaydet
- Benzer durumlarda geçmiş deneyimleri kullan
- Experience replay mechanism

### 5. Multi-Agent Orkestrasyonu (~1saat)
- CodeAgent, DebugAgent, DesignAgent
- CoordinatorAgent (koordinasyon)
- Agent arası iletişim

## Mimari
Kullanıcı → IntentParse → Model Router → Execution → Self-Eval → Obsidian Memory

## Notlar
- DeepSeek V4 Flash API key durumu kontrol edilecek
- Mock/placeholder ile başlayıp gerçek API bağlanabilir
- Her adım sonrası test yapılacak


---
## 🔗 İlgili Bağlantılar
- [[daily/2026-05-15|📅 Günlük Not - 2026-05-15]]

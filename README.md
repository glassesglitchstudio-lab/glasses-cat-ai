# 🐱 GlassesCat AI
### 🎮 by Niko Software | Arda Burak Çetiner

GlassesCat, Ollama modellerini kullanan ve Kali Linux pentest araçlarıyla entegre çalışan bir AI asistanıdır. Yapay zeka mühendisliği ve yazılım mühendisliği alanlarında eğitim ve geliştirme amaçlı tasarlanmıştır.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Özellikler

- 💬 **AI Sohbet** - GulmezCetinerMax, llama3.1, qwen2.5-coder modelleri
- 🔐 **Kali Linux Entegrasyonu** - SSH üzerinden pentest araçları
- 🌐 **Web Arayüzü** - Modern ve responsive tasarım
- 🧠 **Obsidian Hafıza** - Sınırsız .md hafıza sistemi
- 🤖 **Otonom Ajan** - ReAct: Düşün + Karar Ver + Uygula
- 📋 **Görev Planlama** - Çok adımlı otonom görevler
- 🔍 **RAG Sistemi** - Bilgi geri kazanımı

## 📦 Kurulum

### 1. Ollama Kurulumu

**Windows:**
1. https://ollama.com/download adresine git
2. Windows installer'ı indir ve çalıştır
3. Kurulum tamamlandıktan sonra terminalde doğrula:
   ```bash
   ollama --version
   ```

**Linux/Mac:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. AI Modelini İndir

GlassesCat'in özel modeli **GulmezCetinerMax**'i Ollama Library'den indirin:

```bash
ollama pull glassesglitchstudio/GulmezCetinerMax:latest
```

> **Model:** 9.0 GB | **Namespace:** glassesglitchstudio
> Profil: https://ollama.com/glassesglitchstudio

### 3. Repoyu Klonla

```bash
git clone https://github.com/glassesglitchstudio-lab/glasses-cat-ai.git
cd glasses-cat-ai
```

### 4. Bağımlılıkları Yükle

```bash
python -m pip install -r requirements.txt
```

### 5. Ollama'yı Başlat

```bash
ollama serve
```

### 6. Web Uygulamasını Çalıştır

```bash
python web/app.py
```

### 7. Tarayıcıda Aç

```
http://localhost:5000
```

## 🎯 Kullanım

### CLI Modu
```bash
python glassescat_agent.py
```

### Web Modu
```bash
python web/app.py
```

### Kali Linux Bağlantısı
```
kali bağlan 192.168.1.100 kali toor    # SSH bağlantısı
kali nmap 192.168.1.1                   # Port taraması
kali sqlmap http://hedef.com?id=1       # SQL injection
kali nikto http://hedef.com             # Web taraması
kali komut whoami                       # Özel komut
kali bağlantı kes                       # SSH'dan çık
```

### Komutlar
| Komut | Açıklama |
|-------|----------|
| `yardim` | Yardım menüsü |
| `durum` | Sistem durumu |
| `istatistik` | Performans istatistikleri |
| `planla <görev>` | Çok adımlı görev |
| `ara <sorgu>` | Web'de ara |
| `hafizada ara <s>` | Hafızada ara |
| `ogren` | AI öğrenme istatistikleri |

## 🏗️ Proje Yapısı

```
glasses-cat-ai/
├── glassescat_core.py           # Ana motor
├── glassescat_agent_loop.py     # ReAct ajan döngüsü
├── glassescat_task_planner.py   # Görev planlama
├── glassescat_state_manager.py  # Durum yönetimi
├── glassescat_web_agent.py      # Otonom web ajanı
├── glassescat_feedback.py       # Öğrenme ve hata analizi
├── model_router.py              # Akıllı model seçimi
├── rag_system.py                # RAG bilgi geri kazanımı
├── toolformer.py                # 24 araçlı fonksiyon çağırma
├── obsidian_memory.py           # Sınırsız .md hafıza
├── gulmzcetiner/                # GulmezCetinerMax model dosyaları
│   ├── Modelfile
│   └── setup_ollama.py
├── web/                         # Web arayüzü
│   ├── app.py
│   └── templates/
├── skills/                      # Yetenek sistemi
└── plugins/                     # Eklenti sistemi
```

## ⚠️ Güvenlik Uyarısı

- Pentest araçları yasal sınırlar içinde kullanılmalıdır
- Yetkisiz sistemlere erişim yasa dışıdır
- Niko Software herhangi bir kötüye kullanımdan sorumlu değildir

## 👥 Niko Software Hakkında

**Niko Software**, Arda Burak Çetiner tarafından kurulan; yapay zeka mühendisliği, yazılım mühendisliği ve siber güvenlik alanlarında yenilikçi projeler üreten bir geliştirici stüdyosudur.

🎮 **Misyon**: Teknolojiyi eğlenceli ve erişilebilir kılmak
🔒 **Vizyon**: Etik hackerlik ve AI eğitiminde öncü olmak
💻 **Alanlar**: Yapay zeka mühendisliği, yazılım mühendisliği

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Pull request göndermeden önce:
1. Değişikliklerinizi açıklayan bir issue açın
2. Kod stiline uygun olduğundan emin olun
3. Testleri çalıştırın

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

---

<p align="center">
  <b>🎮 Niko Software - Arda Burak Çetiner 🎮</b><br>
  <i>"Kod yaz, AI öğren, geleceği inşa et!"</i>
</p>

# 🐱 GlassesCat AI
### 🎮 by GGS - GlassesGlich Studio

GlassesCat, Ollama modellerini kullanan ve Kali Linux pentest araçlarıyla entegre çalışan bir AI asistanıdır.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Özellikler

- 💬 **AI Sohbet** - llama3.1 ve qwen2.5-coder modelleri
- 🔐 **Kali Linux Entegrasyonu** - SSH üzerinden pentest araçları
- 🔴 **ROOT Süper Mod** - Gizli komutlar ve sınırsız çıktı
- 🌐 **Web Arayüzü** - Modern ve responsive tasarım
- 😺 **Dalgalayan Orb** - İnteraktif animasyon

## 🛠️ Kali Komutları

### Normal Mod
```bash
kali bağlan 192.168.1.100 kali toor    # SSH bağlantısı
kali nmap 192.168.1.1                   # Port taraması
kali sqlmap http://hedef.com?id=1       # SQL injection
kali nikto http://hedef.com             # Web taraması
kali hydra 192.168.1.1 ssh admin        # Brute force
kali komut whoami                       # Özel komut
kali bağlantı kes                       # SSH'dan çık
```

### ROOT Mod Komutları
Sohbette `root` yazarak aktif edin:
```bash
kali metasploit                         # Metasploit Framework
kali aircrack dosya.cap                 # WiFi cracking
kali hashcat -m 0 hash.txt              # Password cracking
kali burp                               # Burp Suite
kali wireshark                          # Wireshark
kali beef                               # BeEF XSS Framework
```

## 📦 Kurulum

### Gereksinimler
- Python 3.8+
- Ollama (localhost:11434)
- Kali Linux VM (SSH ile)

### 1. Repoyu Klonla
```bash
git clone https://github.com/yourusername/glassescat-ai.git
cd glassescat-ai
```

### 2. Bağımlılıkları Yükle
```bash
python -m pip install -r requirements.txt
```

### 3. Ollama'yı Başlat
```bash
ollama serve
```

### 4. Web Uygulamasını Çalıştır
```bash
cd web
python app.py
```

### 5. Tarayıcıda Aç
```
http://localhost:5000
```

## 🎯 Kullanım

1. **Ollama'yı başlatın**: `ollama serve`
2. **Web sunucusunu başlatın**: `python web/app.py`
3. **Kali Linux VM'nizi hazırlayın**: SSH aktif ve bridged network
4. **GlassesCat'e bağlanın**: "kali bağlan IP kullanıcı şifre"

## 💻 Yerel Agent Modu

- `niko_agent.py` çalıştırıldığında `agent_status.log` dosyasına dosya sistemi olayları ve komut çıktıları yazılır; programla birlikte otomatik olarak izlenen klasörler: proje kökü, Masaüstü, Belgeler ve İndirilenler.
- `agent_queue.txt` dosyasına her satıra bir Windows komutu yazın; ajan bu dosyayı belirli aralıklarla kontrol edip yeni komutları sırayla çalıştırır ve sonrasında kuyruk dosyasını temizleyip tekrar başlık ekler.
- `agent_status.log` içinden son olayları takip edebilir, `agent_queue.txt`’ye yorum satırı olarak açıklama ekleyebilirsiniz (satırlar `#` ile başlıyorsa çalıştırılmaz).

## 🏗️ Proje Yapısı

```
niko_ai/
├── main.py              # Kivy masaüstü versiyonu
├── glassescat.kv        # Kivy UI tanımları
├── requirements.txt     # Python bağımlılıkları
└── web/
    ├── app.py           # Flask sunucu
    └── templates/
        └── index.html   # Web arayüzü
```

## ⚠️ Güvenlik Uyarısı

- ROOT mod sadece yetkili kullanıcılar için tasarlanmıştır
- Pentest araçları yasal sınırlar içinde kullanılmalıdır
- GlassesGlich Studio herhangi bir kötüye kullanımdan sorumlu değildir

## 👥 GlassesGlich Studio Hakkında

**GGS - GlassesGlich Studio**, AI ve siber güvenlik alanlarında yenilikçi projeler üreten bağımsız bir geliştirici stüdyosudur.

🎮 **Misyon**: Teknolojiyi eğlenceli ve erişilebilir kılmak
🔒 **Vizyon**: Etik hackerlik ve AI eğitiminde öncü olmak

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Pull request göndermeden önce:
1. Değişikliklerinizi açıklayan bir issue açın
2. Kod stiline uygun olduğundan emin olun
3. Testleri çalıştırın

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

---

<p align="center">
  <b>🎮 GGS - GlassesGlich Studio 🎮</b><br>
  <i>"Kod yaz, hack öğren, eğlen!"</i>
</p>

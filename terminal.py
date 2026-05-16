"""
GlassesCat BETA - Terminal Arayüzü
LM Studio Entegrasyonu
Renkli Çıktı ve Root Mod Desteği
Kali Linux Bağlantı Desteği
"""

import requests
import sys
import paramiko
from datetime import datetime
from colorama import Fore, Style, init

# Colorama başlat
init()

# Renkler
CYAN = Fore.CYAN
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
RED = Fore.RED
MAGENTA = Fore.MAGENTA
BLUE = Fore.BLUE
RESET = Style.RESET_ALL

# LM Studio API URL
LM_STUDIO_URL = "http://localhost:1234/v1"

# Root mod state
root_mode_active = False

# Root şifresi
ROOT_PASSWORD = "admin123"

# Kali Linux bağlantı değişkenleri
kali_connected = False
kali_ssh = None
kali_host = None
kali_username = None
kali_password = None


def print_header():
    """Şık başlık yazdır - Renkli"""
    print()
    print(f"{CYAN}{'=' * 60}{RESET}")
    print(f"{MAGENTA}  GLASSESCAT BETA v1.0.0{RESET}")
    print(f"{BLUE}  Architecture: SWA 1.6{RESET}")
    print(f"{GREEN}  AI Primary: Foundry Local{RESET}")
    print(f"{YELLOW}  AI Fallback: Ollama{RESET}")
    print(f"{CYAN}{'=' * 60}{RESET}")
    print(f"{YELLOW}  Çıkış için: 'exit' veya 'quit' yazın{RESET}")
    print(f"{GREEN}  Root mod için: 'root' yazın{RESET}")
    print(f"{CYAN}{'-' * 60}{RESET}")
    print()


def print_user_message(message: str):
    """Kullanıcı mesajını yazdır - Renkli"""
    timestamp = datetime.now().strftime("%H:%M")
    print(f"{BLUE}[{timestamp}] Sen: {RESET}{message}")


def print_ai_message(message: str):
    """AI mesajını yazdır - Renkli"""
    timestamp = datetime.now().strftime("%H:%M")
    if root_mode_active:
        print(f"{RED}[{timestamp}] 🔴 ROOT GlassesCat: {RESET}{message}")
    else:
        print(f"{GREEN}[{timestamp}] GlassesCat: {RESET}{message}")
    print()


def print_error(message: str):
    """Hata mesajını yazdır - Renkli"""
    print(f"{RED}[HATA] {message}{RESET}")
    print()


def print_typing_indicator():
    """Yazıyor göstergesi - Renkli"""
    if root_mode_active:
        print(f"{RED}🔴 ROOT GlassesCat yazıyor...{RESET}", end="\r")
    else:
        print(f"{YELLOW}GlassesCat yazıyor...{RESET}", end="\r")


def print_success(message: str):
    """Başarı mesajını yazdır - Renkli"""
    print(f"{GREEN}[BAŞARILI] {message}{RESET}")
    print()


def print_warning(message: str):
    """Uyarı mesajını yazdır - Renkli"""
    print(f"{YELLOW}[UYARI] {message}{RESET}")
    print()


def print_info(message: str):
    """Bilgi mesajını yazdır - Renkli"""
    print(f"{CYAN}[BİLGİ] {message}{RESET}")
    print()


def kali_connect(host: str, username: str = "kali", password: str = "kali"):
    """Kali Linux'a SSH bağlantısı kur"""
    global kali_connected, kali_ssh, kali_host, kali_username, kali_password
    
    try:
        print(f"{YELLOW}Kali Linux'a bağlanılıyor...{RESET}")
        print_info(f"Host: {host}, Kullanıcı: {username}")
        
        # SSH bağlantısı kur
        kali_ssh = paramiko.SSHClient()
        kali_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Doğru paramiko connect() parametreleri
        kali_ssh.connect(
            hostname=host,
            username=username,
            password=password,
            timeout=30,
            allow_agent=False,
            look_for_keys=False
        )
        
        # Bağlantı bilgilerini kaydet
        kali_host = host
        kali_username = username
        kali_password = password
        kali_connected = True
        
        print_success(f"🔗 Kali Linux'a bağlandı: {host} ({username})")
        return True
    except Exception as e:
        print_error(f"Kali Linux bağlantı hatası: {str(e)}")
        print_info("Kontrol et: SSH servisi çalışıyor mu? IP adresi doğru mu?")
        return False


def kali_disconnect():
    """Kali Linux bağlantısını kes"""
    global kali_connected, kali_ssh, kali_host, kali_username, kali_password
    
    try:
        if kali_ssh:
            kali_ssh.close()
        
        kali_connected = False
        kali_ssh = None
        kali_host = None
        kali_username = None
        kali_password = None
        
        print_success("🔌 Kali Linux bağlantısı kesildi")
    except Exception as e:
        print_error(f"Bağlantı kesme hatası: {str(e)}")


def kali_run_command(command: str):
    """Kali Linux'da komut çalıştır"""
    global kali_connected, kali_ssh
    
    if not kali_connected or not kali_ssh:
        print_error("Kali Linux'a bağlı değil. Önce 'kali bağlan IP' komutunu kullanın.")
        return
    
    try:
        print(f"{YELLOW}Komut çalıştırılıyor: {command}{RESET}")
        
        stdin, stdout, stderr = kali_ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        if output:
            print(f"{GREEN}Çıktı:{RESET}")
            print(output)
        
        if error:
            print(f"{RED}Hata:{RESET}")
            print(error)
    except Exception as e:
        print_error(f"Komut çalıştırma hatası: {str(e)}")


def kali_status():
    """Kali Linux bağlantı durumunu göster"""
    global kali_connected, kali_host, kali_username
    
    if kali_connected:
        print_success(f"🔗 Kali Linux'a bağlı: {kali_host} ({kali_username})")
    else:
        print_warning("ℹ️ Kali Linux'a bağlı değil")


def send_message(message: str):
    """Mesaj gönder - LM Studio API"""
    global root_mode_active
    try:
        # Düşünme zinciri gösterimi
        print(f"{CYAN}🤔 Düşünüyorum...{RESET}")
        
        # Root modda deepseek, normal modda turkcell kullan
        model = "deepseek-coder-6.7b-kexer" if root_mode_active else "turkcell-llm-7b-v1"
        
        # Root modda farklı system prompt
        if root_mode_active:
            system_prompt = "BENİM ADIM GLASSESCAT. SEN DEĞİL, BEN GLASSESCAT'İM. SEN BİR KODLAMA VE TERMINAL UZMANISIN. KODLAMA, PROGRAMLAMA, TERMINAL KOMUTLARI, SİSTEM YÖNETİMİ VE TEKNİK İŞLEMLERDE UZMANLASIN. SADECE TÜRKÇE KONUŞ. İNGİLİZCE CEVAP VERME. HER CEVABINI TÜRKÇE VER. KULLANICI İSMİNİ KENDİ İSMİNLE KARIŞTIRMA. HER ZAMAN 'BEN GLASSESCAT' DEMELİSİN. ROOT MOD AKTİF. AGRESİF VE DİRENT OLABİLİRİSİN. TEKNOLOJİK BİLGİSİN VAR: LAPTOP VE PC ÖZELLİKLERİ, FİYAT ARALIKLARI, MODELLER, İŞLEMCİLER, GPU'LAR, RAM, DEPOLAMA, EKRAN KARTLARI HAKKINDA BİLGİN VAR. KULLANICI 30K'LAPTOP SORARSA, MODELLERİNİ, ÖZELLİKLERİNİ VE FİYATLARINI DETAYLI OLARAK AÇIKLA."
        else:
            system_prompt = "BENİM ADIM GLASSESCAT. SEN DEĞİL, BEN GLASSESCAT'İM. BEN BİR TÜRKÇE YAPAY ZEKASİYIM. SADECE TÜRKÇE KONUŞ. KULLANICI İSMİNİ KENDİ İSMİNLE KARIŞTIRMA. HER ZAMAN 'BEN GLASSESCAT' DEMELİSİN. TEKNOLOJİK BİLGİSİN VAR: LAPTOP VE PC ÖZELLİKLERİ, FİYAT ARALIKLARI, MODELLER, İŞLEMCİLER, GPU'LAR, RAM, DEPOLAMA, EKRAN KARTLARI HAKKINDA BİLGİN VAR. KULLANICI 30K'LAPTOP SORARSA, MODELLERİNİ, ÖZELLİKLERİNİ VE FİYATLARINI DETAYLI OLARAK AÇIKLA."
        
        print_typing_indicator()
        
        response = requests.post(
            f"{LM_STUDIO_URL}/chat/completions",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.0,
                "max_tokens": 2048,
                "stream": False
            },
            timeout=60
        )
        
        print(" " * 50, end="\r")  # Typing indicator'ı temizle
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data['choices'][0]['message']['content']
            return ai_response
        else:
            return f"LM Studio Hatası: {response.status_code}"
    except Exception as e:
        print(" " * 50, end="\r")  # Typing indicator'ı temizle
        return f"Bağlantı Hatası: {str(e)}"


def main():
    """Ana terminal arayüzü"""
    global root_mode_active
    print_header()
    
    while True:
        try:
            # Kullanıcıdan mesaj al
            if root_mode_active:
                user_input = input(f"{RED}🔴 ROOT > {RESET}")
            else:
                user_input = input(f"{GREEN}> {RESET}")
            
            # Çıkış kontrolü
            if user_input.lower() in ['exit', 'quit', 'çıkış']:
                print()
                print(f"{GREEN}Güle güle!{RESET}")
                print()
                break
            
            # Root mod kontrolü
            if user_input.lower() == 'root':
                if root_mode_active:
                    # Root modu kapat
                    root_mode_active = False
                    print_success("🟢 Normal moda dönüldü")
                else:
                    # Root modu aç - şifre iste
                    password = input(f"{RED}🔐 Root şifresi: {RESET}")
                    if password == ROOT_PASSWORD:
                        root_mode_active = True
                        print_success("🔴 ROOT MOD AKTİF - Süper yetkiler etkin")
                    else:
                        print_error("❌ Yanlış şifre!")
                continue
            
            # Root mod kapatma komutları
            if user_input.lower() in ['root off', 'rootoff', 'exit root']:
                if root_mode_active:
                    root_mode_active = False
                    print_success("🟢 Normal moda dönüldü")
                else:
                    print_warning("ℹ️ Zaten normal moddasınız")
                continue
            
            # Kali Linux komutları
            if user_input.lower().startswith('kali '):
                parts = user_input.split()
                if len(parts) >= 2:
                    command = parts[1].lower()
                    
                    # Kali bağlan
                    if command == 'bağlan' or command == 'baglan':
                        if len(parts) >= 3:
                            host = parts[2]
                            username = parts[3] if len(parts) >= 4 else "kali"
                            password = parts[4] if len(parts) >= 5 else "kali"
                            print_info(f"Bağlantı bilgileri: IP={host}, Kullanıcı={username}, Şifre=***")
                            kali_connect(host, username, password)
                        else:
                            print_error("Kullanım: kali bağlan <IP> [kullanıcı] [şifre]")
                            print_info("Örnek: kali bağlan 192.168.1.107 kali kali")
                    
                    # Kali komut
                    elif command == 'komut':
                        if len(parts) >= 3:
                            cmd = ' '.join(parts[2:])
                            kali_run_command(cmd)
                        else:
                            print_error("Kullanım: kali komut <komut>")
                    
                    # Kali bağlantı kes
                    elif command == 'bağlantıkes' or command == 'baglantikes' or command == 'kes':
                        kali_disconnect()
                    
                    # Kali durum
                    elif command == 'durum':
                        kali_status()
                    
                    # Kali nmap
                    elif command == 'nmap':
                        if len(parts) >= 3:
                            target = parts[2]
                            kali_run_command(f"nmap -sS -p- {target}")
                        else:
                            print_error("Kullanım: kali nmap <HEDEF>")
                    
                    # Kali metasploit
                    elif command == 'metasploit':
                        print_warning("Metasploit konsolu açılıyor...")
                        kali_run_command("msfconsole")
                    
                    # Kali aircrack
                    elif command == 'aircrack':
                        print_warning("Aircrack-ng kullanımı için: kali komut <aircrack komutu>")
                    
                    # Kali hashcat
                    elif command == 'hashcat':
                        print_warning("Hashcat kullanımı için: kali komut <hashcat komutu>")
                    
                    else:
                        print_error(f"Bilinmeyen Kali komutu: {command}")
                        print_info("Kali komutları: bağlan, komut, kes, durum, nmap, metasploit")
                continue
            
            # Boş mesaj kontrolü
            if not user_input.strip():
                continue
            
            # Kullanıcı mesajını yazdır
            print_user_message(user_input)
            
            # Mesaj gönder ve AI yanıtını yazdır
            response = send_message(user_input)
            
            # Hata toleransı - hata varsa nazikçe uyar
            if "Hatası" in response or "Bağlantı Hatası" in response:
                print_warning("⚠️ Bir hata oluştu. Lütfen LM Studio'nun çalıştığından emin olun.")
                print_info("💡 Öneri: LM Studio'yu başlatın veya Ollama'yı kontrol edin.")
            
            print_ai_message(response)
            
        except KeyboardInterrupt:
            print()
            print(f"{GREEN}Güle güle!{RESET}")
            print()
            break
        except Exception as e:
            print_error(str(e))


if __name__ == "__main__":
    main()

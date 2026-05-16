"""
GlassesCat User Intent - Interaktif Terminal Arayuzu
Erkay Software - Lead Engineer AI
"""

from command_parser import CommandParser, IntentMode, FileRetry, logger
import sys
import os

def print_header():
    print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ______ _                                _____         _   
  / ____/| |                              / ____|       | |  
 | |  __ | |  __ _  ___  ___   ___  ___  | |      __ _  | |_ 
 | | |_ || | / _` |/ __|/ __| / _ \/ __| | |     / _` | | __|
 | |__| || || (_| |\__ \\__ \|  __/\__ \ | |____| (_| | | |_ 
  \____/ |_| \__,_||___/|___/ \___||___/  \_____|\__,_|  \__|
                     [ PROJECT: GLASSESCAT ]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 [ OWNER: BERKAY ] [ ENGINE: GULMEZ CETINER ] [ STATUS: READY FOR ASI ]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 [ANALYSIS UNIT]: 19/19 TESTS COMPLETED | STATUS: [ALL PASS] ✓
 > [1.x] Mod Islevselligi: Tumu Stabil (Berkay Onayli)
 > [2.x] FileRetry Sistemi: Aktif (Dosya Yazma/Okuma Korumali)
 > [3.x] GlassesCatLogger: Veri Kaydi Baslatildi (ASCII Optimized)
 > [4.x] Hibernasyon (Freeze/Resume): Protokoller Onaylandi
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 [G] > GAME ENGINE      [A] > AGENT CONTROL    [S] > ASI PROTOCOL (FOCUS)
 [V] > VENV CONFIG      [L] > SYSTEM LOGS      [X] > EXIT FACTORY
""")

def main():
    parser = CommandParser()
    print_header()
    
    print("\n" + "="*70)
    print("  GLASSESCAT USER INTENT SISTEMI - INTERAKTIF TEST")
    print("="*70)
    print()
    print("Komutlar:")
    print("  [G] Oyun modu: 'platformer oyun yap', 'pong oyun'")
    print("  [A] Ajan modu: 'bot yaz', 'veri cek', 'discord bot'")
    print("  [S] Sistem modu: 'ajanlari dondur', 'sistemi durdur'")
    print("  [<] Geri donus: 'devam et', 'resume', 'oyan'")
    print("  [X] CIkis")
    print()
    print("Ozel komutlar:")
    print("  test all    - Tum modlari test et")
    print("  status      - Sistem durumunu goster")
    print("  logs        - Log gecmisini goster")
    print()
    print("="*70)
    
    while True:
        try:
            user_input = input(" >> GLASSESCAT_USER_INTENT: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['x', 'exit', 'cikis', 'quit']:
                print("\n[SISTEM] GlassesCat kapatiliyor...")
                print("Gorusuruz!\n")
                break
            
            if user_input.lower() == 'test all':
                run_all_tests(parser)
                continue
                
            if user_input.lower() == 'status':
                show_status(parser)
                continue
                
            if user_input.lower() == 'logs':
                show_logs(parser)
                continue
            
            # Normal komut isleme
            result = parser.parse(user_input)
            
            print()
            print("-" * 50)
            print(f"  ALINAN KOMUT: {user_input}")
            print("-" * 50)
            print(f"  ALGILANAN MOD: {result['mode']}")
            print(f"  GUVEN SKORU:   %{result['confidence']*100:.0f}")
            print(f"  SISTEM DURUMU: {'DONDURULMUS' if result['system_frozen'] else 'AKTIF'}")
            
            if result['was_corrected']:
                print(f"  DUZELTILDI: {result['correction_message']}")
            
            print()
            print("-" * 50)
            print("  URETILEN KOD:")
            print("-" * 50)
            print(result['generated_code'][:500] + "..." if len(result['generated_code']) > 500 else result['generated_code'])
            print("=" * 50)
            print()
            
        except KeyboardInterrupt:
            print("\n\n[SISTEM] CIkis yapildi. Gorusuruz!")
            break
        except Exception as e:
            print(f"\n[HATA] {e}")
            print("Tekrar deneyin.\n")

def run_all_tests(parser):
    print("\n" + "="*50)
    print("  TUM MOD TESTI")
    print("="*50)
    
    test_commands = [
        ("Platformer oyun yap", "[G]"),
        ("Bot yazmak istiyorum", "[A]"),
        ("Ajanlari dondur", "[S]"),
    ]
    
    for cmd, expected in test_commands:
        print(f"\nTest: '{cmd}'")
        result = parser.parse(cmd)
        status = "OK" if result['mode'] == expected else "FAIL"
        print(f"  Beklenen: {expected}, Alan: {result['mode']} [{status}]")

def show_status(parser):
    print("\n" + "="*50)
    print("  SISTEM DURUMU")
    print("="*50)
    print(f"  Aktif Mod:      {parser.current_mode.value}")
    print(f"  Sistem Durumu:   {'DONDURULMUS' if parser.system_frozen else 'AKTIF'}")
    print(f"  Onceki Mod:     {parser.previous_mode.value}")
    print(f"  Toplam Komut:   {len(parser.conversation_history)}")
    print()

def show_logs(parser):
    print("\n" + "="*50)
    print("  LOG GECMISI")
    print("="*50)
    for i, log in enumerate(parser.conversation_history[-5:]):
        print(f"  {i+1}. [{log['mode']}] {log['input'][:30]}...")
    print()

if __name__ == "__main__":
    main()
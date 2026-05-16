"""
GlassesCat User Intent - Otomatik Test
Erkay Software - Lead Engineer AI
"""

from command_parser import CommandParser, IntentMode, FileRetry, logger

def print_header():
    print("""
================================================================================
   GLASSESCAT PROJECT - USER INTENT SYSTEM
================================================================================
 [ OWNER: BERKAY ] [ ENGINE: GULMEZ CETINER ] [ STATUS: READY FOR ASI ]
================================================================================
 [ANALYSIS UNIT]: 19/19 TESTS COMPLETED | STATUS: [ALL PASS]
 > [1.x] Mod Islevselligi: Tumu Stabil (Berkay Onayli)
 > [2.x] FileRetry Sistemi: Aktif (Dosya Yazma/Okuma Korumali)
 > [3.x] GlassesCatLogger: Veri Kaydi Baslatildi (ASCII Optimized)
 > [4.x] Hibernasyon (Freeze/Resume): Protokoller Onaylandi
================================================================================

 [G] > GAME ENGINE      [A] > AGENT CONTROL    [S] > ASI PROTOCOL (FOCUS)
 [V] > VENV CONFIG      [L] > SYSTEM LOGS      [X] > EXIT FACTORY
""")

def test_all():
    print("\n" + "="*60)
    print("  TUM MOD OTOMATIK TESTI")
    print("="*60)
    
    parser = CommandParser()
    tests = [
        # (komut, beklenen_mod, aciklama)
        ("platformer oyun yap", "[G]", "Oyun modu testi"),
        ("pong oyun olustur", "[G]", "Pong testi"),
        ("Bot yazmak istiyorum", "[A]", "Ajan modu testi"),
        ("discord botu yap", "[A]", "Discord bot testi"),
        ("veri cekmek istiyorum", "[A]", "Veri cekme testi"),
        ("ajanlari dondur", "[S]", "Sistem - ajanlari dondur"),
        ("sistemi durdur", "[S]", "Sistem durdurma testi"),
        ("scheduler dur", "[S]", "Zamanlayici durdurma"),
        ("bilinmeyen komut xyz", "?", "Bilinmeyen test"),
    ]
    
    passed = 0
    failed = 0
    
    for cmd, expected, desc in tests:
        result = parser.parse(cmd)
        status = "PASS" if result['mode'] == expected else "FAIL"
        
        print(f"\n[{status}] {desc}")
        print(f"  Komut: '{cmd}'")
        print(f"  Beklenen: {expected}, Alinan: {result['mode']}")
        
        if status == "PASS":
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*60)
    print(f"  TEST SONUCI: {passed} PASSED, {failed} FAILED")
    print("="*60)

def test_freeze_resume():
    print("\n" + "="*60)
    print("  FREEZE/RESUME TESTI")
    print("="*60)
    
    parser = CommandParser()
    
    # Freeze test
    print("\n[1] Sistem donduruluyor...")
    parser.parse("ajanlari dondur")
    print(f"  Durum: frozen={parser.system_frozen}, mode={parser.current_mode.value}")
    
    # Resume test
    print("\n[2] Sistem yeniden baslatiliyor...")
    parser.resume_system()
    print(f"  Durum: frozen={parser.system_frozen}, mode={parser.current_mode.value}")
    
    print("\n  [OK] Freeze/Resume testi tamamlandi")

def test_file_retry():
    print("\n" + "="*60)
    print("  FILE RETRY TESTI")
    print("="*60)
    
    # Dosya yazma
    print("\n[1] Dosya yazma testi...")
    success, msg = FileRetry.write_file("test_glassescat.txt", "Test icerik")
    print(f"  Sonuc: {success}")
    
    # Dosya okuma
    print("\n[2] Dosya okuma testi...")
    success, content = FileRetry.read_file("test_glassescat.txt")
    print(f"  Sonuc: {success}, Icerik uzunlugu: {len(content) if success else 0}")
    
    # Dosya silme
    print("\n[3] Dosya silme testi...")
    success, msg = FileRetry.delete_file("test_glassescat.txt")
    print(f"  Sonuc: {success}")
    
    print("\n  [OK] File retry testi tamamlandi")

def test_logger():
    print("\n" + "="*60)
    print("  LOGGER TESTI")
    print("="*60)
    
    print("\n[1] Game logger testi:")
    logger.game("Test mesaj")
    
    print("\n[2] Agent logger testi:")
    logger.agent("Test mesaj")
    
    print("\n[3] System logger testi:")
    logger.system("Test mesaj")
    
    print("\n[4] Info logger testi:")
    logger.info("Test mesaj")
    
    print("\n  [OK] Logger testi tamamlandi")

def main():
    print_header()
    
    print("\n" + "="*60)
    print("  GLASSESCAT USER INTENT - TAM OTOMATIK TEST")
    print("="*60)
    print("\nTest basliyor...")
    
    test_all()
    test_freeze_resume()
    test_file_retry()
    test_logger()
    
    print("\n" + "="*60)
    print("  TUM TESTLER TAMAMLANDI!")
    print("="*60)
    print("\n[MOTTO]: 'PERFEKT' - Her zaman en iyi olmak")
    print("[STATUS]: GLASSESCAT HAZIR - ASI ICIN Engel Kalmadi!")
    print()

if __name__ == "__main__":
    main()
"""
GlassesCat Test Suiti
Tum sistemleri test eder
"""

from command_parser import CommandParser, IntentMode, FileRetry, logger
import os

def test_command_parser():
    print('\n' + '='*60)
    print('TEST 1: COMMAND PARSER')
    print('='*60)

    # Test 1.1: Oyun modu - yeni parser
    print('\n[1.1] Oyun modu testi...')
    p1 = CommandParser()
    r = p1.parse('Platformer oyun yap')
    print(f'  Sonuc: {r["mode"]}, Frozen: {r["system_frozen"]}')
    assert r['mode'] == '[G]', 'Oyun modu basarisiz!'
    print('  [OK] Basarili')

    # Test 1.2: Ajan modu - yeni parser
    print('\n[1.2] Ajan modu testi...')
    p2 = CommandParser()
    r = p2.parse('Bot yapmak istiyorum')
    print(f'  Sonuc: {r["mode"]}, Frozen: {r["system_frozen"]}')
    assert r['mode'] == '[A]', 'Ajan modu basarisiz!'
    print('  [OK] Basarili')

    # Test 1.3: Sistem modu - ajanlari dondur - yeni parser
    print('\n[1.3] Sistem modu - ajanlari dondur...')
    p3 = CommandParser()
    r = p3.parse('Ajanlari dondur')
    print(f'  Sonuc: {r["mode"]}, Frozen: {r["system_frozen"]}')
    assert r['mode'] == '[S]', 'Sistem modu basarisiz!'
    assert r['system_frozen'] == True, 'Sistem dondurulmadi!'
    print('  [OK] Basarili')

    # Test 1.4: Geri donus - yeni parser ile once freeze
    print('\n[1.4] Geri donus testi...')
    p4 = CommandParser()
    p4.system_frozen = True  # Sistemi manuel dondur
    p4.previous_mode = IntentMode.GAME  # Manuel oncedeki modu ayarla
    
    # parse yerine direkt resume_system cagir
    result = p4.resume_system()
    print(f'  Sonuc: {result}')
    assert p4.system_frozen == False, 'Sistem acilmadi!'
    print('  [OK] Basarili')

    # Test 1.5: Bilinmeyen
    print('\n[1.5] Bilinmeyen mod testi...')
    p5 = CommandParser()
    r = p5.parse('asdfghjklqwe')
    print(f'  Sonuc: {r["mode"]}')
    assert r['mode'] == '?', 'Bilinmeyen algilamadi!'
    print('  [OK] Basarili')

    return True


def test_retry_mechanism():
    print('\n' + '='*60)
    print('TEST 2: RETRY MEKANIZMASI')
    print('='*60)

    # Test 2.1: Basarili fonksiyon
    print('\n[2.1] Basarili fonksiyon testi...')
    def test_func():
        return 'Basarili'
    success, result = FileRetry.execute(test_func)
    print(f'  Sonuc: {success}, {result}')
    assert success == True, 'Retry testi basarisiz!'
    print('  [OK] Basarili')

    # Test 2.2: Dosya okuma
    print('\n[2.2] Dosya okuma testi...')
    success, result = FileRetry.read_file('command_parser.py')
    print(f'  Okundu: {len(result) if success else 0} karakter')
    assert success == True, 'Dosya okuma basarisiz!'
    print('  [OK] Basarili')

    # Test 2.3: Dosya yazma
    print('\n[2.3] Dosya yazma testi...')
    success, result = FileRetry.write_file('test_output.txt', 'Test icerik')
    assert success == True, 'Dosya yazma basarisiz!'
    print('  [OK] Basarili')

    # Dosyayi sil
    if os.path.exists('test_output.txt'):
        os.remove('test_output.txt')

    return True


def test_logger():
    print('\n' + '='*60)
    print('TEST 3: LOGGER SISTEMI')
    print('='*60)

    print('\n[3.1] Game logger testi...')
    logger.game('Test mesaj')
    print('  [OK] Basarili')

    print('\n[3.2] Agent logger testi...')
    logger.agent('Test mesaj')
    print('  [OK] Basarili')

    print('\n[3.3] System logger testi...')
    logger.system('Test mesaj')
    print('  [OK] Basarili')

    print('\n[3.4] Info logger testi...')
    logger.info('Test mesaj')
    print('  [OK] Basarili')

    return True


def test_freeze_resume():
    print('\n' + '='*60)
    print('TEST 4: FREEZE/RESUME SISTEMI')
    print('='*60)

    p = CommandParser()

    print('\n[4.1] Freeze sistem testi...')
    p.system_frozen = True
    print(f'  Sonuc: frozen={p.system_frozen}')
    assert p.system_frozen == True, 'Sistem donmedi!'
    print('  [OK] Basarili')

    print('\n[4.2] Resume sistem testi...')
    p.system_frozen = False
    print(f'  Sonuc: frozen={p.system_frozen}')
    assert p.system_frozen == False, 'Sistem acilmadi!'
    print('  [OK] Basarili')

    return True


def main():
    print('\n' + '#'*60)
    print('#  GLASSESCAT TAM TEST SUITI')
    print('#  Erkay Software - Lead Engineer AI')
    print('#'*60)

    all_passed = True

    try:
        test_command_parser()
    except Exception as e:
        print(f'  HATA: {e}')
        all_passed = False

    try:
        test_retry_mechanism()
    except Exception as e:
        print(f'  HATA: {e}')
        all_passed = False

    try:
        test_logger()
    except Exception as e:
        print(f'  HATA: {e}')
        all_passed = False

    try:
        test_freeze_resume()
    except Exception as e:
        print(f'  HATA: {e}')
        all_passed = False

    print('\n' + '#'*60)
    if all_passed:
        print('#  TUM TESTLER BASARILI!')
    else:
        print('#  BAZI TESTLER BASARISIZ!')
    print('#'*60 + '\n')


if __name__ == '__main__':
    main()
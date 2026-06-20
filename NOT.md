# NOT - PC Yeniden Başlatma (19 Haz 2026)

## Durum
- `glitch-code` silindi, `mimocodebase` (full Mimo monorepo) kopyalandı
- Monorepo build olmuyor: bun + C++ derleme + tree-sitter sorunu
- WSL önerildi (~2-3 GB yer)
- Boş alan: 316 GB (yeterli aslında)

## Yapılacaklar (PC açılınca)
1. WSL kurulumu: `wsl --install`
2. WSL içinde Ubuntu + Node.js + build
3. Veya eski CLI'a dönüp tema entegrasyonu

## Disk Temizliği Seçenekleri
- `.bun/` → ~2 GB (silebiliriz)
- `.nuget/` → ~2.8 GB (C# yoksa sil)
- Proje node_modules'leri temizlenebilir

---

## KALINAN YER - Glitch Code Rebrand (20 Haz 2026)

### Konum
`C:\Users\ErCuM\CascadeProjects\glitch-code` (WSL: `/mnt/c/.../glitch-code`)

### Yapılan Değişiklikler
1. **Tema** → `.mimocode/themes/glitch.json` (mor neon) + built-in `packages/opencode/src/cli/cmd/tui/context/theme/glitch.json`
2. **Provider** → `.mimocode/mimocode.jsonc`'de ollama provider eklendi (GlassesCat modelleri: V5, V7, V6, X_FABLE_CODER, Qwen, DeepSeek, Llama)
3. **Branding** → "MiMo Code" → "Glitch Code" (i18n tüm diller, footer, trust dialog, system prompt, logo.ts)
4. **TUI** → `.mimocode/tui.json` tema "glitch" olarak ayarlandı

### KALAN SORUN
- **API hatası**: "Cannot connect to API: Unable to connect..."
  - WSL'den `curl http://localhost:11434/api/tags` ile Ollama erişimi test edilecek
  - Ollama Windows'ta `ollama serve` ile çalıştırılacak
  - Sorun çözülünce `bun run dev` ile test

### Test Komutu
```bash
cd /mnt/c/Users/ErCuM/CascadeProjects/glitch-code
rm -rf .dev-home
bun run dev
```

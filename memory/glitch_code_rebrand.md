# Glitch Code Projesi - Durum

## Konum
- `C:\Users\ErCuM\CascadeProjects\glitch-code`
- GitHub: `https://github.com/glassesglitchstudio-lab/Gltich_code`

## Son Yapılanlar (22 Haz 2026) — NEXUS AUTO-PILOT PAKETİ

### 1. 🤖 `/help-the-model` — Model Router
**Tool:** `model-router.ts` | **Workflow:** `model-router.js`
- X_FABLE_CODER_V1 → birincil (Berkay'ın kişisel modeli)
- V7_HYBRID_TITAN → reasoning/security
- V6_OMNI_OVERLORD → 128K context
- V5_NEXUS_CORE → hızlı task'lar
- MiMo Auto → son çare fallback
- 3 mod: `auto` (otomatik) / `manual` (/help-the-model) / `swarm` (paralel)

### 2. 🔍 Auto-Supervision (4 Subagent)
**Tool:** `self-supervision.ts` (geliştirilmiş)
- `subagent-scan` → error/exception/crash pattern taraması
- `agent-flaws` → TODO, @ts-ignore, hardcoded, console.log
- `prompt-audit` → kısa/belirsiz prompt analizi
- `consistency-check` → plan vs çıktı tutarlılığı (YENİ!)

### 3. 🛠️ Self-Healing Loop
**Tool:** `self-healing.ts` | **Workflow:** `self-healing.js`
- Hata bul → Kök neden analizi → Fix üret → Uygula → Tekrar denetle
- Max 3 deneme, başaramazsa insana devreder

### 4. 📝 Code Review Memory
- Supervision sonuçları kaydedilir
- Aynı hata tekrarında uyarı verir

### 5. 📊 Pattern Learner
**Tool:** `pattern-learner.ts`
- Git history + kod tabanında tekrar eden kalıpları tarar
- Anti-pattern, duplicate code, style tutarsızlığı

### 6. 🎯 Smart Predict
**Tool:** `smart-predict.ts`
- Task öncesi süre/risk/öneri tahmini

### 7. 💾 Context Compressor
**Tool:** `context-compressor.ts`
- Uzun session'ları özetler, context tasarrufu

### 8. ⚡ GlassesCat Swarm Mode
**Workflow:** `swarm-mode.js`
- 3 model paralel: ultra / standard / lite
- AI Judge karşılaştırır, en iyisini seçer

### 9. ✅ DeepFileAnalysis FULL REWRITE — 10+ yeni özellik

### 10. 🇹🇷 Türkçe Dil Desteği — `tr.ts` 436 satır

## Kayıtlı Tool'lar (20 adet)
bash, read, write, edit, glob, grep, webfetch, websearch, actor, task, memory, skill, lsp, history, deep-file-analysis, self-supervision, model-router, self-healing, pattern-learner, smart-predict, context-compressor

## Kayıtlı Workflow'lar (4 adet)
deep-research, swarm-mode, model-router, self-healing

## Skills (.glitchcode/skills/) — 23 Haz 2026
Tüm GlassesCat tool'ları için SKILL.md eklendi:
- ✅ `model-router/SKILL.md` — Model yönlendirme talimatları
- ✅ `self-supervision/SKILL.md` — 4 modlu oto-denetim
- ✅ `self-healing/SKILL.md` — 4 aşamalı kendini iyileştirme
- ✅ `pattern-learner/SKILL.md` — 10 anti-pattern + duplicate tespiti
- ✅ `smart-predict/SKILL.md` — Süre/risk tahmin motoru
- ✅ `context-compressor/SKILL.md` — Session özetleme
- ✅ `deep-file-analysis/SKILL.md` — 10+ kategorili dosya analizi

AI artık system prompt'unda `<available_skills>` olarak tümünü görecek!

## v2.0.0 GlassesCat Edition — 23 Haz 2026
- 🎨 **Setup Wizard Modernize Edildi**: ASCII logo, animasyonlar, renkli arayüz
- 🖥️ **Yeni `glitch_kur.ps1`**: PowerShell tabanlı animasyonlu kurulum asistanı
- 🎬 **`glitch_kur.bat` Yenilendi**: Spinner, progress bar, renkli ASCII logo
- 🏷️ **GitHub Release v2.0.0**: https://github.com/glassesglitchstudio-lab/Gltich_code/releases/tag/v2.0.0

## CI/CD Fix (25 Haz 2026)

### Sorunlar ve Çözümleri
1. **Windows binary release'te yoktu** → `win32` vs `windows` path mismatch → matrix target'ları `windows-*` olarak değiştirildi
2. **`--single` cross-platform'da boş artifact üretiyordu** → `--target` flag ile doğru platform hedefleme eklendi
3. **`windows-arm64` fail** → `@opentui/core-win32-arm64` native modülü yok → matrix'ten çıkarıldı
4. **npm publish hatası** → version bump unutulmuş + `catalog:` protocol hatası
5. **macOS takılıyordu** → `timeout-minutes: 20` eklendi
6. **npm version_WRONG** → publish.ts build timestamp kullanıyor, package.json version'u kullanmalı

### v0.2.25 Durumu
- ✅ 11 platform build başarılı
- ✅ GitHub Release: 10 asset (linux, macos, windows tüm platformlar)
- ✅ npm publish başarılı (ama version `0.0.0-prod-*` olarak yayınlandı - düzeltilmeli)
- ✅ npm: `glitchcode-cli` paketi yayınlandı
- ✅ GitHub: https://github.com/glassesglitchstudio-lab/Gltich_code/releases/tag/v0.2.25

### README Güncellendi
- Kurulum talimatları eklendi (npm, GitHub Releases, kaynaktan)
- Gerçek indirme linkleri ve platform bazlı seçim rehberi

## Bulk Rename — mimo → glitch (26 Haz 2026)
**Durum**: ✅ TAMAMLANDI

### Yapılan Değişiklikler
1. **Package scope**: `@mimo-ai/*` → `@glitchcode/*` (146+ dosya)
2. **Config directory**: `.mimocode/` → `.glitchcode/` (52+ dosya)
3. **Env vars**: `MIMOCODE_*` → `GLITCHCODE_*` (96+ dosya)
4. **HTTP headers**: `x-mimocode-*` → `x-glitchcode-*` (8 dosya)
5. **DB/Config filenames**: `mimocode.db` → `glitchcode.db`, `mimocode.json` → `glitchcode.json` (60+ dosya)
6. **User-Agent**: `mimocode/` → `glitchcode/` (6 dosya)
7. **CLI commands**: i18n dosyalarında tüm `mimo` komutları `glitch` olarak değiştirildi (8 dil)
8. **Theme**: `mimocode.json` → `glitchcode.json` tema dosyası yeniden adlandırıldı
9. **Internal code**: Memory, MCP, Installation, Auth gibi modüllerdeki tüm iç referanslar güncellendi
10. **Bin/postinstall**: `.mimocode` cache → `.glitchcode`, duplicate variable fix
11. **Error messages**: "no providers found" → açıklayıcı mesajlar
12. **Auto-login dialog**: İlk açılışta provider yoksa otomatik login dialog'u açılıyor

### hariç tutulanlar (değişmedi):
- External API'ler: `mimo.xiaomi.com`, `api.xiaomimimo.com`, `platform.xiaomimimo.com`
- Model ID'leri: `mimo-auto`, `mimo-v2.5`, `mimo-v2.5-pro`, `mimo-v2.5-asr`
- OAuth: `MimoAuthPlugin`, `plugin/mimo.ts` (dış servis sözleşmesi)
- Provider ID: `"mimo"` (API-level contract)

## v0.2.26 — Local Build (26 Haz 2026)
- ✅ Local build başarılı (`bun run script/build.ts --single --target glitchcode-windows-x64 --skip-install`)
- ✅ Binary güncellendi: `C:\Users\ErCuM\.glitchcode\bin\glitch.exe`
- ✅ Version: `0.0.0-main-202606261105`
- ✅ Tüm branding düzeldi (glitchcode tui, glitchcode server, glitchcode.local)
- ✅ Provider'lar test edildi: MiMo, GitHub Copilot, Cloudflare mevcut
- ✅ `glitch models` 35 model gösteriyor
- ⚠️ Uyarı mesajında hâlâ "Opencode'dan base alınmıştır" yazıyor (atıf, kasıtlı)

## Provider Kurulum Rehberi
Kullanıcılar `glitch auth login` ile bağlanmalı:
- **MiMo**: Browser OAuth → otomatik
- **GitHub Copilot**: Device Code OAuth → GitHub'da onay
- **Cloudflare**: Env var gerekli (`CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_KEY`)

## Kalan İşler
- [x] ~~Startup wizard~~ ✅ v2.0.0'da yapıldı
- [x] ~~npm version fix~~ ✅ publish.ts doğru çalışıyor
- [ ] Obsidian Bridge Sync (ayrı proje olarak planlandı)
- [x] ~~`mimo` → `glitch` rename~~ ✅ v0.2.26'da yayınlandı
- [x] ~~Workflow dosyalarını npm package'a ekle~~ ✅ Zaten binary'ye embed ediliyor
- [x] ~~CI/CD Fix~~ ✅ v0.2.26 publish başarılı (10/10 build)
- [x] ~~Hata mesajları~~ ✅ Açıklayıcı mesajlar eklendi
- [x] ~~Auto-login dialog~~ ✅ İlk açılışta otomatik açılıyor
- [x] ~~Local build~~ ✅ Binary güncellendi

## v0.2.33 — T3-T8 + 5 Yeni Komut + Dokümantasyon (30 Haz 2026)

### Tamamlanan İşler
1. **T3: LLM Skorlama** — `parseLLMScore()` + `evaluateSolution()` LLM skorunu tercih ediyor
2. **T4: JSON Review** — 3 prompt JSON format, `parseReviewResponse()`, gerçek skorlar
3. **T5-T7: Testler** — 59 test, 85 assertion, 0 hata
4. **T8: Advisory** — README platform tablosu, build.ts warning
5. **5 Yeni Komut** — cost, changelog, replay, audit, bench
6. **Dokümantasyon** — CONTRIBUTING.md, ARCHITECTURE.md, README yeniden yazıldı

### CLI Değerlendirmesi
- **Genel**: 8.5/10
- **En güçlü**: PlusTwoCoder (9.5/10), Fix pipeline (9/10)
- **En zayıf**: Rate limiting, Test coverage, Plugin ekosistemi

### Publish
- v0.2.33: 10 platform, GitHub Actions başarılı
- npm: `glitchcode-cli@0.2.33`
- Binary kopyalandı: `.glitchcode/bin/glitch.exe`

### Pazarlama Notları
- PlusTwoCoder viral potansiyeli taşıyor
- 30sn video + Twitter postu yeterli
- Konukla video yapılması önerildi
- HN "Show HN" + Reddit postları planlandı

## v0.3.2 — TUI Visual Overhaul (18 Tem 2026)

### 7 Büyük Görsel Değişiklik TAMAMLANDI ✅
1. **Home Page** — GLITCH ASCII banner (block characters, theme.primary)
2. **Dialog Glassmorphism** — Tüm dialog'lara turuncu border glow
3. **Sidebar Collapsible** — Toggle (◀/▶), compact mod (6px), kv persistent
4. **Footer** — SessionFooter: dizin ●, durum (ready/thinking), model adı
5. **Prompt Glassmorphism** — Full border, glow animasyonu, Glitch adı, karakter sayacı
6. **Message Cards** — ▸ You / ◆ Glitch (zaten mevcuttu)
7. **Tool Output Cards** — Status-aware border (zaten mevcuttu)

### Prompt İyileştirmeleri
- Glow border animasyonu (0.5→0.7→1.0→0.7 nabız atışı)
- Türkçe placeholder: "Glitch'e sor...", "Ne yapmak istersin?"
- Sabit "Glitch" adı (agent.name yerine)
- Karakter sayacı: 0/128K, sarı >%70, kırmızı >%90
- `◆` model göstergesi

### Değişen Dosyalar
- `sidebar.tsx` — Collapsible toggle, compact mod
- `session/index.tsx` — sidebarCollapsed state, SessionFooter entegrasyonu
- `prompt/index.tsx` — Glow animasyonu, Glitch adı, karakter sayacı
- `session-footer.tsx` — Yeni dosya (status bar)

### Commit'ler
- `a2fc0bf` — collapsible sidebar + glassmorphism prompt + session footer
- `8804d52` — prompt area 7 iyileştirme
- `46021b4` — Glitch adı düzeltmesi

### Typecheck: 12/12 başarılı ✅

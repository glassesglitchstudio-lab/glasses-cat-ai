#!/bin/bash
# GlassesCat - Linux (Tablet) Otomasyon Kurulum Scripti
# Calistir: bash scripts/setup-linux.sh

set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo "========================================"
echo "  GlassesCat - Linux Kurulum"
echo "  Repo: $REPO_DIR"
echo "========================================"
echo ""

# 1. Post-commit hook (commit -> otomatik push)
echo "[1/3] Post-commit hook kuruluyor..."
HOOK_FILE="$REPO_DIR/.git/hooks/post-commit"
cat > "$HOOK_FILE" << 'HOOK'
#!/bin/bash
# GlassesCat - Otomatik push on commit
git push origin main 2>/dev/null || true
HOOK
chmod +x "$HOOK_FILE"
echo "  [OK] $HOOK_FILE"

# 2. Cron - 15dk'da bir otomatik pull
echo "[2/3] Cron job ekleniyor (15dk'da bir pull)..."
CRON_JOB="*/15 * * * * cd $REPO_DIR && git pull origin main 2>/dev/null >> /tmp/glassescat-sync.log"
(crontab -l 2>/dev/null | grep -v "glassescat-sync"; echo "$CRON_JOB") | crontab -
echo "  [OK] Cron eklendi"

# 3. Cron - 30dk'da bir otomatik backup commit + push
echo "[3/3] Auto-backup cron ekleniyor (30dk'da bir)..."
BACKUP_JOB="*/30 * * * * cd $REPO_DIR && git add -A && git commit -m \"auto-backup: \$(date '+%%Y-%%m-%%d %%H:%%M')\" 2>/dev/null && git push origin main 2>/dev/null >> /tmp/glassescat-backup.log"
(crontab -l 2>/dev/null | grep -v "glassescat-backup"; echo "$BACKUP_JOB") | crontab -
echo "  [OK] Auto-backup cron eklendi"

echo ""
echo "========================================"
echo "  KURULUM TAMAM!"
echo "========================================"
echo "  - Commit atinca -> otomatik push"
echo "  - Her 15dk'da bir -> otomatik pull"
echo "  - Her 30dk'da bir -> otomatik backup"
echo "========================================"
crontab -l | grep -E "glassescat"

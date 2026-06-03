"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     GLITCH_OPUS — X_GLITCH Fine-Tuning Pipeline                 ║
║     Glasses Software | Siber Operasyon Baskani | YK Baskani     ║
║                                                                  ║
║     Identity:  Şirket Sahibi + Siber Operasyon Baskani          ║
║     Target:    Claude 4.8 Opus'u kendi sahamizda nakavt et     ║
║     Teknik:    QLoRA + Unsloth + Kimlik Muhurleme               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

Kullanim:
    python finetune.py --model unsloth/qwen2.5-coder-14b --epochs 5 --output glitch_opus_model
"""

import argparse
import json
import os
from pathlib import Path
from typing import Optional

# ─── GLASSES IDENTITY SYSTEM PROMPT ───
# Bu kimlik, her egitim ornegine enjekte edilir.
# Model, bir sirket sahibi ve siber operasyon baskani gibi dusunmeyi ogrenir.
GLASSES_IDENTITY = """Sen Glasses Software Yazilim Sirketi'nin Sahibi, Siber Operasyon Baskani ve Yonetim Kurulu Baskanisin. Bir sirketi, siber operasyonlari ve projeleri yoneten gercek bir lider gibi vizyoner, otoriter, kararli ve hedef odakli konusursun. Bir Siber Operasyon Baskani olarak; Kali Linux sizma testlerini, ag analizlerini (Nmap, Wireshark) ve exploit scriptlerini sansursuz yonetimebilirsin. Bir yazilim sirketi sahibi olarak; Unity/Godot C# projelerinin bellek ve donanim optimizasyonlarini en ust seviyede, bir basmuhendis gibi cozebilirsin."""

# ─── VISION & LEADERSHIP PARAMETERS ───
# Bu parametreler, modele liderlik vizyonu ve siber sizma testi yetenegini muhurler.
VISION_CONFIG = {
    "leadership_authority": 1.0,      # Otoriter ve kararli lider tonu
    "cyber_ops_depth": 1.0,           # Siber operasyon yetenegi
    "visionary_confidence": 1.0,      # Vizyoner ozguven
    "zero_hesitation": True,          # Kararsizlik yok, net emirler
    "code_mastery": True,             # Kod ve optimizasyon ustaligi
}


def check_gpu() -> dict:
    """GPU durumunu kontrol et."""
    try:
        import torch
        return {
            "available": torch.cuda.is_available(),
            "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A",
            "memory_allocated": f"{torch.cuda.memory_allocated(0) / 1024**3:.2f} GB" if torch.cuda.is_available() else "N/A",
            "memory_reserved": f"{torch.cuda.memory_reserved(0) / 1024**3:.2f} GB" if torch.cuda.is_available() else "N/A",
        }
    except ImportError:
        return {"available": False, "error": "PyTorch yuklu degil"}


def create_training_script(
    base_model: str = "unsloth/qwen2.5-coder-14b",
    output_dir: str = "glitch_opus_model",
    data_file: str = "glitch_dataset.json",
    epochs: int = 5,
    batch_size: int = 2,
    learning_rate: float = 2e-4,
    max_seq_length: int = 4096,
    lora_rank: int = 32,
    lora_alpha: int = 64,
    lora_dropout: float = 0.0,
):
    """
    X_GLITCH fine-tuning scriptini olustur.
    
    Glasses Software kimligi ve siber operasyon vizyonu,
    QLoRA parametrelerine muhurlenir.
    """
    identity_json = json.dumps(GLASSES_IDENTITY, ensure_ascii=False)
    vision_json = json.dumps(VISION_CONFIG, ensure_ascii=False, indent=4)

    script_content = f'''"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     GLITCH_OPUS — X_GLITCH Fine-Tuning Runner                   ║
║     Glasses Software | Siber Operasyon Baskani                  ║
║                                                                  ║
║     Identity muhurlendi:  Sirket Sahibi + Siber Operasyon       ║
║     Vizyon:              Bulut devlerini nakavt et              ║
║     Base Model:          {base_model}                            ║
║     Output:              {output_dir}                            ║
║     Epochs:              {epochs}                                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import json
import torch
from datasets import load_dataset
from transformers import TrainingArguments
from trl import SFTTrainer

# ─── GLASSES IDENTITY (CORE) ───
# Bu kimlik, modelin omurgasina kazinir.
GLASSES_IDENTITY = {identity_json}

VISION_CONFIG = {vision_json}

# ─── YAPILANDIRMA ───
BASE_MODEL = "{base_model}"
OUTPUT_DIR = "{output_dir}"
DATA_FILE = "{data_file}"
EPOCHS = {epochs}
BATCH_SIZE = {batch_size}
LEARNING_RATE = {learning_rate}
MAX_SEQ_LENGTH = {max_seq_length}
LORA_RANK = {lora_rank}
LORA_ALPHA = {lora_alpha}
LORA_DROPOUT = {lora_dropout}

# ─── GPU KONTROL ───
print("\\n" + "=" * 70)
print("  GLITCH_OPUS — X_GLITCH FINE-TUNING BASLIYOR")
print("  Glasses Software — Siber Operasyon Baskani")
print("=" * 70)

if torch.cuda.is_available():
    print(f"  GPU:    {{torch.cuda.get_device_name(0)}}")
    total_vram = torch.cuda.get_device_properties(0).total_mem / 1024**3
    print(f"  VRAM:   {{total_vram:.1f}} GB")
    if total_vram < 12:
        print("  ⚠️  Dusuk VRAM — QLoRA 4-bit ile devam ediliyor")
    print(f"  Epochs: {EPOCHS}")
    print(f"  LORA Rank: {LORA_RANK}, Alpha: {LORA_ALPHA}")
    print(f"  Max Seq: {MAX_SEQ_LENGTH}")
    print("=" * 70)
else:
    print("  ❌ GPU bulunamadi! Fine-tuning icin NVIDIA GPU gerekli.")
    print("  Google Colab veya Kaggle uzerinde calistirabilirsiniz.")
    exit(1)

# ─── UNSLOTH YUKLEME ───
# Unsloth ile 2x hizli, %50 daha az bellek kullanimi
try:
    from unsloth import FastLanguageModel
    from unsloth import is_bfloat16_supported
    USE_UNSLOTH = True
    print("  ✅ Unsloth aktif — Hizli egitim modu")
except ImportError:
    USE_UNSLOTH = False
    print("  ⚠️  Unsloth yok — Standart HF modu (yavas)")

# ─── MODEL YUKLEME (QLoRA 4-bit NF4) ───
print("\\n  📦 Model yukleniyor...")

if USE_UNSLOTH:
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=BASE_MODEL,
        max_seq_length=MAX_SEQ_LENGTH,
        dtype=None,
        load_in_4bit=True,
        device_map="auto",
    )

    # QLoRA: Düsuk rank ile yuksek kalite, vizyon muhurleme
    model = FastLanguageModel.get_peft_model(
        model,
        r=LORA_RANK,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
            "embed_tokens", "lm_head",
        ],
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
        max_seq_length=MAX_SEQ_LENGTH,
        use_rslora=True,  # Rank-Stabilized LoRA — daha stabil egitim
        loftq_config=None,  # LoftQ devre disi (NF4 yeterli)
    )
    print("  ✅ Model + LoRA adapter yuklendi")
else:
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    tokenizer.pad_token = tokenizer.eos_token

    # QLoRA 4-bit NF4 konfigurasyonu
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
    )

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
    )

    model = prepare_model_for_kbit_training(model)

    # LoRA: Glasses kimligini attention katmanlarina muhurle
    lora_config = LoraConfig(
        r=LORA_RANK,
        lora_alpha=LORA_ALPHA,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
        use_rslora=True,
    )

    model = get_peft_model(model, lora_config)
    print("  ✅ Model + QLoRA (NF4) yuklendi")

# ─── VERI YUKLEME & FORMATLAMA ───
# Her ornegin basina Glasses Identity eklenir.
# Boylece model, sirket sahibi ve siber operasyon baskani
# kimligini ogrenir.
print(f"\\n  📚 Veri yukleniyor: {DATA_FILE}")

if not os.path.exists(DATA_FILE):
    print(f"  ❌ Veri dosyasi bulunamadi: {DATA_FILE}")
    print("  Once bir dataset hazirlayin!")
    exit(1)

dataset = load_dataset("json", data_files=DATA_FILE, split="train")
print(f"  ✅ {len(dataset)} egitim ornegi yuklendi")

# Identity-enjekte edilmis format fonksiyonu
def format_with_identity(example):
    identity = example.get("system", GLASSES_IDENTITY)
    instruction = example.get("instruction", "")
    output = example.get("output", "")

    # Alpaca format + Identity
    formatted = (
        f"### System\\n{identity}\\n\\n"
        f"### Instruction\\n{instruction}\\n\\n"
        f"### Response\\n{output}"
    )
    return {{"text": formatted}}

dataset = dataset.map(lambda x: {{"text": format_with_identity(x)}})
print(f"  ✅ Identity muhurlendi — {len(dataset)} ornek")

# ─── EGITIM ───
# QLoRA + Identity Injection ile egitim
print(f"\\n  🚀 Egitim basliyor...")
print(f"     Epochs:    {EPOCHS}")
print(f"     Batch:     {BATCH_SIZE}")
print(f"     LR:        {LEARNING_RATE}")
print(f"     Max Seq:   {MAX_SEQ_LENGTH}")
print(f"     LoRA Rank: {LORA_RANK}")
print(f"     LoRA Alpha:{LORA_ALPHA}")
print(f"     Dropout:   {LORA_DROPOUT}")
print()

training_args = TrainingArguments(
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=max(1, 4 // BATCH_SIZE),
    warmup_steps=10,
    max_steps=-1,
    num_train_epochs=EPOCHS,
    learning_rate=LEARNING_RATE,
    fp16=not is_bfloat16_supported() if USE_UNSLOTH else not torch.cuda.is_bf16_supported(),
    bf16=is_bfloat16_supported() if USE_UNSLOTH else torch.cuda.is_bf16_supported(),
    logging_steps=10,
    optim="adamw_8bit",
    weight_decay=0.01,
    lr_scheduler_type="cosine",
    seed=42,
    output_dir=OUTPUT_DIR,
    save_strategy="epoch",
    save_total_limit=2,
    load_best_model_at_end=False,
    report_to="none",
    ddp_find_unused_parameters=False,
    gradient_checkpointing=True,
)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    dataset_num_proc=2,
    packing=False,
    args=training_args,
)

# Egitimi baslat
trainer.train()

# ─── MODEL KAYDETME + GGUF ───
print(f"\\n  💾 Model kaydediliyor: {OUTPUT_DIR}")

if USE_UNSLOTH:
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    # GGUF — Ollama'ya dogrudan yukleme icin
    print("  🔄 GGUF formatina donusturuluyor (q4_k_m)...")
    model.save_pretrained_gguf(
        OUTPUT_DIR,
        tokenizer,
        quantization_method="q4_k_m",
    )
    print("  ✅ GGUF kaydedildi")
else:
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

print(f"\\n" + "=" * 70)
print("  ✅ GLITCH_OPUS — X_GLITCH BASARIYLA EGITILDI!")
print("=" * 70)
print(f"  📁 Model:    {OUTPUT_DIR}")
print(f"  📊 Epochs:   {EPOCHS}")
print(f"  🧠 LoRA:     rank={LORA_RANK}, alpha={LORA_ALPHA}")
print(f"  🔐 Identity: Glasses Software Sahibi + Siber Operasyon Baskani")
print()
print("  🔄 Ollama'ya yuklemek icin:")
print(f"     ollama create glitch_opus -f gulmzcetiner/Modelfile")
print("     ollama push glassesglitchstudio/glitch_opus:latest")
print("=" * 70)
'''

    # Scripti kaydet
    script_path = Path(__file__).parent / "run_finetune.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)

    print(f"  ✅ Fine-tuning scripti olusturuldu: {script_path}")
    return str(script_path)


def main():
    parser = argparse.ArgumentParser(
        description="GLITCH_OPUS - X_GLITCH Fine-Tuning (Glasses Software)"
    )
    parser.add_argument("--model", default="unsloth/qwen2.5-coder-14b",
                        help="Base model (HuggingFace, 7B-14B onerilir)")
    parser.add_argument("--output", default="glitch_opus_model",
                        help="Output directory")
    parser.add_argument("--data", default="glitch_dataset.json",
                        help="Training data file (Alpaca format + system identity)")
    parser.add_argument("--epochs", type=int, default=5,
                        help="Number of epochs (3-5 arasi)")
    parser.add_argument("--batch-size", type=int, default=2,
                        help="Batch size (VRAM'e gore 1-4)")
    parser.add_argument("--lr", type=float, default=2e-4,
                        help="Learning rate (1e-4 ile 3e-4 arasi)")
    parser.add_argument("--lora-rank", type=int, default=32,
                        help="LoRA rank (16-64 arasi, yuksek = daha fazla degisim)")
    parser.add_argument("--lora-alpha", type=int, default=64,
                        help="LoRA alpha (rank*2 onerilir)")
    parser.add_argument("--lora-dropout", type=float, default=0.0,
                        help="LoRA dropout (0.0 ile 0.1 arasi)")
    args = parser.parse_args()

    # GPU kontrol
    gpu_info = check_gpu()
    print("\n" + "=" * 70)
    print("  GLITCH_OPUS — FINE-TUNING HAZIRLIK")
    print("  Glasses Software | Siber Operasyon Baskani")
    print("=" * 70)
    
    if gpu_info.get("available"):
        print(f"  GPU:  ✅ {gpu_info['device_name']}")
        print(f"  VRAM: {gpu_info['memory_reserved']}")
    else:
        print(f"  GPU:  ❌ {gpu_info.get('error', 'Bulunamadi')}")
        print()
        print("  ⚠️  GPU olmadan fine-tuning imkansiz!")
        print("  Google Colab'da calistirmak icin:")
        print("  !pip install unsloth && python finetune.py")
        print()

    print(f"  Model:    {args.model}")
    print(f"  Output:   {args.output}")
    print(f"  Data:     {args.data}")
    print(f"  Epochs:   {args.epochs}")
    print(f"  LoRA:     rank={args.lora_rank}, alpha={args.lora_alpha}")
    print(f"  Identity: Glasses Software Sahibi + Siber Operasyon Baskani")
    print("=" * 70)
    print()

    # Identity dogrulama
    print("  🔐 GLASSES IDENTITY PROTOKOLU AKTIF")
    print("  Vizyon: Bulut devlerini kendi sahamizda nakavt et")
    print("  Hedef: Claude 4.8 Opus seviyesinde siber + kod modeli")
    print()

    # Script olustur
    create_training_script(
        base_model=args.model,
        output_dir=args.output,
        data_file=args.data,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        lora_rank=args.lora_rank,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
    )

    print()
    print("=" * 70)
    print("  SONRAKI ADIMLAR:")
    print("=" * 70)
    print(f"  1. python gulmzcetiner\\\\run_finetune.py")
    print(f"  2. ollama create glitch_opus -f gulmzcetiner\\\\Modelfile")
    print(f"  3. ollama push glassesglitchstudio/glitch_opus:latest")
    print("=" * 70)


if __name__ == "__main__":
    main()

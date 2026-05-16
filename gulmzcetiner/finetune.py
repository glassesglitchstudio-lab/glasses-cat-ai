"""
GulmezCetinerMax - Fine-Tuning Pipeline
Glassescat Software | CEO: Berkay

Bu script, GulmezCetinerMax modelini fine-tune etmek icin kullanilir.
Unsloth veya Hugging Face TRL ile calisir.

Gereksinimler:
    pip install torch transformers trl peft accelerate bitsandbytes datasets

Kullanim:
    python finetune.py --model qwen2.5-coder:14b --epochs 3 --output gulmzcetinermax_model
"""

import argparse
import json
import os
from pathlib import Path
from typing import Optional


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
    output_dir: str = "gulmzcetinermax_model",
    data_file: str = "gulmzcetinermax_train.json",
    epochs: int = 3,
    batch_size: int = 2,
    learning_rate: float = 2e-4,
    max_seq_length: int = 2048,
    lora_rank: int = 16,
):
    """
    Fine-tuning scriptini olustur.
    
    Args:
        base_model: Temel model (Hugging Face)
        output_dir: Cikti dizini
        data_file: Egitim veri dosyasi
        epochs: Egitim epoch sayisi
        batch_size: Batch boyutu
        learning_rate: Ogrenme orani
        max_seq_length: Maksimum siralama uzunlugu
        lora_rank: LoRA rank
    """

    script_content = f'''"""
GulmezCetinerMax - Fine-Tuning Script
Otomatik olusturuldu - Glassescat Software

Base Model: {base_model}
Output: {output_dir}
Epochs: {epochs}
"""

import os
import torch
from datasets import load_dataset
from transformers import TrainingArguments
from trl import SFTTrainer

# Unsloth import (varsa)
try:
    from unsloth import FastLanguageModel
    USE_UNSLOTH = True
    print("✅ Unsloth bulundu - Hizli egitim modu aktif!")
except ImportError:
    USE_UNSLOTH = False
    print("⚠️ Unsloth bulunamadi - Standart egitim modu")

# ─── YAPILANDIRMA ───
BASE_MODEL = "{base_model}"
OUTPUT_DIR = "{output_dir}"
DATA_FILE = "{data_file}"
EPOCHS = {epochs}
BATCH_SIZE = {batch_size}
LEARNING_RATE = {learning_rate}
MAX_SEQ_LENGTH = {max_seq_length}
LORA_RANK = {lora_rank}

# ─── GPU KONTROL ───
print("\\n" + "="*60)
print("GULMEZCETINERMAX - FINE-TUNING BASLIYOR")
print("="*60)

if torch.cuda.is_available():
    print(f"✅ GPU: {{torch.cuda.get_device_name(0)}}")
    print(f"   VRAM: {{torch.cuda.get_device_properties(0).total_mem / 1024**3:.1f}} GB")
else:
    print("⚠️ GPU bulunamadi - CPU uzerinde calisacak (cok yavas!)")

# ─── MODEL YUKLEME ───
if USE_UNSLOTH:
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=BASE_MODEL,
        max_seq_length=MAX_SEQ_LENGTH,
        dtype=None,
        load_in_4bit=True,
    )

    # LoRA ayarlari
    model = FastLanguageModel.get_peft_model(
        model,
        r=LORA_RANK,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        lora_alpha=LORA_RANK,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )
else:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16,
        device_map="auto",
        load_in_4bit=True,
    )

    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=LORA_RANK,
        lora_alpha=LORA_RANK,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0,
        bias="none",
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, lora_config)

# ─── VERİ YUKLEME ───
print(f"\\n📚 Veri yukleniyor: {{DATA_FILE}}")

if not os.path.exists(DATA_FILE):
    print(f"❌ Veri dosyasi bulunamadi: {{DATA_FILE}}")
    print("   Once 'python data_prep.py' komutunu calistirin!")
    exit(1)

dataset = load_dataset("json", data_files=DATA_FILE, split="train")

# Alpaca formatini metne cevir
def format_example(example):
    instruction = example.get("instruction", "")
    input_text = example.get("input", "")
    output = example.get("output", "")

    if input_text:
        return f"### Instruction:\\n{{instruction}}\\n\\n### Input:\\n{{input_text}}\\n\\n### Response:\\n{{output}}"
    else:
        return f"### Instruction:\\n{{instruction}}\\n\\n### Response:\\n{{output}}"

dataset = dataset.map(lambda x: {{"text": format_example(x)}})

print(f"✅ {{len(dataset)}} egitim ornegi yuklendi")

# ─── EGİTİM ───
print(f"\\n🚀 Egitim basliyor...")
print(f"   Epochs: {{EPOCHS}}")
print(f"   Batch Size: {{BATCH_SIZE}}")
print(f"   Learning Rate: {{LEARNING_RATE}}")
print(f"   Max Seq Length: {{MAX_SEQ_LENGTH}}")

gradient_accumulation_steps = max(1, 4 // BATCH_SIZE)
total_steps = (len(dataset) * EPOCHS) // (BATCH_SIZE * gradient_accumulation_steps)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    dataset_num_proc=2,
    packing=False,
    args=TrainingArguments(
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=gradient_accumulation_steps,
        warmup_steps=5,
        max_steps=total_steps if total_steps > 0 else 100,
        learning_rate=LEARNING_RATE,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=10,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=42,
        output_dir=OUTPUT_DIR,
        save_strategy="epoch",
        save_total_limit=2,
        report_to="none",
    ),
)

# Egitimi baslat
trainer.train()

# ─── MODEL KAYDETME ───
print(f"\\n💾 Model kaydediliyor: {{OUTPUT_DIR}}")

if USE_UNSLOTH:
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    # GGUF formatinda da kaydet
    model.save_pretrained_gguf(
        OUTPUT_DIR,
        tokenizer,
        quantization_method="q4_k_m",
    )
else:
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

print(f"\\n✅ GulmezCetinerMax modeli basariyla egitildi!")
print(f"📁 Model dizini: {{OUTPUT_DIR}}")
print(f"\\n🔄 Ollama'ya yuklemek icin:")
print(f"   1. python convert_to_gguf.py --model {{OUTPUT_DIR}}")
print(f"   2. ollama create gulmzcetinermax -f gulmzcetiner/Modelfile")
'''

    # Scripti kaydet
    script_path = Path(__file__).parent / "run_finetune.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)

    print(f"✅ Fine-tuning scripti olusturuldu: {script_path}")
    return str(script_path)


def main():
    parser = argparse.ArgumentParser(description="GulmezCetinerMax Fine-Tuning")
    parser.add_argument("--model", default="unsloth/qwen2.5-coder-14b", help="Base model")
    parser.add_argument("--output", default="gulmzcetinermax_model", help="Output directory")
    parser.add_argument("--data", default="gulmzcetinermax_train.json", help="Data file")
    parser.add_argument("--epochs", type=int, default=3, help="Number of epochs")
    parser.add_argument("--batch-size", type=int, default=2, help="Batch size")
    parser.add_argument("--lr", type=float, default=2e-4, help="Learning rate")
    args = parser.parse_args()

    # GPU kontrol
    gpu_info = check_gpu()
    print("\n" + "="*60)
    print("GULMEZCETINERMAX - FINE-TUNING HAZIRLIK")
    print("="*60)
    print(f"GPU: {'✅ ' + gpu_info.get('device_name', 'N/A') if gpu_info.get('available') else '❌ GPU bulunamadi'}")

    if not gpu_info.get('available'):
        print("\n⚠️ GPU bulunamadi! Fine-tuning icin NVIDIA GPU gerekli.")
        print("   Google Colab veya Kaggle uzerinde calistirabilirsiniz.")
        print("   Veya script olusturup baska bir makinede calistirin.")

    # Script olustur
    create_training_script(
        base_model=args.model,
        output_dir=args.output,
        data_file=args.data,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
    )

    print("\n" + "="*60)
    print("SONRAKI ADIMLAR:")
    print("="*60)
    print("1. python data_prep.py          # Veri hazirla")
    print("2. python run_finetune.py        # Fine-tuning baslat")
    print("3. python convert_to_gguf.py     # GGUF'e donustur")
    print("4. ollama create gulmzcetinermax -f Modelfile  # Ollama'ya yukle")


if __name__ == "__main__":
    main()

"""Build tiny random-weight chat models for CPU tests and dry runs. No download needed.

The tokenizer is a small BPE trained on FinQA text with a ChatML template like Qwen's, so the
prompt, chat-template, completion-only-loss and generation code paths are the real ones.
Usage: python -m finqa_lora.tiny <out_dir>
"""
import sys
from pathlib import Path

from tokenizers import Tokenizer, models, pre_tokenizers, decoders, trainers
from transformers import PreTrainedTokenizerFast

from finqa_lora.data import load_split
from finqa_lora.prompt import SYSTEM

CHATML = (
    "{% for m in messages %}<|im_start|>{{ m['role'] }}\n{{ m['content'] }}<|im_end|>\n{% endfor %}"
    "{% if add_generation_prompt %}<|im_start|>assistant\n{% endif %}"
)
SPECIAL = ["<|endoftext|>", "<|im_start|>", "<|im_end|>"]


def build_tokenizer(out):
    texts = [SYSTEM]
    for ex in load_split("train")[:1500]:
        texts += [t for _, t in ex["qa"]["model_input"]] + [ex["qa"]["question"], ex["qa"]["program"]]
    tk = Tokenizer(models.BPE())
    tk.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tk.decoder = decoders.ByteLevel()
    tk.train_from_iterator(texts, trainers.BpeTrainer(vocab_size=2000, special_tokens=SPECIAL,
                                                      initial_alphabet=pre_tokenizers.ByteLevel.alphabet()))
    tok = PreTrainedTokenizerFast(tokenizer_object=tk, eos_token="<|im_end|>", pad_token="<|endoftext|>")
    tok.chat_template = CHATML
    tok.save_pretrained(out)
    return tok


def build(out, family="qwen2"):
    from transformers import AutoConfig, AutoModelForCausalLM
    out = Path(out)
    tok = build_tokenizer(out)
    cfg = AutoConfig.for_model(family, vocab_size=len(tok), hidden_size=64, intermediate_size=128,
                               num_hidden_layers=2, num_attention_heads=4, num_key_value_heads=2,
                               max_position_embeddings=2048, eos_token_id=tok.eos_token_id,
                               pad_token_id=tok.pad_token_id, tie_word_embeddings=True)
    model = AutoModelForCausalLM.from_config(cfg)
    model.generation_config.eos_token_id = tok.eos_token_id
    model.generation_config.pad_token_id = tok.pad_token_id
    model.save_pretrained(out)
    return out


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "qwen2")

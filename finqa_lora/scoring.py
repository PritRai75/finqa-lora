"""Score predicted programs with the official FinQA code, unchanged.

The official evaluate.py is vendored in third_party/finqa_official and loaded by file path,
so it cannot clash with the Hugging Face `evaluate` package. Two behaviours of the official
evaluate_result() are kept apart here on purpose:
  - execution accuracy: the program must run (invalid flag 0) and its result, rounded to 5
    decimals by the official code, must equal exe_ans exactly;
  - program accuracy: symbolic equality with the gold program (official equal_program).
The official loop asserts that symbolically equal programs execute to the same value. This
wrapper does not assert, so one odd prediction cannot stop a scoring run.
"""
import contextlib
import importlib.util
import io

from finqa_lora import REPO_ROOT

_PATH = REPO_ROOT / "third_party" / "finqa_official" / "evaluate.py"
_spec = importlib.util.spec_from_file_location("finqa_official_evaluate", _PATH)
official = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(official)


def tokenize(program):
    """'subtract(5829, 5735), divide(#0, 5735)' -> official token list ending in 'EOF'."""
    return official.program_tokenization(program)


def execute(program, table):
    """Run a program string. Returns (ok, value); value is a float rounded to 5 places, 'yes'/'no', or None."""
    invalid, value = official.eval_program(tokenize(program), table)
    if invalid or value == "n/a":
        return False, None
    return True, value


def exe_correct(program, example):
    ok, value = execute(program, example["table"])
    return ok and value == example["qa"]["exe_ans"]


def prog_correct(program, example):
    gold = tokenize(example["qa"]["program"])
    with contextlib.redirect_stdout(io.StringIO()):  # official code prints "structure error"
        try:
            return bool(official.equal_program(gold, tokenize(program)))
        except Exception:
            return False

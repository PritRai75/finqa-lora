"""One prompt format for training, zero-shot and few-shot inference.

The model sees FinQA's `model_input` facts (gold facts plus distractors in train, the paper's
retriever top 3 in dev and test) and the question, and replies with a program on one line.
Training uses the same messages as inference, so the only difference between the base and the
fine-tuned model is the weights.
"""
import re

SYSTEM = (
    "You answer questions about a company's financial report by writing a program that a calculator runs.\n"
    "Operations with two arguments: add, subtract, multiply, divide, exp, greater.\n"
    "Operations over a table row: table_sum, table_average, table_max, table_min, written as "
    "table_average(row name, none).\n"
    "An argument is a number copied from the facts, a constant such as const_100 or const_1000, "
    "or #n for the result of step n, counting from 0.\n"
    "Reply with the program only, on one line, for example: subtract(5829, 5735), divide(#0, 5735)"
)

# Train items the screen marks `agree`, one per common program shape. Fixed so every few-shot
# run sees the same examples; none of them is in dev or test.
FEW_SHOT_IDS = (
    "KMI/2014/page_114.pdf-2",   # subtract, divide
    "APD/2017/page_37.pdf-2",    # table_average
    "DVN/2014/page_88.pdf-1",    # add, divide, multiply by const_100
    "ECL/2017/page_85.pdf-4",    # greater
)

# Bump PROMPT_VERSION with any change to the prompt; tests/test_prompt.py pins the fingerprint,
# so an edit fails the tests until the version and the pinned value are updated together.
PROMPT_VERSION = 1


def prompt_fingerprint():
    """12-character hash of everything that shapes a prompt: system text, shots and the user layout."""
    import hashlib
    probe = {"qa": {"model_input": [["text_0", "FACT_A"], ["table_1", "FACT_B"]], "question": "QUESTION",
                    "program": "PROGRAM"}}
    material = repr((PROMPT_VERSION, SYSTEM, FEW_SHOT_IDS, messages(probe, [probe])))
    return hashlib.sha256(material.encode()).hexdigest()[:12]


OPS = ("add", "subtract", "multiply", "divide", "exp", "greater",
       "table_sum", "table_average", "table_max", "table_min")
_STEP = re.compile(r"\b(" + "|".join(OPS) + r")\(([^()]*)\)")


def user_text(ex):
    facts = "\n".join(f"- {text}" for _, text in ex["qa"]["model_input"])
    return f"Facts:\n{facts}\n\nQuestion: {ex['qa']['question']}"


def target(ex):
    return ex["qa"]["program"]


def messages(ex, shots=()):
    """Chat messages up to and including the user turn for `ex`."""
    msgs = [{"role": "system", "content": SYSTEM}]
    for s in shots:
        msgs.append({"role": "user", "content": user_text(s)})
        msgs.append({"role": "assistant", "content": target(s)})
    msgs.append({"role": "user", "content": user_text(ex)})
    return msgs


def few_shot_examples(train):
    by_id = {ex["id"]: ex for ex in train}
    return [by_id[i] for i in FEW_SHOT_IDS]


def extract_program(text):
    """Model reply -> program string in FinQA syntax, or '' if no step is found.

    Takes the steps from the first line that has any, so trailing chatter is ignored.
    Arithmetic arguments are re-joined with ', ' because the official tokenizer splits on it.
    """
    for line in str(text).splitlines():
        steps = _STEP.findall(line)
        if not steps:
            continue
        out = []
        for op, inner in steps:
            args = [" ".join(a.split()) for a in inner.split(",")]
            out.append(f"{op}({', '.join(args)})")
        return ", ".join(out)
    return ""

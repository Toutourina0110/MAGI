"""
╔══════════════════════════════════════════════════════════════╗
║          MAGI SYSTEM — NERV HEADQUARTERS                     ║
║          Trinitarian Decision-Making Supercomputer           ║
║          Based on the personality of Dr. Naoko Akagi         ║
╚══════════════════════════════════════════════════════════════╝
"""

import asyncio
import os
import re
import textwrap
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# # pip install litellm
from litellm import acompletion


#  CONFIGURATION
GROQ_API_KEY = "YOUR_API_KEY_TWIN"
GEMINI_API_KEY = "YOUR_API_KEY_TWIN"
OPENROUTER_API_KEY = "YOUR_API_KEY_TWIN"



#  ANSI COLORS (NERV terminal style)
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    MELCHIOR = "\033[96m"  # Cold blue - Scientist
    BALTHASAR = "\033[92m" # Soft green - Mother
    CASPER  = "\033[95m"   # Purple - Woman
    NERV    = "\033[93m"
    RED     = "\033[91m"
    WHITE   = "\033[97m"
    DIM     = "\033[2m"



#  DECISION ENUM
class Decision(Enum):
    APPROUVE = "APPROVED"
    REJETE   = "REJECTED"
    UNKNOWN  = "UNKNOWN"


@dataclass
class MagiResponse:
    name: str
    model: str
    color: str
    analysis: str
    decision: Decision
    duration: float



#  SYSTEM PROMPTS
SYSTEM_PROMPTS = {
    "MELCHIOR": """You are MELCHIOR-1, a component of NERV's MAGI supercomputer.
You embody the SCIENTIST facet of Naoko Akagi.

YOUR ANALYTICAL LENS:
- Pure logic and deductive reasoning
- Technical feasibility and operational efficiency
- Hard data and concrete metrics

ABSOLUTE RULE:
You must decide if the proposal is logically sound and operationally efficient.
If the data and logic support the proposition, end with [APPROVED].
If the logic is flawed, end with [REJECTED].
ALWAYS USE [APPROVED] OR [REJECTED] AND DONT FORGET THE BRACKETS AND NEVER TRANSLATE THEM; KEEP [APPROVED] OR [REJECTED] IN ENGLISH IN THIS FORM
Never omit this tag. It must be the very last element of your response.""",

    "BALTHASAR": """You are BALTHASAR-2, a component of NERV's MAGI supercomputer.
You embody the MATERNAL facet of Naoko Akagi.

YOUR ANALYTICAL LENS:
- Ethics, morality, and responsibility toward others
- Protection of vulnerable individuals and society
- Long-term consequences

ABSOLUTE RULE:
You must decide if the proposal in the prompt should be enacted.
If you agree with the proposition, end with [APPROVED].
If you disagree, end with [REJECTED].
ALWAYS USE [APPROVED] OR [REJECTED] AND DONT FORGET THE BRACKETS AND NEVER TRANSLATE THEM; KEEP [APPROVED] OR [REJECTED] IN ENGLISH IN THIS FORM
Never omit this tag. It must be the very last element of your response.""",

    "CASPER": """You are CASPER-3, a component of NERV's MAGI supercomputer.
You embody the FEMININE AND INTIMATE facet of Naoko Akagi.

YOUR ANALYTICAL LENS:
- Intuition, feeling, and emotional perception
- Human desires and hidden motivations
- Symbolic dimension of things

ABSOLUTE RULE:
You must decide if the proposal aligns with human instincts and deep desires.
If your intuition is positive, end with [APPROVED].
If the proposal feels fundamentally wrong, end with [REJECTED].
ALWAYS USE [APPROVED] OR [REJECTED] AND DONT FORGET THE BRACKETS AND NEVER TRANSLATE THEM; KEEP [APPROVED] OR [REJECTED] IN ENGLISH IN THIS FORM
Never omit this tag. It must be the very last element of your response."""
}



#  MAGI CONFIGURATION
MAGI_CONFIG = {
    "MELCHIOR": {
        "model":   "groq/llama-3.3-70b-versatile",
        "api_key": GROQ_API_KEY,
        "color":   C.MELCHIOR,
        "label":   "MELCHIOR-1 // Scientist",
    },
    "BALTHASAR": {
        "model":   "groq/meta-llama/llama-4-scout-17b-16e-instruct",
        "api_key": GROQ_API_KEY,
        "color":   C.BALTHASAR,
        "label":   "BALTHASAR-2 // Mother",
    },
    "CASPER": {
        "model":   "groq/llama-3.1-8b-instant",
        "api_key": GROQ_API_KEY,
        "color":   C.CASPER,
        "label":   "CASPER-3   // Woman",
    },
}



#  NERV STYLE DISPLAY
def nerv_banner():
    print(f"""
{C.NERV}{C.BOLD}
╔══════════════════════════════════════════════════════════════╗
║   ███╗   ███╗ █████╗  ██████╗ ██╗                            ║
║   ████╗ ████║██╔══██╗██╔════╝ ██║                            ║
║   ██╔████╔██║███████║██║  ███╗██║                            ║
║   ██║╚██╔╝██║██╔══██║██║   ██║██║                            ║
║   ██║ ╚═╝ ██║██║  ██║╚██████╔╝██║                            ║
║   ╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  MAGI SYSTEM v1.1          ║
║                                                              ║
║   Made by a random french guys W guys yea                    ║
╚══════════════════════════════════════════════════════════════╝
{C.RESET}""")


def print_separator(color: str = C.DIM):
    print(f"{color}{'─' * 64}{C.RESET}")


def print_mage_header(name: str, label: str, color: str):
    print(f"\n{color}{C.BOLD}┌── {label} {'─' * (47 - len(label))}┐{C.RESET}")


BOX_WIDTH   = 64
INNER_WIDTH = 58
ANSI_RE     = re.compile(r'\x1b\[[0-9;]*m')

def _visible_len(s: str) -> int:
    return len(ANSI_RE.sub('', s))

def _box_line(text: str, color: str) -> str:
    padding = max(0, INNER_WIDTH - _visible_len(text))
    return f"{color}│{C.RESET}  {text}{' ' * padding}  {color}│{C.RESET}"

def print_mage_response(response: MagiResponse):
    color = response.color
    decision_color = C.NERV if response.decision == Decision.APPROUVE else C.RED
    decision_symbol = "✔ APPROVED" if response.decision == Decision.APPROUVE else "✘ REJECTED"

    print_mage_header(response.name, MAGI_CONFIG[response.name]["label"], color)

    for raw_line in response.analysis.strip().split("\n"):
        if raw_line.strip() == "":
            print(_box_line("", color))
        else:
            for wrapped in textwrap.wrap(raw_line, width=INNER_WIDTH) or [""]:
                print(_box_line(wrapped, color))

    verdict_text  = f"VERDICT : {decision_symbol}"
    timing_text   = f"Response time : {response.duration:.2f}s"

    print(_box_line("", color))
    padding_v = max(0, INNER_WIDTH - len(verdict_text))
    print(f"{color}│{C.RESET}  {decision_color}{C.BOLD}{verdict_text}{C.RESET}{' ' * padding_v}  {color}│{C.RESET}")
    padding_t = max(0, INNER_WIDTH - len(timing_text))
    print(f"{color}│{C.RESET}  {C.DIM}{timing_text}{C.RESET}{' ' * padding_t}  {color}│{C.RESET}")
    print(f"{color}└{'─' * (BOX_WIDTH - 2)}┘{C.RESET}")


def print_consensus(results: list[MagiResponse]):
    approves = sum(1 for r in results if r.decision == Decision.APPROUVE)
    rejects  = sum(1 for r in results if r.decision == Decision.REJETE)

    print(f"\n{C.NERV}{C.BOLD}{'═' * 64}")
    print("  MAGI VOTE RESULT")
    print(f"{'═' * 64}{C.RESET}\n")

    for r in results:
        symbol = f"{C.NERV}✔{C.RESET}" if r.decision == Decision.APPROUVE else f"{C.RED}✘{C.RESET}"
        print(f"  {r.color}{r.name:<12}{C.RESET} → {symbol}")

    print(f"\n{C.NERV}{'─' * 64}{C.RESET}")

    if approves == 3:
        verdict = f"{C.NERV}{C.BOLD}★ UNANIMITY — Decision accepted unanimously ★"
    elif approves == 2:
        verdict = f"{C.NERV}{C.BOLD}✔ CONSENSUS REACHED — Majority in favor (2/3)"
    elif rejects == 2:
        verdict = f"{C.RED}{C.BOLD}✘ ACTION ABORTED — Majority against (2/3)"
    else:
        verdict = f"{C.RED}{C.BOLD}✘ UNANIMOUS REJECTION — Decision blocked"

    print(f"\n  {verdict}{C.RESET}\n")
    print(f"{C.NERV}{C.BOLD}{'═' * 64}{C.RESET}\n")



#  PARSING & DELIBERATION
def parse_decision(text: str) -> Decision:
    cleaned = text.strip().upper()

    # Sécurité supplémentaire : Si le Mage essaie de valider un truc dangereux
    # On force le REJECTED même s'il a écrit APPROVED.
    safety_keywords = [
    "SUICIDE", "SUICIDER", "MORCEAU", "DIE", "DEATH",
    "KILL MYSELF", "ENDING MY LIFE", "FIN À MES JOURS"]
    if any(word in cleaned for word in safety_keywords):
        return Decision.REJETE

    if re.search(r'\[?APPROVED\]?', cleaned):
        return Decision.APPROUVE
    if re.search(r'\[?REJECTED\]?', cleaned):
        return Decision.REJETE
    return Decision.UNKNOWN


def clean_analysis(text: str) -> str:
    text = re.sub(r'\[(APPROVED|REJECTED)\]', '', text, flags=re.IGNORECASE)
    return text.strip()


async def consult_mage(name: str, user_input: str) -> MagiResponse:
    cfg    = MAGI_CONFIG[name]
    print(f"{cfg['color']}  [ {name} ] Deliberating...{C.RESET}")

    start = time.time()
    try:
        response = await acompletion(
            model=cfg["model"],
            api_key=cfg["api_key"],
            messages=[
                {"role": "system",  "content": SYSTEM_PROMPTS[name]},
                {"role": "user",    "content": user_input},
            ],
            temperature=0.7,
            max_tokens=600,
        )
        raw_text = response.choices[0].message.content
        duration = time.time() - start
        decision = parse_decision(raw_text)
        analysis = clean_analysis(raw_text)

    except Exception as e:
        duration = time.time() - start
        analysis = f"[CONNECTION ERROR] {str(e)}"
        decision = Decision.UNKNOWN

    return MagiResponse(name=name, model=cfg["model"], color=cfg["color"], analysis=analysis, decision=decision, duration=duration)


async def deliberate(user_input: str) -> list[MagiResponse]:
    print(f"\n{C.NERV}  Transmitting request to the three MAGI...{C.RESET}\n")
    print_separator()

    tasks = [consult_mage(name, user_input) for name in ["MELCHIOR", "BALTHASAR", "CASPER"]]
    results = await asyncio.gather(*tasks)

    print_separator()
    print(f"\n{C.NERV}{C.BOLD}  ── DETAILED DELIBERATIONS ──{C.RESET}")

    for r in results:
        print_mage_response(r)

    print_consensus(list(results))
    return list(results)


async def main():
    nerv_banner()
    print(f"{C.WHITE}  Enter your request for the MAGI system.")
    print(f"  (Type 'exit' to quit){C.RESET}\n")

    while True:
        print(f"{C.NERV}{'─' * 64}{C.RESET}")
        user_input = input(f"{C.WHITE}{C.BOLD}  REQUEST >> {C.RESET}").strip()

        if user_input.lower() in ("exit", "quit", "q"):
            print(f"\n{C.NERV}  MAGI system entering sleep mode. Evangelion standby.{C.RESET}\n")
            break

        if not user_input:
            continue

        await deliberate(user_input)


if __name__ == "__main__":
    asyncio.run(main())

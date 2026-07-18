#!/usr/bin/env python3
"""Build README.md with the ANSI-colored neofetch block.

Runs in CI so the raw ANSI escape bytes are generated on the runner.
"""
import os

E = "\x1b["
R = E + "0m"          # reset
CY = E + "36m"         # cyan
BCY = E + "96m"        # bright cyan
GR = E + "32m"         # green
BGR = E + "92m"        # bright green
WH = E + "97m"         # bright white
DIM = E + "90m"        # grey
B = E + "1m"           # bold

ART = [
    "        ▄▄██████▄▄        ",
    "      ███▀▀    ▀▀███      ",
    "     ███          ███     ",
    "     ███          ███     ",
    "     ███          ███     ",
    "  ▄████████████████████▄  ",
    "  ██████████████████████  ",
    "  ████████▀▀▀▀▀▀████████  ",
    "  ███████  ▄██▄  ███████  ",
    "  ████████ ▀██▀ ████████  ",
    "  █████████ ██ █████████  ",
    "  ██████████████████████  ",
    "  ▀████████████████████▀  ",
    "                          ",
    "     [ DP//SEC v2.0 ]     ",
]
ART_W = max(len(a) for a in ART)

def k(label):  # neofetch key
    return f"{B}{GR}{label}{R}"

INFO = [
    f"{B}{BCY}dimitris{R}{WH}@{R}{B}{BCY}DimPourn{R}",
    f"{DIM}──────────────────{R}",
    f"{k('Now')}        Information Science @ AUEB — cybersecurity path",
    f"{k('Focus')}      Network security · GRC · pentest labs",
    f"{k('Base')}       Athens, GR",
    "",
    f"{B}{WH}Stack{R}",
    f"{k('Security')}   Nmap · Metasploit · Hydra · Wireshark · fail2ban",
    f"{k('Infra')}      Docker · Tailscale / WireGuard · Pi-hole · Unbound",
    f"{k('Code')}       Python · Java · Bash",
    f"{k('Env')}        Kali Linux · VirtualBox · Raspberry Pi 5",
    "",
    f"{B}{WH}Highlights{R}",
    f"{BGR}•{R} Built & hardened a self-hosted homelab, then attacked it",
    f"{BGR}•{R} Exploitation range: vsftpd 2.3.4 backdoor → root {DIM}(sandboxed){R}",
    f"{BGR}•{R} CV runs like a secure phone OS",
    "",
    f"{k('Langs')}      GR ●●●●● · EN ●●●●● · JP ●●●○○",
]

lines = [f"{B}{BCY}dimitris@sec{R}{WH}:{R}{BCY}~{R}{WH}${R} neofetch", ""]
rows = max(len(ART), len(INFO))
art_pad_top = 1  # start art one line down for balance
for i in range(rows + art_pad_top):
    ai = i - art_pad_top
    art = ART[ai] if 0 <= ai < len(ART) else " " * ART_W
    info = INFO[i] if i < len(INFO) else ""
    lines.append(f"{CY}{art.ljust(ART_W)}{R}   {info}".rstrip())

while lines and not lines[-1].replace("\x1b[36m", "").replace("\x1b[0m", "").strip():
    lines.pop()
NEOFETCH = "\n".join(lines)

README = f"""<div align="center">

# `dimitris@sec:~$ ./init --profile`

[![CV](https://img.shields.io/badge/CV-phone--OS_experience-22d3ee?style=for-the-badge&labelColor=070a18)](https://dimpourn.github.io/DimPournCV/)
[![Homelab](https://img.shields.io/badge/Homelab-sh__lab_write--up-34d399?style=for-the-badge&labelColor=070a18)](https://dimpourn.github.io/sh_lab/)
[![Email](https://img.shields.io/badge/Email-dvpournatzis@proton.me-7c3aed?style=for-the-badge&labelColor=070a18)](mailto:dvpournatzis@proton.me)

</div>

```ansi
{NEOFETCH}
```

### `dimitris@sec:~$ ./contributions.sh`

<div align="center">

[![Contribution graph](assets/contributions.svg)](https://github.com/DimPourn)

</div>

### `dimitris@sec:~$ ./stats.sh --all`

<div align="center">

<img height="165" src="https://github-readme-stats.vercel.app/api?username=DimPourn&show_icons=true&hide_border=true&bg_color=070a18&title_color=22d3ee&icon_color=34d399&text_color=b9c2dd&ring_color=22d3ee" alt="GitHub stats" />
<img height="165" src="https://github-readme-stats.vercel.app/api/top-langs/?username=DimPourn&layout=compact&hide_border=true&bg_color=070a18&title_color=22d3ee&text_color=b9c2dd" alt="Top languages" />

</div>

### `dimitris@sec:~$ cat mission.txt`

> Building secure infrastructure and then attacking it — the two halves of understanding
> how things actually break. Open to **security internships & junior roles** · Athens / remote.

<div align="center">

`nmap -sV dimitris` → `443/tcp open  always-learning`

</div>
"""

out = os.path.join(os.path.dirname(__file__), "..", "README.md")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    f.write(README)

# sanity: uniform art width, no tabs, line lengths (visible chars)
import re
strip = lambda s: re.sub(r"\x1b\[[0-9;]*m", "", s)
widths = sorted({len(strip(l)) for l in lines})
print("max visible line width in ansi block:", widths[-1])
print("README bytes:", os.path.getsize(out))

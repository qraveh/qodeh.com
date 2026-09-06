---
title: "Superconductor Electronics Monitor 2026"
subtitle: "An annual, tiered assessment of superconductor electronics"
date: 2026-09-06
summary: "Superconductor electronics holds the outright digital speed record and switches roughly 1,000× below CMOS. The 2026 Monitor consolidates the field's scattered technical, ecosystem and funding facts into one tiered picture — a family taxonomy, subsystem readiness, a fab × technology matrix with fourteen fab profiles, and market scenarios to 2035."
author: "Raveh Neeman"
showToc: false
# The slug moved with the v1.1 rename. Hugo emits a redirect stub at the old
# path, which was live from 9 Aug 2026 and is indexed by Google and Bing.
aliases: ["/publications/sfq-technology-monitor-2026/"]
---

_v1.1 · published 6 September 2026 · supersedes v1.0 (9 August 2026) · CC BY 4.0_

**[Download the Monitor (PDF)](/sfq-monitor/files/Superconductor-Electronics-Monitor-2026_v1.1.pdf)** · **[PPTX](/sfq-monitor/files/Superconductor-Electronics-Monitor-2026_v1.1.pptx)** · **[Monitor home](/sfq-monitor/)** · doi:[10.5281/zenodo.21860767](https://doi.org/10.5281/zenodo.21860767)

Superconductor electronics (SCE) — digital logic, memory and mixed-signal circuits built from Josephson junctions, whose largest branch is single-flux-quantum (SFQ) logic — is a genuine outlier. It holds the outright digital speed record, a 770 GHz toggle flip-flop that no technology has beaten, and it switches at roughly 2×10⁻¹⁹ J, about 1,000× below CMOS before the cryogenic cooling tax and a conditional 10–30× after it.

Its limitations are equally plain, though. It is not dense — about 2×10⁴× behind CMOS as demonstrated, with a physics ceiling still three to four orders of magnitude below it. It is memory-poor: the 4 K RAM record is 64 kb, set in 2013, and the largest all-junction memory ever built holds 202,280 bits. And its tooling is uneven — a commercial physical-verification layer exists, from a single supplier, but above RTL nothing is licensable. Memory, not tooling, is the lowest gating subsystem.

## Why this warrants its own monitor

SCE sits on three critical paths at once.

**It is an enabler and a multiplier for superconducting quantum computing.** Room-temperature control tops out at roughly a thousand lines into a cryostat; at 10⁵–10⁶ qubits, control electronics has to move inside it. SFQ is the only logic family that has demonstrated qubit-control waveform synthesis at millikelvin — up to 99.9% single-qubit fidelity in 2026, now from three independent parties — and demonstrated digital demultiplexing that breaks one-line-per-qubit scaling. Control and readout are also where a quantum processor meets the classical machine around it, so the same cold-side position places SCE directly on the interface between quantum computing and HPC.

**It is one of the plausible futures of HPC itself.** Wall-plug energy per unit of work is now the binding constraint on large-scale computing, and the projected system figures sit well below current datacenter accelerators even after the cooling tax is paid. Those are vendor projections, not silicon.

**It is very nearly the only route to computing at hundreds of gigahertz.** The outright digital speed record in any technology is an SFQ flip-flop, and Josephson-junction physics supports switching approaching a terahertz. Complex circuits run at tens of gigahertz today; no other digital family is credibly in that conversation.

## What v1.1 changed

The publication is renamed to the field's own umbrella term: SFQ is the largest branch of superconductor electronics, not the whole of it. The edition adds a twenty-two-family taxonomy, a density page — the gap, the four levers and the fabs that hold them — a fab × technology matrix, and fourteen fab profiles that the matrix rows link through to.

It also **corrects eight claims of v1.0**, itemised on the edition's page 32. Every scenario band, scenario weight and absolute market figure is unchanged and was re-verified anchor by anchor.

**Cite as**

> Neeman, R., "Superconductor Electronics Monitor 2026," v1.1, Qodeh, 2026 · qodeh.com/sfq-monitor · doi:[10.5281/zenodo.21860767](https://doi.org/10.5281/zenodo.21860767)

The all-versions DOI always resolves to the current edition; to pin this edition cite [10.5281/zenodo.22537315](https://doi.org/10.5281/zenodo.22537315). v1.0 remains citable at [10.5281/zenodo.21860768](https://doi.org/10.5281/zenodo.21860768).

Factual corrections are welcome: **[raveh.neeman@qodeh.com](mailto:raveh.neeman@qodeh.com?subject=SFQ%20Monitor%20correction)**

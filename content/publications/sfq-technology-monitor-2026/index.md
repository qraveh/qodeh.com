---
title: "SFQ Technology Monitor 2026"
subtitle: "An annual, tiered assessment of superconducting single-flux-quantum digital electronics"
date: 2026-08-09
summary: "Superconducting SFQ logic holds the outright digital speed record and switches roughly 1,000× below CMOS. The 2026 Monitor consolidates the field's scattered technical, ecosystem and funding facts into one tiered picture — subsystem readiness, a fabrication and funding census, and market scenarios to 2035."
author: "Raveh Neeman"
showToc: false
---

_v1.0 · published 9 August 2026 · CC BY 4.0_

**[Download the Monitor (PDF)](/sfq-monitor/files/SFQ-Technology-Monitor-2026_v1.0.pdf)** · **[SFQ Monitor home](/sfq-monitor/)** · doi:[10.5281/zenodo.21860768](https://doi.org/10.5281/zenodo.21860768)

Single-flux-quantum logic — RSFQ, ERSFQ/eSFQ, RQL, AQFP and DSFQ, treated as one field — is a genuine outlier. It holds the outright digital speed record, a 770 GHz toggle flip-flop that no technology has beaten, and it switches at roughly 2×10⁻¹⁹ J, about 1,000× below CMOS before the cryogenic cooling tax and a conditional 10–30× after it.

Its limitations are equally plain, though: it is not dense — some 10³–10⁵× behind CMOS; it is memory-poor, with a 4 K RAM record of 64 kb unbeaten since 2013; and it is tool-poor, with no commercial EDA flow.

## Why this warrants its own monitor

SFQ sits on four critical paths at once.

**It is an enabler and a multiplier for superconducting quantum computing.** Room-temperature control tops out at roughly a thousand lines into a cryostat; at 10⁵–10⁶ qubits, control electronics has to move inside it. SFQ is the only logic family that has demonstrated qubit-control waveform synthesis at millikelvin — up to 99.9% single-qubit fidelity in 2026 — and demonstrated digital demultiplexing that breaks one-line-per-qubit scaling. The Monitor's verdict is deliberately bounded: physics-favored, not physics-mandated.

**It is the bridge from quantum computing to HPC.** Control and readout are where a quantum processor meets the classical machine around it. SFQ operates on the cold side of that boundary, which makes it a candidate substrate for the QC→HPC interface rather than an accessory bolted onto it.

**It is one of the plausible futures of HPC itself.** Wall-plug energy per unit of work is now the binding constraint on large-scale computing, and SFQ's projected system figures sit well below current datacenter accelerators even after the cooling tax is paid. Those are vendor projections rather than silicon — which is precisely why this Monitor tiers them instead of asserting them.

**It is very nearly the only route to computing at hundreds of gigahertz.** The outright digital speed record in any technology is an SFQ flip-flop, and Josephson-junction physics supports switching approaching a terahertz. Complex SFQ circuits run at tens of gigahertz today; no other digital family is credibly in that conversation.

## Cite as

> Neeman, R., "SFQ Technology Monitor 2026," v1.0, Qodeh, 2026. doi:[10.5281/zenodo.21860768](https://doi.org/10.5281/zenodo.21860768) (all versions: [10.5281/zenodo.21860767](https://doi.org/10.5281/zenodo.21860767)).

Factual corrections are welcome: **[raveh.neeman@qodeh.com](mailto:raveh.neeman@qodeh.com?subject=SFQ%20Monitor%20correction)**

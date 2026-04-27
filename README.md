# AEGIS HOUSING SYSTEM PROTOCOL SPECIFICATION

**Hybrid On-chain Operational Proof (HOOP) Network**  
*Climate-Resilient Modular Row-House Community on Solana*

**Date:** April 27, 2026  
**Author:** Martin Poveda Amarfil | Climate Risk Analytics, LLC  
**Project Wallet:** `CzdBHjP7CkqRaYrxwoCxDpFhXU2B6akZ5rfFKQqo1NCj` (Solana Mainnet)  
**Contact:** +1 (202) 438-1338 | martin.poveda@climateriskanalytics.lat | [climateriskanalytics.lat](https://climateriskanalytics.lat) | Washington, DC

---

## Repository Structure (Local Mirror)

This directory contains the open-source components of the Aegis Protocol as specified in the full protocol document.

- **Aegis-Public-Basement/**: Basement engineering, geothermal models, CAD validation scripts (MIT/Apache 2.0)
- **Aegis-Core-Validation/**: Community PoW validation scripts and workflow (free for community use)
- **HOOP-Utility-Protocol/**: Placeholder for Anchor program source (to be added upon Mainnet deploy)

**Full Protocol Specification:** See the authoritative PDF or original document for complete details on architecture, smart contracts, capital tranches, gamified PoW, LaaS model, and legal structure (Wyoming DAO LLC + titlingDAO).

**Deployment Protocol:** Aegis_Deployment_Protocol.pdf — Public vs Private assets, Solana Devnet/Mainnet strategy, phased roadmap, and rationale for maximum advancement/flexibility/scalability.

**Google Cloud Admin Push (text/code only):** google_cloud_admin_push.py — Full admin setup: create public (world-readable CDN) + private (IAM restricted) buckets, IAM policies (allUsers vs validator+multisig), upload open-source patent + v2.0 PoW/gamification assets, private upper-IP (SHA256 metadata only), contest leaderboard. Run: python google_cloud_admin_push.py --admin-push

**License:** Basement engineering models and validation code — MIT / Apache 2.0 (free for community use). Upper architectural IP — proprietary but auditable via hash.

**On-Chain Reference:** Solana Memo Program + Anchor program on Devnet (deployed). First grant tranche confirmed.

---

## Quick Start for Validators (MAX GAMIFICATION v2.0 — April 2026)

**New in v2.0:** Ultra-rigorous PoW with Structural Math, Electric Labor, Permitting/Contracting, 
Earnings (staking yield + labor bounties), Badges, Weekly Contests, Leaderboards.

```bash
cd Aegis-Core-Validation
python validate_all.py --milestone 2 --local_data ./my_milestone2_evidence/ --stake_amount 250 --wallet YOUR_SOLANA_WALLET
```

**Rewards:**
- First 10 per gate: 150+ HOOP + 1.0-2.0x multiplier from specialist badges
- Earnings: ~$120-300 USD equiv per successful validation (protocol treasury share + staking yield)
- Badges: STRUCTURAL_SPECIALIST (+25% earnings), ELECTRICIAN_SPECIALIST, MASTER_BUILDER (+50%)
- Contest: Weekly $5k HOOP prize pool + NFT drops for top 10 leaderboard

**Full PoW Modules (all mandatory for max score):**
- `structural_math_validator.py` — IRC/ASCE loads, deflection, seismic, rebar (50+ pts)
- `electrical_labor_validator.py` — NEC 2023, mini-grid 180kW/600kWh, grounding, EV (40+ pts)
- `construction_permitting_validator.py` — 10-phase sequence, Virginia permits (USBC, 12VAC5-630), AIA contracts, liens (60+ pts)
- Thermal/Fourier + ACH50 legacy + new

**US Permitting & Contracting (max educational content for engagement):**
See full roadmap in construction_permitting_validator.py docstring:
1. Zoning (R-12/R-16/C-H/T-5C by-right)
2. Building + Trade Permits (county + VDH geothermal)
3. Inspections (footing → CO)
4. Contracting (AIA, progress payments, VA lien waivers §43)
5. Post-CO: Warranty, HOA, utility transfer

**Stake & Earn:** Lock 50-500 USDC (365d post-CO) for slashing protection + 1.5x reward multiplier. 
Dispute resolution via 4-of-7 multi-sig + P.E. E&O insurance.

For full details, refer to Aegis_Deployment_Protocol.pdf (Section 3 PoW) and Protocol Specification (Sections 4, 8, 10).

---

*This is the local sandbox mirror of the protocol assets. For production GitHub repos and Solana Mainnet deployment, see official channels.*

#!/usr/bin/env python3
"""
AEGIS HOOP - validate_all.py v2.2
Full multi-module Proof-of-Work validator with REAL evidence parsing.

Key Improvement (v2.2):
- Now reads actual measurements from local_data/measurements.json
- Feeds real values into StructuralParams() and ElectricalParams()
- Still includes deterministic chunked hashing and safe gamification preview
"""

import argparse
import hashlib
import json
import os
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List

# Import validators
from structural_math_validator import validate_structural_integrity, StructuralParams
from electrical_labor_validator import validate_electrical_labor, ElectricalParams
from construction_permitting_validator import validate_construction_sequence

def parse_evidence_data(local_data_path: str) -> Dict:
    """
    Extracts real parameter values from the builder's evidence folder.
    Expected file: local_data/measurements.json
    """
    params = {
        "structural": {},
        "electrical": {}
    }
    
    target_file = os.path.join(local_data_path, "measurements.json")
    
    if os.path.exists(target_file):
        with open(target_file, "r") as f:
            data = json.load(f)
        
        # Structural measurements
        if "structural" in data:
            params["structural"] = {
                "measured_deflection_in": data["structural"].get("measured_deflection_in", 0.12),
                "measured_rebar_spacing_in": data["structural"].get("measured_rebar_spacing_in", 6.0),
                "soil_bearing_psf": data["structural"].get("soil_bearing_psf", 2000.0)
            }
        
        # Electrical measurements
        if "electrical" in data:
            params["electrical"] = {
                "measured_service_amps": data["electrical"].get("measured_service_amps", 185),
                "measured_grounding_ohms": data["electrical"].get("measured_grounding_ohms", 4.8),
                "ev_load_kva": data["electrical"].get("ev_load_kva", 7.2)
            }
        
        print("✅ Real evidence data loaded from measurements.json")
    else:
        print("⚠️ WARNING: No measurements.json found. Using default values (PoW score will be lower).")
    
    return params

def compute_local_hash(local_data: str) -> str:
    """Deterministic + memory-safe SHA256 hashing."""
    hasher = hashlib.sha256()
    
    if os.path.isdir(local_data):
        for root, dirs, files in os.walk(local_data):
            dirs.sort()
            for file in sorted(files):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, local_data)
                hasher.update(rel_path.encode('utf-8'))
                
                with open(filepath, 'rb') as f:
                    while chunk := f.read(8192):
                        hasher.update(chunk)
    else:
        with open(local_data, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
                
    return hasher.hexdigest()

def calculate_gamification_score(struct_res: Dict, elec_res: Dict, construct_res: Dict, stake_amount: float) -> Dict:
    """Calculate points/badges. Earnings logic stays on-chain."""
    base = 50
    struct_pts = struct_res.get("score", 0) * 0.5
    elec_pts = elec_res.get("score", 0) * 0.4
    construct_pts = construct_res.get("score", 0) * 0.6
    total = base + struct_pts + elec_pts + construct_pts
    
    badges = []
    if struct_res.get("score", 0) > 85: badges.append("STRUCTURAL_SPECIALIST")
    if elec_res.get("score", 0) > 80: badges.append("ELECTRICIAN_SPECIALIST")
    if construct_res.get("score", 0) > 90: badges.append("PERMIT_MASTER")
    if len(badges) >= 3: badges.append("MASTER_BUILDER")
    
    multiplier = 2.0 if "MASTER_BUILDER" in badges else (1.5 if len(badges) >= 2 else 1.0)
    final_points = int(total * multiplier)
    
    earnings_usd_preview = round(final_points * 0.8 + (stake_amount * 0.02), 2)
    
    return {
        "points": final_points,
        "badges": badges,
        "multiplier": multiplier,
        "earnings_usd_preview": earnings_usd_preview,
        "hoop_reward": final_points * 2
    }

def validate_milestone_full(
    milestone: int,
    local_data: str,
    on_chain_hash: str,
    stake_amount: float,
    validator_wallet: str
) -> Dict:
    
    local_hash = compute_local_hash(local_data)
    hash_match = local_hash == on_chain_hash
    
    # === REAL DATA EXTRACTION ===
    evidence = parse_evidence_data(local_data)
    
    # Feed real values into sub-validators
    struct_params = StructuralParams(
        measured_deflection_in=evidence["structural"].get("measured_deflection_in", 0.12),
        measured_rebar_spacing_in=evidence["structural"].get("measured_rebar_spacing_in", 6.0),
        soil_bearing_psf=evidence["structural"].get("soil_bearing_psf", 2000.0)
    )
    struct_res = validate_structural_integrity(struct_params)
    
    elec_params = ElectricalParams(
        measured_service_amps=evidence["electrical"].get("measured_service_amps", 185),
        measured_grounding_ohms=evidence["electrical"].get("measured_grounding_ohms", 4.8),
        ev_load_kva=evidence["electrical"].get("ev_load_kva", 7.2)
    )
    elec_res = validate_electrical_labor(elec_params)
    
    construct_res = validate_construction_sequence(milestone)
    
    game = calculate_gamification_score(struct_res, elec_res, construct_res, stake_amount)
    
    status = "FULL PoW SUCCESS" if hash_match and game["points"] > 120 else "PARTIAL / NEEDS REVIEW"
    if not hash_match:
        status = "HASH MISMATCH - VALIDATION FAILED"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "milestone": milestone,
        "validator_wallet": validator_wallet,
        "local_hash": local_hash,
        "on_chain_hash": on_chain_hash,
        "hash_match": hash_match,
        "structural": struct_res,
        "electrical": elec_res,
        "construction": construct_res,
        "gamification": game,
        "stake_amount_usdc_claimed": stake_amount,
        "status": status,
        "evidence_source": "measurements.json" if os.path.exists(os.path.join(local_data, "measurements.json")) else "defaults"
    }
    
    filename = f"pow_report_m{milestone}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Validation complete. Report saved: {filename}")
    print(f"   Status: {report['status']}")
    print(f"   Points: {game['points']} | Badges: {', '.join(game['badges'])}")
    
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AEGIS HOOP Full PoW Validator v2.2 (Real Evidence Parsing)")
    parser.add_argument("--milestone", type=int, required=True)
    parser.add_argument("--local_data", type=str, required=True)
    parser.add_argument("--on_chain_hash", type=str, default="")
    parser.add_argument("--stake_amount", type=float, default=100.0)
    parser.add_argument("--wallet", type=str, default="CzdBHjP7CkqRaYrxwoCxDpFhXU2B6akZ5rfFKQqo1NCj")
    
    args = parser.parse_args()
    
    if not args.on_chain_hash:
        print("⚠️ WARNING: No on-chain hash provided. Auto-generating for local testing only.")
        args.on_chain_hash = compute_local_hash(args.local_data)
    
    validate_milestone_full(args.milestone, args.local_data, args.on_chain_hash, args.stake_amount, args.wallet)

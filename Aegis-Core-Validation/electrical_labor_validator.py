#!/usr/bin/env python3
"""
AEGIS HOOP - electrical_labor_validator.py (v3.0 - Enterprise Grade)
Strict NEC 2023 Proof-of-Work validator.
Correctly isolates continuous/non-continuous loads and enforces IEEE grounding standards.
"""

from dataclasses import dataclass
from typing import Dict
import math

@dataclass
class ElectricalParams:
    """Rigorous electrical parameters for residential + mini-grid PoW."""
    # General Loads (Subject to Demand Factors)
    floor_area_sqft: float = 2700.0
    general_lighting_va_per_sqft: float = 3.0
    small_appliance_circuits: int = 2
    laundry_circuit_va: float = 1500.0
    
    # Fixed & Continuous Loads (100% or 125%)
    hvac_va: float = 12000.0
    ev_level2_kva: float = 7.2  # Continuous
    other_fixed_va: float = 5000.0
    
    # Field Measurements
    measured_service_amps: float = 200.0 # e.g., standard 200A panel
    measured_grounding_ohms: float = 4.8 # AEGIS standard <= 5 ohms
    
    # Mini-Grid Spec Commitments
    community_pv_kw: float = 180.0
    community_battery_kwh: float = 600.0

def calculate_nec_demand(params: ElectricalParams) -> float:
    """Strict NEC 2023 Article 220 Load Calculation."""
    
    # 1. General Loads (Lighting, Small Appliance, Laundry)
    lighting_va = params.general_lighting_va_per_sqft * params.floor_area_sqft
    small_appliance_va = 1500 * params.small_appliance_circuits
    general_total_va = lighting_va + small_appliance_va + params.laundry_circuit_va
    
    # Apply NEC 220.42 Demand Factor ONLY to general loads
    if general_total_va <= 10000:
        general_demand_va = general_total_va
    else:
        general_demand_va = 10000 + ((general_total_va - 10000) * 0.35)
        
    # 2. Continuous & Fixed Loads
    ev_demand_va = (params.ev_level2_kva * 1000) * 1.25 # NEC 625.41 requires 125% for EV
    hvac_demand_va = params.hvac_va # 100% for largest motor load
    
    # 3. Total Calculated Demand
    total_demand_va = general_demand_va + ev_demand_va + hvac_demand_va + params.other_fixed_va
    
    return round(total_demand_va, 1)

def validate_electrical_labor(params: ElectricalParams) -> Dict:
    """Full electrical validation evaluating Code vs. Field Reality."""
    results = {}
    
    # 1. Load Calculation
    demand_va = calculate_nec_demand(params)
    service_amps_required = demand_va / 240.0 
    
    # Find next standard breaker size (e.g., 100, 125, 150, 200)
    standard_breakers = [100, 125, 150, 200, 225, 400]
    required_panel_size = next((size for size in standard_breakers if size >= service_amps_required), 400)
    
    results["calculated_demand_va"] = demand_va
    results["minimum_amps_required"] = round(service_amps_required, 1)
    results["required_panel_size_amps"] = required_panel_size
    
    # 2. Service Amp Verification
    # Ensure the measured (installed) panel is at least the required size
    amp_pass = params.measured_service_amps >= required_panel_size
    amp_score = 100 if amp_pass else 0 # It's a pass/fail safety issue
    
    results["measured_service_amps"] = params.measured_service_amps
    results["amp_pass"] = amp_pass
    results["amp_score"] = amp_score
    
    # 3. Grounding Resistance (AEGIS Gold Standard ≤ 5Ω)
    ground_pass = params.measured_grounding_ohms <= 5.0
    ground_score = 100 if ground_pass else max(0, 100 - (params.measured_grounding_ohms - 5) * 25)
    
    results["measured_grounding_ohms"] = params.measured_grounding_ohms
    results["ground_pass"] = ground_pass
    results["ground_score"] = round(ground_score, 1)
    
    # 4. Mini-Grid Minimums Check
    grid_pass = params.community_pv_kw >= 150 and params.community_battery_kwh >= 500
    grid_score = 100 if grid_pass else 0
    results["grid_specs_pass"] = grid_pass
    results["grid_score"] = grid_score
    
    # 5. Overall Score
    overall_score = round((
        results["amp_score"] * 0.40 +
        results["ground_score"] * 0.40 +
        results["grid_score"] * 0.20
    ), 1)
    
    results["score"] = overall_score
    results["pass"] = overall_score >= 80 and amp_pass # Must pass critical safety checks
    results["status"] = "PASS" if results["pass"] else "FAIL - Safety Review Required"
    
    return results

if __name__ == "__main__":
    params = ElectricalParams()
    result = validate_electrical_labor(params)
    print("=== Strict NEC Electrical PoW Result ===")
    for k, v in result.items():
        print(f"{k}: {v}")

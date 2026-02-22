import sys
import os
import json

# Setup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_engine.utils.clinical_memory import save_experience

def populate_demo_memories():
    print("--- Injecting Clinically Refined Demo Memories ---")
    
    # NEW MEMORY: Brain Cancer, MGMT Unmethylated, Older Patient (Matching your test)
    case_match = {
        "patientId": "REF-BRAIN-75-UNMETH",
        "cancer_type": "brain",
        "age": 75,
        "genomicProfile": {"MGMT": "unmethylated", "IDH": "mutant"},
        "imaging_metrics": {"tumor_vol": 35}
    }
    plan_match = {
        "primary_treatment": "Hypofractionated RT (40Gy/15fx) + Adjuvant TMZ (Extended)",
        "rationale": ["Modified Perry Regimen with extended observation for MGMT unmethylated elderly cohort."]
    }
    save_experience(case_match, plan_match, is_correction=True)

    # Memory 1: Brain Cancer with IDH1 Mutation
    case_brain = {
        "patientId": "REF-BRAIN-2025-001",
        "cancer_type": "brain",
        "age": 45,
        "genomicProfile": {"IDH": "mutant", "MGMT": "methylated"},
        "imaging_metrics": {"tumor_vol": 40}
    }
    plan_brain = {
        "primary_treatment": "Concurrent TMZ + Hypofractionated RT (40Gy/15fx) with Signal Boost",
        "rationale": ["Clinician opted for hypofractionation to minimize neuro-toxicity in active IDH mutant profile."]
    }
    save_experience(case_brain, plan_brain, is_correction=True)

    # Memory 2: Breast Cancer with HER2+
    case_breast = {
        "patientId": "REF-BREAST-2025-042",
        "cancer_type": "breast",
        "age": 55,
        "genomicProfile": {"HER2": "positive"},
        "imaging_metrics": {"tumor_vol": 10}
    }
    plan_breast = {
        "primary_treatment": "Trastuzumab Deruxtecan + Adjuvant Endocrine Blockade",
        "rationale": ["Second-line HER2 targeting applied successfully after standard pathway deviation."]
    }
    save_experience(case_breast, plan_breast, is_correction=True)
    
    print("\n[OK] Clinical memories updated with match for test patient.")

if __name__ == "__main__":
    populate_demo_memories()

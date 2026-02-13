import os
import sys
import json

# Add ai_engine to path - going up one level from Tests folder to root
sys.path.append(os.path.join(os.getcwd(), 'ai_engine'))

from utils.outcome_engine import engine as outcome_engine

def test_outcomes():
    print("=== STARTING MULTIMODAL OUTCOME ENGINE TEST ===")
    print("")

    # 1. Test Brain Cancer (Should use CoxPH Model + Genomic Offsets)
    print("[TEST 1] Brain Cancer Survival (Statistical Model)")
    brain_patient = {
        "cancer_type": "Brain",
        "age": 62,
        "resection": "GTR",
        "kps": 90,
        "genomicProfile": {"IDH1": "Mutated", "MGMT": "Methylated"}
    }
    res_brain = outcome_engine.predict_survival(brain_patient)
    print(f"Result: Median {res_brain['median']} months (Confidence: {res_brain['confidence']}%)")
    print("")

    # 2. Test Breast Cancer (Should use Parametric Engine + Hazard Ratios)
    print("[TEST 2] Breast Cancer Survival (Parametric/Literature Model)")
    breast_patient = {
        "cancer_type": "Breast",
        "age": 45,
        "stage": "II",
        "genomicProfile": {"HER2": "Positive", "BRCA": "Wild Type"}
    }
    res_breast = outcome_engine.predict_survival(breast_patient)
    print(f"Result: Median {res_breast['median']} months (Confidence: {res_breast['confidence']}%)")
    print("")

    # 3. Test Pharmacological Toxicity Mapping
    print("[TEST 3] Toxicity Mapping (Temozolomide + Bevacizumab)")
    drugs = ["Temozolomide", "Bevacizumab"]
    patient_frail = {"age": 75, "kps": 60, "comorbidities": "cardiac history"}
    toxicity = outcome_engine.predict_toxicity(drugs, patient_frail)
    
    print("Projected Risks for Elderly/Frail Patient:")
    for effect, risk in toxicity.items():
        print(f"  - {effect.replace('_', ' ').capitalize()}: {risk}%")

    print("")
    print("=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_outcomes()

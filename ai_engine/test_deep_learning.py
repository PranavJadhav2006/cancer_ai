import sys
import os
import json

# Setup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_engine.utils.clinical_memory import save_experience, retrieve_similar_experience

def test_learning_flow():
    print("--- 1. Simulating an Expert Human Correction ---")
    patient_a = {
        "patientId": "TEST_PATIENT_001",
        "cancer_type": "Brain",
        "age": 45,
        "genomicProfile": {"IDH1": "Mutated"},
        "imaging_metrics": {"tumor_vol": 50, "edema_vol": 10}
    }
    
    final_plan = {
        "primary_treatment": "Experimental Protocol X (Human Override)",
        "rationale": ["Manual override by clinician."]
    }
    
    save_experience(patient_a, final_plan, feedback_score=2.0, is_correction=True)
    print("[OK] Expert correction saved.")

    print("\n--- 2. Testing Retrieval for Similar Patient B ---")
    patient_b = {
        "cancer_type": "Brain",
        "age": 48,
        "genomicProfile": {"IDH1": "Mutated"},
        "imaging_metrics": {"tumor_vol": 45, "edema_vol": 12}
    }
    
    past_cases = retrieve_similar_experience(patient_b, top_k=1)
    
    if past_cases:
        case = past_cases[0]
        print(f"MATCH: {case['treatment_plan']['primary_treatment']}")
        print(f"Similarity Score: {case['similarity_score']:.4f}")
        if "Experimental Protocol X" in case['treatment_plan']['primary_treatment']:
            print("\n[SUCCESS] AI learned and retrieved the human correction!")
    else:
        print("[FAIL] No cases found.")

if __name__ == "__main__":
    test_learning_flow()

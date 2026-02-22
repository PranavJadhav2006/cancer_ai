import sys
import os
import json
import numpy as np

# Setup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_engine.utils.clinical_memory import save_experience, retrieve_similar_experience

def run_automated_learning_test():
    print("--- 1. Populating AI Memory ---")
    
    # Case 1: Lung
    case_lung = {
        "patientId": "LUNG_001",
        "cancer_type": "Lung",
        "age": 62,
        "genomicProfile": {"EGFR": "L858R"}
    }
    plan_lung = {"primary_treatment": "Targeted: Osimertinib"}
    save_experience(case_lung, plan_lung, is_correction=False)

    # Case 2: Breast (Correction)
    case_breast = {
        "patientId": "BREAST_002",
        "cancer_type": "Breast",
        "age": 55,
        "genomicProfile": {"HER2": "Positive"}
    }
    plan_breast = {"primary_treatment": "Clinical Trial: B-XYZ"}
    save_experience(case_breast, plan_breast, is_correction=True)

    print("\n--- 2. Verifying Memory ---")
    meta_path = "ai_engine/faiss_store/clinical_experience/experience_meta.npy"
    count = len(np.load(meta_path, allow_pickle=True))
    print(f"Total stored cases: {count}")

    print("\n--- 3. Testing Personalized Retrieval ---")
    # Query for similar Breast case
    new_patient = {"cancer_type": "Breast", "age": 53, "genomicProfile": {"HER2": "Positive"}}
    results = retrieve_similar_experience(new_patient, top_k=1)
    
    if results:
        print(f"Match: {results[0]['treatment_plan']['primary_treatment']}")
        print(f"Type: {'Correction' if 'CLINICAL_CORRECTION' in results[0]['text'] else 'Standard'}")
        print(f"Score: {results[0]['similarity_score']:.4f}")

if __name__ == "__main__":
    run_automated_learning_test()

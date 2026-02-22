import numpy as np
import os

meta_path = "ai_engine/faiss_store/clinical_experience/experience_meta.npy"

if os.path.exists(meta_path):
    all_meta = np.load(meta_path, allow_pickle=True)
    print(f"--- AI MEMORY REPORT ({len(all_meta)} cases stored) ---")
    for i, entry in enumerate(all_meta):
        print(f"Case {i+1}] ID: {entry['patient_id']}")
        print(f"Timestamp: {entry['timestamp']}")
        print(f"Clinical Features: {entry['text'][:150]}...")
        print(f"Treatment: {entry['treatment_plan']['primary_treatment']}")
        print(f"Feedback Score: {entry['feedback_score']}")
else:
    print("Memory is empty. Approve a treatment plan in the UI or run the test script first.")

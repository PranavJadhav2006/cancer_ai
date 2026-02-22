# utils/clinical_memory.py

import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from datetime import datetime

# Use the same model as the RAG system for consistency
EMBED = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_DIR = os.path.join(BASE_DIR, "faiss_store", "clinical_experience")

os.makedirs(MEMORY_DIR, exist_ok=True)

def _get_index_path():
    return os.path.join(MEMORY_DIR, "experience_index.bin")

def _get_meta_path():
    return os.path.join(MEMORY_DIR, "experience_meta.npy")

def serialize_case(patient_data, treatment_plan):
    """
    Deep Multimodal Serialization: Converts raw clinical, genomic, and imaging 
    metrics into a dense feature string for precise similarity matching.
    """
    # 1. Core Clinical Features
    cancer_type = patient_data.get('cancer_type', 'Unknown')
    stage = patient_data.get('stage', 'Unknown')
    age = patient_data.get('age', 'Unknown')
    kps = patient_data.get('kps', 'Unknown')

    # 2. Structured Genomic Profile (Extracting high-impact markers)
    genomics = patient_data.get('genomicProfile', {})
    if isinstance(genomics, str):
        try: genomics = json.loads(genomics)
        except: genomics = {}
    
    # 3. Imaging Ratios (Volume metrics)
    img = patient_data.get('imaging_metrics', {})
    tumor_vol = img.get('tumor_vol', 0)
    edema_vol = img.get('edema_vol', 0)
    vol_ratio = f"Ratio: {float(tumor_vol)/float(edema_vol):.2f}" if edema_vol and float(edema_vol) > 0 else "N/A"

    profile = [
        f"TYPE: {cancer_type}",
        f"STAGE: {stage}",
        f"AGE: {age}",
        f"KPS: {kps}",
        f"GENOMIC_KEYS: {','.join(genomics.keys())}",
        f"GENOMIC_VALS: {json.dumps(genomics)}",
        f"TUMOR_VOL: {tumor_vol}cm3",
        f"EDEMA_VOL: {edema_vol}cm3",
        f"VOL_RATIO: {vol_ratio}",
        f"SELECTED_TREATMENT: {treatment_plan.get('primary_treatment', 'Standard')}",
        f"RATIONALE_KEYS: {','.join(treatment_plan.get('rationale', [])[:3])}"
    ]
    return " | ".join(profile)

def save_experience(patient_data, treatment_plan, feedback_score=1.0, is_correction=False):
    """
    Vectorizes case with weighting. 
    is_correction=True means the human doctor modified the AI's suggestion.
    """
    case_text = serialize_case(patient_data, treatment_plan)
    
    # If it's a correction, we give it more weight/visibility in future retrievals
    # by slightly prefixing the text to bias the embedding
    if is_correction:
        case_text = f"CLINICAL_CORRECTION: {case_text}"
        feedback_score *= 1.5 

    vector = EMBED.encode([case_text], convert_to_numpy=True)
    
    meta_entry = {
        "text": case_text,
        "patient_id": patient_data.get("patientId", "unknown"),
        "timestamp": datetime.now().isoformat(),
        "treatment_plan": treatment_plan,
        "feedback_score": feedback_score
    }

    index_path = _get_index_path()
    meta_path = _get_meta_path()

    if os.path.exists(index_path):
        index = faiss.read_index(index_path)
        all_meta = list(np.load(meta_path, allow_pickle=True))
    else:
        dim = vector.shape[1]
        index = faiss.IndexFlatL2(dim)
        all_meta = []

    index.add(vector)
    all_meta.append(meta_entry)

    faiss.write_index(index, index_path)
    np.save(meta_path, np.array(all_meta, dtype=object))
    
    print(f"[MEMORY] Successfully indexed experience for case {meta_entry['patient_id']}")
    return True

def retrieve_similar_experience(patient_data, top_k=3):
    """
    Searches memory for similar past cases to provide context for the current patient.
    """
    index_path = _get_index_path()
    meta_path = _get_meta_path()

    if not os.path.exists(index_path):
        return []

    # Vectorize the current patient profile (without the treatment plan part)
    current_profile = serialize_case(patient_data, {"primary_treatment": ""})
    query_vector = EMBED.encode([current_profile], convert_to_numpy=True)

    index = faiss.read_index(index_path)
    all_meta = np.load(meta_path, allow_pickle=True)

    distances, indices = index.search(query_vector, top_k)
    
    results = []
    for i, idx in enumerate(indices[0]):
        if idx != -1 and idx < len(all_meta):
            entry = all_meta[idx]
            entry["similarity_score"] = float(1 / (1 + distances[0][i])) # Normalize distance
            results.append(entry)
            
    return results

def get_memory_stats():
    """
    Aggregates statistics from the local experience store for the dashboard.
    """
    meta_path = _get_meta_path()
    if not os.path.exists(meta_path):
        return {"total_cases": 0, "corrections": 0, "distribution": {}}

    all_meta = np.load(meta_path, allow_pickle=True)
    
    total = len(all_meta)
    corrections = sum(1 for m in all_meta if "CLINICAL_CORRECTION" in m['text'])
    
    # Analyze distribution by cancer type
    distribution = {}
    for m in all_meta:
        # Extract cancer type from serialized text (Simple parsing)
        try:
            c_type = m['text'].split('TYPE: ')[1].split(' |')[0]
            distribution[c_type] = distribution.get(c_type, 0) + 1
        except:
            continue

    return {
        "total_cases": total,
        "expert_corrections": corrections,
        "standard_approvals": total - corrections,
        "cancer_type_distribution": distribution,
        "learning_density": round((corrections / total * 100), 1) if total > 0 else 0,
        "last_updated": all_meta[-1]['timestamp'] if total > 0 else None
    }

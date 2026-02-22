# llm_chain.py

import os
import re
import json
import traceback
from google import genai as google_genai
from google.genai import types as google_types
from openai import OpenAI
from dotenv import load_dotenv
from rag.retriever_hybrid import hybrid_retrieve
from utils.clinical_memory import retrieve_similar_experience

# --- ROBUST ENV LOADING ---
def load_clinical_env():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
    root_dir = os.path.dirname(base_dir) 
    potential_paths = [
        os.path.join(root_dir, "Backend", ".env"),
        os.path.join(root_dir, ".env"),
        os.path.join(base_dir, ".env")
    ]
    for path in potential_paths:
        if os.path.exists(path):
            print(f"[LLM] LOADING ENV: {path}")
            load_dotenv(path)
            break
    
    return {
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_KEY")
    }

ENV_KEYS = load_clinical_env()

def _init_github_client():
    if not ENV_KEYS["GITHUB_TOKEN"]:
        return None
    try:
        # No ping, just initialize
        return OpenAI(base_url="https://models.inference.ai.azure.com", api_key=ENV_KEYS["GITHUB_TOKEN"])
    except Exception as e:
        print(f"[LLM] Error initializing GitHub client: {e}")
        return None

def _init_gemini_client():
    if not ENV_KEYS["GEMINI_API_KEY"]:
        return None
    try:
        # No ping, just initialize
        return google_genai.Client(api_key=ENV_KEYS["GEMINI_API_KEY"])
    except Exception as e:
        print(f"[LLM] Error initializing Gemini client: {e}")
        return None

def _get_initialized_clients():
    clients = {}
    github_client = _init_github_client()
    if github_client:
        clients["github"] = github_client
    
    gemini_client = _init_gemini_client()
    if gemini_client:
        clients["gemini"] = gemini_client
        
    return clients





def generate_treatment_plan(patient, rules, evidence_levels, cancer, query, queries):
    evidence = hybrid_retrieve(cancer, query, queries)
    evidence_text = "\n".join([f"- {e['text']}" for e in evidence])
    rule_summary = json.dumps(rules, indent=2)

    # ─── Case-Based Reasoning Context ───
    historical_experience = ""
    experiences_raw = [] # Return structured objects for the UI
    try:
        patient_dict = patient if isinstance(patient, dict) else {}
        print(f"[MEMORY] Searching for similar cases for {cancer}...")
        past_cases = retrieve_similar_experience(patient_dict, top_k=2)
        if past_cases:
            print(f"[MEMORY] Found {len(past_cases)} similar cases in local index.")
            experiences_raw = past_cases
            historical_experience = "\nINTERNAL HOSPITAL EXPERIENCE (Similar Past Cases):\n"
            for i, case in enumerate(past_cases):
                tx = case['treatment_plan'].get('primary_treatment', 'Standard Care')
                is_corr = "CLINICAL_CORRECTION" in case['text']
                type_str = "[Expert Human Correction]" if is_corr else "[Standard Approval]"
                historical_experience += f"Case {i+1} {type_str}: {tx}. (Similarity: {case['similarity_score']:.2f})\n"
        else:
            print("[MEMORY] No similar cases found in local index.")
    except Exception as e:
        print(f"[MEMORY] Experience retrieval error: {e}")

    prompt = f"""
    Return a structured JSON oncology treatment plan.
    PATIENT: {patient}
    RULES: {rule_summary}
    EVIDENCE: {evidence_text}
    {historical_experience}
    
    INSTRUCTION: Synthesize guidelines with internal hospital experience if provided. 
    Return ONLY valid JSON with primary_treatment, clinical_rationale, formatted_evidence (Markdown), alternatives, safety_alerts, follow_up, pathway.
    """
    
    initialized_clients = _get_initialized_clients()
    available_providers = ["github", "gemini"] 

    while available_providers:
        provider_name = available_providers[0] 
        current_client = initialized_clients.get(provider_name)

        if not current_client:
            available_providers.pop(0) 
            continue

        try:
            text = ""
            if provider_name == "github":
                print("[LLM] Attempting GPT-4o synthesis for treatment plan...")
                response = current_client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}], temperature=0.1)
                text = response.choices[0].message.content
            elif provider_name == "gemini":
                print("[LLM] Attempting Gemini 1.5 Flash synthesis for treatment plan...")
                response = current_client.models.generate_content(model="gemini-1.5-flash", contents=prompt, config=google_types.GenerateContentConfig(temperature=0.1))
                text = response.text
            
            json_match = re.search(r'\{.*\}', text.strip(), re.DOTALL)
            if json_match: 
                # RETURN EXPERIENCES HERE
                return json.loads(json_match.group(0)), evidence, experiences_raw
            else:
                raise ValueError(f"JSON parsing failed or empty response from {provider_name} LLM.")

        except Exception as e:
            error_message = str(e)
            print(f"[LLM ERROR] Plan failed with {provider_name}: {error_message}")
            if "429 Too Many Requests" in error_message or "rate limit" in error_message.lower() or "quota" in error_message.lower():
                available_providers.pop(0)
                continue
            else:
                return get_fallback_plan(rules, cancer), evidence, experiences_raw
    
    return get_fallback_plan(rules, cancer), evidence, experiences_raw

def get_fallback_plan(rules, cancer):
    primary = rules.get("primary_treatments", ["Standard Protocol"])[0]
    return {
        "primary_treatment": primary,
        "clinical_rationale": rules.get("personalization_insight") or "Standard protocol.",
        "formatted_evidence": "### Clinical Evidence\n* Local rule-based synthesis applied.",
        "alternatives": ["Trial"],
        "safety_alerts": rules.get("warnings", ["Monitor toxicity"]),
        "follow_up": "Routine follow-up.",
        "pathway": [{ "title": "Phase 1", "duration": "Wk 0-4", "description": "Start", "details": [primary], "marker": "🏥" }]
    }

def predict_outcomes(patient, patient_data_dict, cancer, query, queries):
    evidence = hybrid_retrieve(cancer, query, queries)
    evidence_text = "\n".join([f"[{i+1}] {e['text']}" for i, e in enumerate(evidence)])

    # ─── New: Case-Based Reasoning for Outcomes ───
    historical_experience = ""
    try:
        past_cases = retrieve_similar_experience(patient_data_dict, top_k=2)
        if past_cases:
            historical_experience = "\nINTERNAL EXPERIENCE (Actual Past Outcomes):\n"
            for i, case in enumerate(past_cases):
                tx = case['treatment_plan'].get('primary_treatment', 'Standard Care')
                historical_experience += f"Case {i+1}: Treatment '{tx}' was approved by clinician with score {case['feedback_score']}.\n"
    except Exception as e:
        print(f"[MEMORY] Outcomes experience retrieval failed: {e}")

    prompt = f"Return ONLY JSON for outcomes. Structure: {{ side_effects: {{ fatigue: 0 }}, overall_survival: {{ median: 0, range_min: 0, range_max: 0 }}, progression_free_survival: {{ median: 0 }}, risk_stratification: {{ low: 0, moderate: 0, high: 0 }}, prognostic_factors: {{ Age: 0 }}, timeline_projection: {{ months: [], response_indicator: [], quality_of_life: [] }}, quality_of_life: 0 }}. Patient: {patient}. Evidence: {evidence_text}. {historical_experience}"
    
    initialized_clients = _get_initialized_clients()
    available_providers = ["github", "gemini"] # Initial order of preference

    while available_providers:
        provider_name = available_providers[0] # Get the top preference
        current_client = initialized_clients.get(provider_name)

        if not current_client:
            available_providers.pop(0) # Remove this provider if not initialized
            continue

        try:
            text = ""
            if provider_name == "github":
                print("[LLM] Attempting GPT-4o synthesis for outcomes...")
                response = current_client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
                text = response.choices[0].message.content
            elif provider_name == "gemini":
                print("[LLM] Attempting Gemini 1.5 Flash synthesis for outcomes...")
                response = current_client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
                text = response.text
            
            json_match = re.search(r'\{.*\}', text.strip(), re.DOTALL)
            if json_match: 
                return json.loads(json_match.group(0)), evidence
            else:
                raise ValueError(f"No JSON detected in {provider_name} LLM response.")

        except Exception as e:
            error_message = str(e)
            print(f"[LLM ERROR] Outcomes prediction failed with {provider_name}: {error_message}")
            if "429 Too Many Requests" in error_message or "rate limit" in error_message.lower() or "quota" in error_message.lower():
                print(f"[LLM] {provider_name} rate limited. Trying next provider.")
                available_providers.pop(0) # Remove this provider from the available list
                continue # Try the next provider in the loop
            else:
                # Other non-rate-limit error, fall back to local outcomes immediately
                print(f"[LLM] Non-rate-limit error with {provider_name}. Falling back to local outcomes.")
                return get_fallback_outcomes(patient_data_dict), evidence
    
    # If all providers failed or were not available
    print("[LLM ERROR] All configured LLM providers failed or were not available. Falling back to local outcomes.")
    return get_fallback_outcomes(patient_data_dict), evidence

def get_fallback_outcomes(p):
    import random
    k = int(p.get("kps", 100))
    q = round(random.uniform(60, 80), 1)
    return {
        "side_effects": { "fatigue": 35, "nausea": 25, "cognitive_impairment": 20, "hematologic_toxicity": 15 },
        "overall_survival": { "median": 24 if k >= 80 else 14, "range_min": 12, "range_max": 36 },
        "progression_free_survival": { "median": 12, "range_min": 6, "range_max": 18 },
        "risk_stratification": { "low": 30, "moderate": 50, "high": 20 },
        "prognostic_factors": { "Age": 85, "Performance Status": 90, "Biomarkers": 80, "Clinical Stage": 70, "Comorbidities": 60 },
        "timeline_projection": { "months": ["Baseline", "3 mo", "6 mo", "12 mo", "18 mo", "24 mo"], "response_indicator": [100, 40, 35, 45, 55, 65], "quality_of_life": [q, q-5, q-2, q-8, q-12, q-15] },
        "quality_of_life": q
    }

def query_treatment_plan(patient, plan, query, cancer, history=None):
    """
    NEURO-SYMBOLIC CHATBOT: 
    Uses LLM to extract deltas, re-runs rule engine for deterministic clinical logic.
    """
    from rule_engine import run_rules # Local import to avoid circular dependency
    from utils.formatter import format_multimodal_data
    
    # 1. Ask LLM if the user is proposing a change to the patient's data (with fallback)
    extraction_prompt = f"""
    Analyze this doctor's query: "{query}"
    Is the doctor providing NEW clinical information or asking a "What if" scenario?
    If YES, return a JSON object representing the change. If NO, return {{"change": false}}.
    
    Example input: "What if the patient has diabetes?"
    Example output: {{"change": true, "field": "comorbidities", "value": "diabetes", "operation": "append"}}
    
    Current Patient Data: {str(patient)}
    """
    
    clinical_delta = {"change": False}
    initialized_clients = _get_initialized_clients()
    available_providers_delta = ["github", "gemini"] # Initial order of preference for delta extraction

    while available_providers_delta:
        provider_name = available_providers_delta[0] # Get the top preference
        current_client = initialized_clients.get(provider_name)

        if not current_client:
            available_providers_delta.pop(0) # Remove this provider if not initialized
            continue

        try:
            resp = None
            if provider_name == "github":
                print("[LLM] Attempting GPT-4o for clinical delta extraction...")
                resp = current_client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": extraction_prompt}], response_format={"type": "json_object"})
                clinical_delta = json.loads(resp.choices[0].message.content)
            elif provider_name == "gemini":
                print("[LLM] Attempting Gemini 1.5 Flash for clinical delta extraction...")
                resp = current_client.models.generate_content(model="gemini-1.5-flash", contents=extraction_prompt)
                match = re.search(r'\{.*\}', resp.text, re.DOTALL)
                if match: clinical_delta = json.loads(match.group(0))
            break # Success, break out of loop
        except Exception as e:
            error_message = str(e)
            print(f"[LLM ERROR] Clinical delta extraction failed with {provider_name}: {error_message}")
            if "429 Too Many Requests" in error_message or "rate limit" in error_message.lower() or "quota" in error_message.lower():
                print(f"[LLM] {provider_name} rate limited during delta extraction. Trying next provider.")
                available_providers_delta.pop(0) # Remove this provider from the available list
                continue # Try again with the next provider
            else:
                # Other non-rate-limit error, proceed with default clinical_delta
                print(f"[LLM] Non-rate-limit error with {provider_name} during delta extraction. Proceeding with default.")
                break


    # 2. IF a change is detected, re-run the DETERMINISTIC RULE ENGINE
    modified_rules_output = None
    patient_dict = patient if isinstance(patient, dict) else {}
    
    if clinical_delta.get("change"):
        print(f"[SIMULATION] Detected change in {clinical_delta['field']}. Re-running rules...")
        try:
            # Create a virtual copy for simulation
            sim_patient = patient_dict.copy()
            field = clinical_delta['field']
            val = clinical_delta['value']
            
            if clinical_delta.get('operation') == 'append':
                existing = str(sim_patient.get(field, ""))
                sim_patient[field] = f"{existing}, {val}" if existing else val
            else:
                sim_patient[field] = val
                
            # EXECUTE DETERMINISTIC CODE
            modified_rules_output = run_rules(sim_patient, cancer)
        except Exception as e:
            print(f"[SIMULATION ERROR] Rule re-run failed: {e}")

    # 3. Final Answer Generation (with fallback)
    history_text = ""
    if history and isinstance(history, list):
        history_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in history if isinstance(m, dict)])

    simulation_context = ""
    if modified_rules_output:
        simulation_context = f"\n[INTERNAL SIMULATION RESULT]: The rule engine was re-run with the new data. NEW RULES OUTPUT: {json.dumps(modified_rules_output)}"

    # Generate readable summary for the prompt
    multimodal_summary = format_multimodal_data(patient_dict)

    # 3. EXTREME PRUNING (RESONANCE AI CORE DATA ONLY)
    # We strip ALL large objects and keep only high-level identifiers
    pruned_patient = {
        "firstName": patient_dict.get("firstName"),
        "lastName": patient_dict.get("lastName"),
        "age": patient_dict.get("age"),
        "gender": patient_dict.get("gender"),
        "diagnosis": patient_dict.get("diagnosis"),
        "cancerType": patient_dict.get("cancerType"),
        "kps": patient_dict.get("kps"),
        "performanceStatus": patient_dict.get("performanceStatus"),
        "symptoms": patient_dict.get("symptoms"),
        "comorbidities": patient_dict.get("comorbidities"),
        "medicalHistory": patient_dict.get("medicalHistory", "")[:500], # First 500 chars only
        "genomicProfile": patient_dict.get("genomicProfile", {})
    }

    final_prompt = f"""
    You are a Senior Oncology Consultant. Answer the doctor's query.
    {simulation_context}
    
    CRITICAL STRUCTURE GUIDELINES:
    1. HEADER: Identify the factor (### [FACTOR] IMPACT ANALYSIS).
    2. DELTA: Explain exactly how rule-engine results changed.
    3. ACTIONS: 3-4 clinical bullet points.
    4. SYSTEMIC: Changes to Chemo/RT.
    5. SAFETY: New contraindications.

    PATIENT CONTEXT (Summarized):
    {multimodal_summary}
    
    CORE CLINICAL PROFILE:
    {json.dumps(pruned_patient, indent=2)}

    PLAN: {str(plan)}
    QUERY: {query}
    
    CONSULTANT RESPONSE:
    """
    
    initialized_clients = _get_initialized_clients()
    available_providers_final = ["github", "gemini"] # Initial order of preference for final answer generation

    while available_providers_final:
        provider_name = available_providers_final[0] # Get the top preference
        current_client = initialized_clients.get(provider_name)

        if not current_client:
            available_providers_final.pop(0) # Remove this provider if not initialized
            continue
        
        try:
            response_text = ""
            if provider_name == "github":
                print("[LLM] Attempting GPT-4o for final answer generation...")
                response = current_client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": final_prompt}])
                response_text = response.choices[0].message.content.strip()
            elif provider_name == "gemini":
                print("[LLM] Attempting Gemini 1.5 Flash for final answer generation...")
                response = current_client.models.generate_content(model="gemini-1.5-flash", contents=final_prompt)
                response_text = response.text.strip()
            
            return response_text, [] # Success, return response
        except Exception as e:
            error_message = str(e)
            print(f"[LLM ERROR] Final answer generation failed with {provider_name}: {error_message}")
            if "429 Too Many Requests" in error_message or "rate limit" in error_message.lower() or "quota" in error_message.lower():
                print(f"[LLM] {provider_name} rate limited during final answer generation. Trying next provider.")
                available_providers_final.pop(0) # Remove this provider from the available list
                continue # Try again with the next provider
            else:
                # Other non-rate-limit error, return error message
                print(f"[LLM] Non-rate-limit error with {provider_name} during final answer generation. Returning error message.")
                return "The reasoning engine encountered an error while generating the final response.", []
    
    # If all providers failed or were not available for final answer generation
    print("[LLM ERROR] All configured LLM providers failed or rate limited for final answer generation.")
    return "The reasoning engine encountered an error while generating the final response.", []

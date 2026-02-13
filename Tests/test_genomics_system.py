import os
import sys
import json

# Add ai_engine to path
sys.path.append(os.path.join(os.getcwd(), 'ai_engine'))

from utils.vcf_parser import parse_vcf
from rule_engine.rule_engine import run_rules
from llm.llm_chain import generate_treatment_plan

def test_genomics_pipeline():
    print("=== STARTING GENOMICS PIPELINE TEST ===
")

    # 1. Test VCF Parsing
    vcf_path = os.path.join('genomics', 'breast_simple.vcf')
    print(f"[STEP 1] Parsing VCF: {vcf_path}")
    vcf_result = parse_vcf(vcf_path)
    
    if not vcf_result['success']:
        print(f"FAILED: {vcf_result.get('error')}")
        return

    print(f"Found {vcf_result['stats']['actionable_found']} actionable variants.")
    print(f"Stats: {vcf_result['stats']}")
    
    # 2. Prepare Patient Data for Rule Engine
    patient = {
        "cancer_type": "Breast",
        "stage": "II",
        "kps": 90,
        "age": 45,
        "genomicProfile": {}
    }
    
    # Merge VCF markers into profile
    for marker_id, data in vcf_result['markers'].items():
        patient[marker_id] = data['value']
        print(f"Mapped {data['gene']} ({data['value']}) [Tier: {data['evidence_tier']}]")

    # 3. Test Rule Engine
    print(f"
[STEP 2] Running Rule Engine for {patient['cancer_type']} Stage {patient['stage']}...")
    rules = run_rules(patient, patient['cancer_type'])
    
    if "error" in rules:
        print(f"FAILED: {rules['error']}")
        return

    print(f"Primary Treatments: {rules['primary_treatments']}")
    print(f"Evidence Tags Found: {len(rules['evidence_levels'])}
")
    for el in rules['evidence_levels']:
        print(f"  - {el['treatment']}: {el['level']}")

    # 4. Test LLM Generation
    print("
[STEP 3] Generating AI Treatment Plan (Incorporating Evidence Levels)...")
    
    try:
        plan, evidence = generate_treatment_plan(
            patient=f"45yo Female, Breast Cancer Stage II, KPS 90. BRCA: {patient.get('brca', 'Unknown')}",
            rules=rules,
            evidence_levels=rules['evidence_levels'],
            cancer="Breast",
            query="Breast cancer treatment",
            queries=["Breast cancer treatment"]
        )
        print("
=== AI RECOMMENDED PLAN ===")
        print(json.dumps(plan, indent=2))
    except Exception as e:
        print(f"
LLM Step skipped or failed: {e}")

if __name__ == "__main__":
    test_genomics_pipeline()

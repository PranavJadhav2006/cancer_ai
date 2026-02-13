import pandas as pd
import numpy as np
import os
import json
from lifelines import CoxPHFitter

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SURVIVAL_DATA_PATH = os.path.join(os.path.dirname(BASE_DIR), "Segmentation Model", "survival_info.csv")
DRUG_KB_PATH = os.path.join(BASE_DIR, "config", "drug_knowledge.json")
PROGNOSTIC_DATA_PATH = os.path.join(BASE_DIR, "config", "prognostic_data.json")

class OutcomeEngine:
    def __init__(self):
        self.cph = CoxPHFitter()
        self.is_brain_model_trained = False
        self.drug_kb = {}
        self.prognostic_data = {}
        
        # Load Knowledge Bases
        self.load_configs()
        
        # Train Brain Model (since we have the CSV)
        self.train_brain_model()

    def load_configs(self):
        try:
            with open(DRUG_KB_PATH, 'r') as f:
                self.drug_kb = json.load(f)
            with open(PROGNOSTIC_DATA_PATH, 'r') as f:
                self.prognostic_data = json.load(f)
        except Exception as e:
            print(f"[Outcome Engine] Config loading error: {e}")

    def train_brain_model(self):
        """Trains CoxPH model strictly for Brain Cancer (BraTS data)."""
        try:
            if not os.path.exists(SURVIVAL_DATA_PATH):
                print("[Outcome Engine] Brain survival CSV not found. Using parametric fallback.")
                return

            df = pd.read_csv(SURVIVAL_DATA_PATH)
            
            # 1. Preprocessing Survival Days and Events
            # Some entries are like 'ALIVE (361 days later)'
            import re
            def parse_days(val):
                val = str(val)
                if 'ALIVE' in val.upper():
                    match = re.search(r'(\d+)', val)
                    return int(match.group(1)) if match else 0, 0 # censored
                try:
                    # Clean and convert to float first to handle potential decimals/whitespace
                    clean_val = re.sub(r'[^0-9.]', '', val)
                    return int(float(clean_val)), 1 # death event
                except:
                    return 0, 0

            parsed = df['Survival_days'].apply(parse_days)
            df['duration'] = [p[0] for p in parsed]
            df['event'] = [p[1] for p in parsed]
            
            # 2. Filter out invalid rows (duration <= 0)
            df = df[df['duration'] > 0].copy()

            # 3. Encoding: GTR=1, STR/NA=0
            df['resection_num'] = df['Extent_of_Resection'].apply(lambda x: 1 if x == 'GTR' else 0)
            
            # Feature Subset
            train_df = df[['Age', 'duration', 'event', 'resection_num']].copy()
            
            self.cph.fit(train_df, duration_col='duration', event_col='event')
            self.is_brain_model_trained = True
            print(f"[Outcome Engine] Brain CoxPH Model Trained. C-Index: {self.cph.concordance_index_:.2f}")
        except Exception as e:
            print(f"[Outcome Engine] Brain model training failed: {e}")

    def predict_survival(self, patient_data):
        """
        Master prediction router.
        Uses CoxPH for Brain, and Parametric Engine for others.
        """
        cancer_type = patient_data.get('cancer_type', 'Brain')
        
        if cancer_type == 'Brain' and self.is_brain_model_trained:
            return self._predict_brain_cox(patient_data)
        else:
            return self._predict_parametric(patient_data, cancer_type)

    def _predict_brain_cox(self, patient_data):
        """
        Specific pipeline for Brain cancer using real ML model + genomic offsets.
        """
        try:
            # 1. Base Prediction (Age + Resection)
            age = float(patient_data.get('age') or 50)
            resection = 1 if patient_data.get('resection') == 'GTR' else 0
            
            input_df = pd.DataFrame([{'Age': age, 'resection_num': resection}])
            
            # predict_median returns a series or scalar depending on version/input
            prediction = self.cph.predict_median(input_df)
            if hasattr(prediction, 'values'):
                base_median_days = float(prediction.values[0]) if len(prediction) > 0 else 450.0
            else:
                base_median_days = float(prediction)
            
            # 2. Apply Genomic Offsets (IDH, MGMT) from Prognostic KB
            total_hr = 1.0
            genomics = patient_data.get('genomicProfile', {})
            brain_kb = self.prognostic_data.get("Brain", {}).get("hazard_ratios", {})

            # IDH
            idh = genomics.get('IDH') or genomics.get('idh1')
            if idh in brain_kb.get("IDH1", {}):
                total_hr *= brain_kb["IDH1"][idh]
            
            # MGMT
            mgmt = genomics.get('MGMT') or genomics.get('mgmt')
            if mgmt in brain_kb.get("MGMT", {}):
                total_hr *= brain_kb["MGMT"][mgmt]

            # 3. Tumor Volume Offset (from MRI)
            mri = patient_data.get('mriPaths', {})
            if isinstance(mri, dict) and mri.get('tumorVolume'):
                vol = float(mri['tumorVolume'])
                if vol > 40: total_hr *= 1.2 
                elif vol < 15: total_hr *= 0.9 

            # Calculate Final
            adj_median_months = (base_median_days / 30.44) / total_hr
            
            # Cap realistic maximums for GBM
            adj_median_months = min(120.0, adj_median_months)
            
            return self._format_output(adj_median_months, self.cph.concordance_index_ * 100)

        except Exception as e:
            print(f"[Outcome Engine] Brain prediction error: {e}")
            return self._predict_parametric(patient_data, 'Brain')

    def _predict_parametric(self, patient_data, cancer_type):
        """
        General engine for Breast, Lung, Liver, Pancreas.
        Uses Baseline Median from literature * Composite Hazard Ratio.
        """
        config = self.prognostic_data.get(cancer_type, self.prognostic_data.get('Brain'))
        base_median = config.get("baseline_mOS", 12.0)
        hrs = config.get("hazard_ratios", {})
        
        total_hr = 1.0
        genomics = patient_data.get('genomicProfile', {})
        
        # 1. Stage HR
        stage_raw = str(patient_data.get('stage', 'IV')).upper()
        stage = stage_raw.replace('STAGE', '').strip()
        
        if stage in hrs.get("Stage", {}):
            total_hr *= hrs["Stage"][stage]
        else:
            # Fallback for common staging (I, II, III, IV)
            for s_key in hrs.get("Stage", {}):
                if s_key in stage:
                    total_hr *= hrs["Stage"][s_key]
                    break

        # 2. Genomic/Biomarker HRs
        for marker, values in hrs.items():
            if marker == "Stage": continue
            val = genomics.get(marker) or genomics.get(marker.lower()) or genomics.get(marker.upper())
            if val and val in values:
                total_hr *= values[val]

        # 3. Clinical Factors (Age, KPS)
        age = float(patient_data.get('age') or 50)
        kps = int(patient_data.get('kps') or 100)
        
        if age > 70: total_hr *= 1.3
        if kps < 70: total_hr *= 1.5

        # Calculate Final
        adj_median_months = base_median / total_hr
        
        # Cap realistic maximums (e.g. 20 years for Breast)
        max_survival = 240.0 if cancer_type == 'Breast' else 120.0
        adj_median_months = min(max_survival, adj_median_months)
        
        # Artificial confidence score based on data completeness
        confidence = 85.0
        if not genomics: confidence -= 15
        
        return self._format_output(adj_median_months, confidence)

    def _format_output(self, median, confidence):
        return {
            "median": round(median, 1),
            "range_min": round(median * 0.5, 1),
            "range_max": round(median * 1.8, 1), # Cancer survival is right-skewed
            "confidence": round(confidence, 1)
        }

    def predict_toxicity(self, drugs, patient_data):
        """
        Pharmacological risk mapper with frailty scaling.
        """
        risks = {
            "fatigue": 5,
            "nausea": 5,
            "cognitive_impairment": 0,
            "hematologic_toxicity": 0,
            "cardiac_toxicity": 0
        }

        # 1. Base Drug Mapping
        for drug in drugs:
            # Fuzzy find drug in KB
            found = False
            for kb_drug, profile in self.drug_kb.items():
                if kb_drug.lower() in drug.lower():
                    found = True
                    for effect, prob in profile.items():
                        if effect in risks:
                            risks[effect] = max(risks[effect], prob) # Take max risk of the combo
                        elif effect != "evidence_level":
                            risks[effect] = prob
            
            # Default chemo toxicity if drug not in KB but implies chemo
            if not found and ("platin" in drug.lower() or "rubicin" in drug.lower()):
                risks["nausea"] = max(risks["nausea"], 40)
                risks["fatigue"] = max(risks["fatigue"], 50)

        # 2. Frailty Scaling (Age, KPS, Comorbidities)
        age = float(patient_data.get('age') or 50)
        kps = int(patient_data.get('kps') or 100)
        comorbidities = str(patient_data.get('comorbidities') or '').lower()

        multiplier = 1.0
        if age > 65: multiplier += 0.2
        if kps < 80: multiplier += 0.3
        
        # Apply multiplier
        for k in risks:
            risks[k] = min(95, round(risks[k] * multiplier, 1))

        # 3. Comorbidity Specific Penalties
        if "heart" in comorbidities or "cardiac" in comorbidities:
            risks["cardiac_toxicity"] = max(risks.get("cardiac_toxicity", 0) * 2, 20)
        
        return risks

# Singleton
engine = OutcomeEngine()

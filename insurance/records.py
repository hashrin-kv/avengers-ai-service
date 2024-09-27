cbc = """
Patient: Jane Doe
DOB: 06/21/1960
Report Date: 09/07/2023

Clinical Notes:
Patient reports feeling fatigued for the past month, experiencing occasional dizziness. No significant weight loss or fevers. No history of recent infections.

CBC Report:
- Hemoglobin: 9.8 g/dL (Low, reference range: 12-15.5 g/dL)
- Hematocrit: 29% (Low, reference range: 36-46%)
- White Blood Cell Count (WBC): 6,200/mm³ (Normal, reference range: 4,500-11,000/mm³)
- Platelet Count: 220,000/mm³ (Normal, reference range: 150,000-450,000/mm³)
- Mean Corpuscular Volume (MCV): 75 fL (Low, reference range: 80-100 fL)
- Mean Corpuscular Hemoglobin (MCH): 25 pg (Low, reference range: 27-33 pg)

Impression:
Anemia, likely iron deficiency (microcytic, hypochromic). Further evaluation and iron studies are recommended.
"""

lft = """
Patient: Jane Doe
DOB: 06/21/1960
Report Date: 03/15/2024

History:
Patient has a history of alcohol use and was recently diagnosed with fatty liver disease. Complaints of mild abdominal discomfort and occasional nausea. Denies jaundice or significant weight loss.

LFT Results:
- Total Bilirubin: 1.8 mg/dL (Elevated, normal < 1.2 mg/dL)
- Direct Bilirubin: 0.8 mg/dL (Elevated, normal < 0.3 mg/dL)
- ALT (Alanine Aminotransferase): 88 U/L (Elevated, reference range: 7-56 U/L)
- AST (Aspartate Aminotransferase): 102 U/L (Elevated, reference range: 10-40 U/L)
- Alkaline Phosphatase: 150 U/L (Slightly elevated, reference range: 44-147 U/L)
- Total Protein: 6.8 g/dL (Normal, reference range: 6.4-8.3 g/dL)
- Albumin: 3.5 g/dL (Normal, reference range: 3.5-5.0 g/dL)
- Globulin: 3.3 g/dL (Normal, reference range: 2.0-3.5 g/dL)

Impression:
Elevated liver enzymes consistent with alcoholic liver disease. Recommend continued abstinence from alcohol, repeat testing in 3 months.
"""

kft = """
Patient: Jane Doe
DOB: 06/21/1960
Report Date: 05/20/2023

Clinical History:
Patient has been managing hypertension for 5 years, currently on lisinopril. Recent complaints of swelling in the ankles and fatigue. No history of diabetes.

KFT Results:
- Serum Creatinine: 1.4 mg/dL (Slightly elevated, normal < 1.2 mg/dL)
- Blood Urea Nitrogen (BUN): 28 mg/dL (Elevated, normal 7-20 mg/dL)
- Estimated GFR: 60 mL/min/1.73m² (Borderline low, normal > 60 mL/min/1.73m²)
- Serum Sodium: 142 mmol/L (Normal, reference range: 135-145 mmol/L)
- Serum Potassium: 4.3 mmol/L (Normal, reference range: 3.5-5.0 mmol/L)

Impression:
Mild renal impairment, likely related to long-term hypertension. Consider adjusting antihypertensive medications and follow up with nephrologist.
"""

ecg = """
Patient: Jane Doe
DOB: 06/21/1960
Report Date: 12/12/2023

Reason for Test:
Patient presents with intermittent chest pain, radiating to the left arm. No history of heart attack. Family history of cardiovascular disease.

ECG Findings:
- Heart Rate: 82 bpm (Normal)
- Rhythm: Sinus rhythm
- PR Interval: 160 ms (Normal)
- QRS Duration: 120 ms (Normal)
- ST Segment: Slight elevation in leads II, III, and aVF
- T Waves: Inverted in leads V1-V2

Impression:
ECG findings suggest possible inferior myocardial ischemia. Recommend further evaluation with stress testing and possibly angiography.
"""

xray = """
Patient: Jane Doe
DOB: 06/21/1960
Report Date: 01/10/2024

Clinical History:
Patient reports persistent cough for 3 weeks, mild shortness of breath, and chest discomfort. Smoker for 15 years, quit 2 years ago. No fever, chills, or night sweats.

Chest X-Ray (PA View) Report:
- Lungs: Mild hyperinflation seen bilaterally. No focal consolidation or mass lesion.
- Cardiac Shadow: Enlarged cardiothoracic ratio, suggestive of mild cardiomegaly.
- Diaphragm: Normal
- Pleura: No evidence of pleural effusion
- Bony Thorax: Normal

Impression:
Mild hyperinflation consistent with chronic obstructive pulmonary disease (COPD). Mild cardiomegaly, likely related to long-standing hypertension. Recommend pulmonary function tests and follow-up with cardiology.
"""

biopsy = """
Patient: Jane Doe
DOB: 06/21/1960
Report Date: 07/29/2023

Clinical Details:
Patient underwent a biopsy of a suspicious lesion on the left breast. Family history of breast cancer (mother). No prior history of breast abnormalities.

Biopsy Findings:
- Gross Description: The specimen consists of an irregular, firm mass measuring 2.5 cm in diameter.
- Microscopic Description: The sections show invasive ductal carcinoma with a moderate degree of differentiation. Tumor cells are arranged in irregular cords and nests. The surrounding stroma shows desmoplastic reaction.
- Immunohistochemistry: Estrogen receptor (ER) positive, Progesterone receptor (PR) positive, HER2 negative.

Impression:
Invasive ductal carcinoma, moderately differentiated. ER/PR positive, HER2 negative. Recommend consultation with oncology for treatment planning.
"""

lipid_panel = """
Patient: Jane Doe
DOB: 06/21/1960
Report Date: 07/29/2023

Clinical Details:
Patient underwent a biopsy of a suspicious lesion on the left breast. Family history of breast cancer (mother). No prior history of breast abnormalities.

Biopsy Findings:
- Gross Description: The specimen consists of an irregular, firm mass measuring 2.5 cm in diameter.
- Microscopic Description: The sections show invasive ductal carcinoma with a moderate degree of differentiation. Tumor cells are arranged in irregular cords and nests. The surrounding stroma shows desmoplastic reaction.
- Immunohistochemistry: Estrogen receptor (ER) positive, Progesterone receptor (PR) positive, HER2 negative.

Impression:
Invasive ductal carcinoma, moderately differentiated. ER/PR positive, HER2 negative. Recommend consultation with oncology for treatment planning.
"""

def get_records():
    records = [cbc, lft, kft, ecg, xray, biopsy, lipid_panel]
    return records
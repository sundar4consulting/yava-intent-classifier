"""
YAVA Intent Knowledge Base - Phase 1 Commercial Profile (Inbound-3788)
47 Active Intents
"""

INTENT_KNOWLEDGE_BASE = {
    # HEALTHCARE (12)
    "INT-PHR-0001": {
        "intent_id": "INT-PHR-0001", "intent_name": "pharmacy", "category": "healthcare",
        "agent_routing": "PharmacyAgent", "priority": 2,
        "training_utterances": [
            "I need to refill my prescription", "Where can I get my medications",
            "What pharmacies are in network", "How much does my prescription cost",
            "I want to transfer my prescription", "Can I get a 90 day supply",
            "Is my drug covered", "Where is the nearest CVS", "I need to find a pharmacy",
            "What is my copay for medications", "Mail order pharmacy", "Generic vs brand name",
            "Drug formulary", "Prior authorization for medication", "Specialty pharmacy",
            "Medication tier", "Prescription history", "Drug interactions"
        ],
        "keywords": ["pharmacy", "prescription", "medication", "drug", "refill", "CVS", "formulary"]
    },
    "INT-PRC-0002": {
        "intent_id": "INT-PRC-0002", "intent_name": "precert", "category": "healthcare",
        "agent_routing": "PrecertAgent", "priority": 2,
        "training_utterances": [
            "I need prior authorization", "Does my procedure need precertification",
            "How do I get approval for surgery", "Check status of my authorization",
            "My doctor needs to submit a prior auth", "Preauthorization requirements",
            "Was my MRI approved", "Authorization denied", "Appeal a precert decision",
            "How long does prior auth take", "Emergency authorization", "Medical necessity",
            "Inpatient authorization", "Outpatient precert", "Authorization reference number",
            "Precert for imaging", "DME authorization", "Home health precert"
        ],
        "keywords": ["precert", "prior authorization", "preauth", "approval", "authorization"]
    },
    "INT-NCM-0003": {
        "intent_id": "INT-NCM-0003", "intent_name": "nurseCaseManager", "category": "healthcare",
        "agent_routing": "CareAgent", "priority": 3,
        "training_utterances": [
            "I want to speak to my nurse case manager", "Connect me to my care coordinator",
            "Who is my assigned nurse", "Case management program", "I need help managing my condition",
            "Care coordination services", "Schedule a call with my nurse", "Complex case management",
            "Transition of care support", "Post discharge follow up", "Care plan review",
            "Nurse navigator", "Health coach", "Chronic condition support", "High risk pregnancy support",
            "Cancer case management", "Transplant coordination", "Care gap closure"
        ],
        "keywords": ["nurse", "case manager", "care coordinator", "care management", "health coach"]
    },
    "INT-NRS-0004": {
        "intent_id": "INT-NRS-0004", "intent_name": "24HourNurseLine", "category": "healthcare",
        "agent_routing": "NurseLineAgent", "priority": 1,
        "training_utterances": [
            "I need to talk to a nurse", "24 hour nurse line", "Medical advice line",
            "Should I go to the ER", "Nurse hotline", "I have a health question",
            "Speak to a registered nurse", "Is this an emergency", "After hours medical help",
            "Symptom checker", "My child is sick", "Fever advice", "Poison control",
            "Allergic reaction advice", "Urgent care or ER", "Nurse triage",
            "Medical question at night", "Talk to someone about my symptoms"
        ],
        "keywords": ["nurse line", "24 hour", "nurse hotline", "medical advice", "triage"]
    },
    "INT-BEH-0005": {
        "intent_id": "INT-BEH-0005", "intent_name": "behavioralHealth", "category": "healthcare",
        "agent_routing": "BehavioralAgent", "priority": 2,
        "training_utterances": [
            "I need mental health support", "Find a therapist", "Behavioral health services",
            "Counseling coverage", "Psychiatrist in network", "Substance abuse treatment",
            "Depression help", "Anxiety treatment", "Outpatient mental health",
            "Inpatient psychiatric", "Marriage counseling", "Family therapy",
            "Psychologist coverage", "Mental health copay", "How many therapy sessions",
            "Telehealth therapy", "Eating disorder treatment", "Addiction services"
        ],
        "keywords": ["mental health", "behavioral health", "therapy", "counseling", "psychiatrist"]
    },
    "INT-BEM-0006": {
        "intent_id": "INT-BEM-0006", "intent_name": "behavioralEmergency", "category": "healthcare",
        "agent_routing": "EmergencyAgent", "priority": 1,
        "training_utterances": [
            "I am having thoughts of suicide", "Mental health crisis", "I need help now",
            "Crisis hotline", "Someone is threatening self harm", "Psychiatric emergency",
            "I feel like hurting myself", "Overdose", "988 suicide line",
            "Immediate mental health help", "Crisis intervention", "Behavioral emergency room",
            "Psychotic episode", "Danger to self or others", "Mental breakdown",
            "Suicide prevention", "Crisis stabilization", "Mobile crisis team"
        ],
        "keywords": ["crisis", "suicide", "emergency", "self harm", "psychiatric emergency", "988"]
    },
    "INT-PCP-0007": {
        "intent_id": "INT-PCP-0007", "intent_name": "primaryCareProvider", "category": "healthcare",
        "agent_routing": "PCPAgent", "priority": 2,
        "training_utterances": [
            "I need to find a primary care doctor", "Change my PCP", "Who is my primary care physician",
            "Select a new doctor", "PCP assignment", "Find a family doctor",
            "General practitioner near me", "Internal medicine doctor", "Primary care referral",
            "Switch my primary doctor", "New member PCP selection", "PCP accepting new patients",
            "Doctor taking Aetna insurance", "Primary care network", "Assign PCP for my child",
            "Primary doctor office hours", "Update my doctor information"
        ],
        "keywords": ["PCP", "primary care", "doctor", "physician", "family doctor"]
    },
    "INT-SPC-0008": {
        "intent_id": "INT-SPC-0008", "intent_name": "specialist", "category": "healthcare",
        "agent_routing": "SpecialistAgent", "priority": 2,
        "training_utterances": [
            "I need to see a specialist", "Find a cardiologist", "Dermatologist in network",
            "Orthopedic surgeon near me", "Do I need a referral for specialist", "Find an ENT doctor",
            "Neurologist coverage", "Gastroenterologist appointment", "Oncologist in my network",
            "Endocrinologist search", "Pulmonologist near me", "Rheumatologist covered",
            "Urologist in network", "Specialist copay amount", "Out of network specialist",
            "Second opinion specialist", "Specialist referral process"
        ],
        "keywords": ["specialist", "cardiologist", "dermatologist", "referral", "orthopedic"]
    },
    "INT-URG-0009": {
        "intent_id": "INT-URG-0009", "intent_name": "urgentCare", "category": "healthcare",
        "agent_routing": "UrgentCareAgent", "priority": 1,
        "training_utterances": [
            "Find urgent care near me", "Walk in clinic locations", "Urgent care vs emergency room",
            "After hours clinic", "Urgent care copay", "MinuteClinic locations", "CVS health hub",
            "Retail clinic coverage", "Weekend clinic hours", "Urgent care for my child",
            "Is urgent care covered", "Nearest urgent care open now", "Urgent care wait times",
            "In network urgent care", "Virtual urgent care", "Urgent care for stitches"
        ],
        "keywords": ["urgent care", "walk in", "clinic", "after hours", "MinuteClinic"]
    },
    "INT-EMR-0010": {
        "intent_id": "INT-EMR-0010", "intent_name": "emergencyRoom", "category": "healthcare",
        "agent_routing": "EmergencyAgent", "priority": 1,
        "training_utterances": [
            "Emergency room coverage", "ER copay amount", "Nearest emergency room",
            "Emergency services covered", "Out of network emergency", "ER vs urgent care",
            "Emergency room bill", "Hospital emergency department", "Emergency admission",
            "Trauma center location", "Emergency surgery coverage", "ER visit while traveling",
            "Emergency out of state", "Ambulance coverage", "Freestanding ER coverage"
        ],
        "keywords": ["emergency room", "ER", "emergency", "hospital", "ambulance", "trauma"]
    },
    "INT-TEL-0011": {
        "intent_id": "INT-TEL-0011", "intent_name": "telemedicine", "category": "healthcare",
        "agent_routing": "TelemedicineAgent", "priority": 2,
        "training_utterances": [
            "Telemedicine appointment", "Virtual doctor visit", "Online doctor consultation",
            "Telehealth coverage", "Video visit with doctor", "Teladoc services",
            "Virtual care options", "Phone appointment with doctor", "Remote healthcare visit",
            "E-visit coverage", "Telehealth copay", "Virtual urgent care", "Online prescription",
            "Telemedicine for mental health", "Virtual specialist visit", "Telehealth app"
        ],
        "keywords": ["telemedicine", "telehealth", "virtual", "video visit", "online doctor", "Teladoc"]
    },
    "INT-HOS-0012": {
        "intent_id": "INT-HOS-0012", "intent_name": "hospital", "category": "healthcare",
        "agent_routing": "HospitalAgent", "priority": 2,
        "training_utterances": [
            "Hospital coverage information", "Inpatient admission coverage", "Hospital stay cost",
            "In network hospitals", "Hospital precertification", "Planned hospital admission",
            "Hospital room charges", "Surgery at hospital", "Hospital outpatient services",
            "Hospital bill explanation", "Length of stay coverage", "Hospital selection help",
            "Centers of excellence hospitals", "Out of network hospital", "Skilled nursing facility"
        ],
        "keywords": ["hospital", "inpatient", "admission", "surgery", "skilled nursing"]
    },
    
    # BENEFITS (14)
    "INT-ELG-0013": {
        "intent_id": "INT-ELG-0013", "intent_name": "eligibility", "category": "benefits",
        "agent_routing": "EligibilityAgent", "priority": 1,
        "training_utterances": [
            "Am I covered", "Check my eligibility", "When does my coverage start",
            "Is my plan active", "Coverage effective date", "Verify my insurance",
            "Am I still enrolled", "When does my coverage end", "Eligibility status",
            "My benefits terminated", "Check active coverage", "Insurance verification letter",
            "Proof of coverage", "Coverage confirmation", "Am I insured", "Member eligibility"
        ],
        "keywords": ["eligibility", "coverage", "active", "enrolled", "effective date", "verify"]
    },
    "INT-BEN-0014": {
        "intent_id": "INT-BEN-0014", "intent_name": "benefits", "category": "benefits",
        "agent_routing": "BenefitsAgent", "priority": 1,
        "training_utterances": [
            "What are my benefits", "Benefits summary", "What does my plan cover",
            "Benefit details", "Coverage information", "Plan benefits explanation",
            "What services are covered", "Benefits booklet", "Summary of benefits",
            "Evidence of coverage", "Covered services list", "Benefit limits",
            "Annual maximum benefits", "Lifetime maximum", "Benefit year dates"
        ],
        "keywords": ["benefits", "coverage", "covered", "plan", "summary", "services"]
    },
    "INT-DED-0015": {
        "intent_id": "INT-DED-0015", "intent_name": "deductible", "category": "benefits",
        "agent_routing": "DeductibleAgent", "priority": 1,
        "training_utterances": [
            "What is my deductible", "How much deductible have I met", "Deductible status",
            "Annual deductible amount", "Family deductible", "Individual deductible",
            "Deductible accumulator", "When does deductible reset", "Deductible applied to claim",
            "Out of pocket vs deductible", "High deductible plan", "Deductible remaining",
            "Embedded deductible", "Deductible waived services", "Preventive care deductible"
        ],
        "keywords": ["deductible", "accumulator", "met", "remaining", "annual", "out of pocket"]
    },
    "INT-OOP-0016": {
        "intent_id": "INT-OOP-0016", "intent_name": "outOfPocketMax", "category": "benefits",
        "agent_routing": "OOPAgent", "priority": 2,
        "training_utterances": [
            "Out of pocket maximum", "What is my out of pocket limit", "Maximum out of pocket reached",
            "OOP max status", "Annual out of pocket", "Family out of pocket maximum",
            "Individual OOP max", "Out of pocket accumulator", "When is everything covered",
            "Reached my maximum", "Out of pocket remaining", "Catastrophic coverage",
            "Stop loss amount", "Out of pocket expenses", "MOOP amount"
        ],
        "keywords": ["out of pocket", "OOP", "maximum", "limit", "MOOP", "catastrophic"]
    },
    "INT-COP-0017": {
        "intent_id": "INT-COP-0017", "intent_name": "copay", "category": "benefits",
        "agent_routing": "CopayAgent", "priority": 1,
        "training_utterances": [
            "What is my copay", "Copay for doctor visit", "Specialist copay amount",
            "Copay vs coinsurance", "Prescription copay", "ER copay", "Urgent care copay",
            "Copay at time of service", "Office visit copay", "Lab work copay",
            "Imaging copay", "Therapy copay", "Copay after deductible", "Zero copay services"
        ],
        "keywords": ["copay", "copayment", "office visit", "cost", "dollar amount"]
    },
    "INT-COI-0018": {
        "intent_id": "INT-COI-0018", "intent_name": "coinsurance", "category": "benefits",
        "agent_routing": "CoinsuranceAgent", "priority": 2,
        "training_utterances": [
            "What is my coinsurance", "Coinsurance percentage", "80 20 coinsurance",
            "How coinsurance works", "Coinsurance after deductible", "In network coinsurance",
            "Out of network coinsurance", "Hospital coinsurance rate", "Surgery coinsurance",
            "Coinsurance vs copay", "My share of costs", "Percentage I pay", "Coinsurance maximum"
        ],
        "keywords": ["coinsurance", "percentage", "share", "80/20", "cost sharing"]
    },
    "INT-NET-0019": {
        "intent_id": "INT-NET-0019", "intent_name": "network", "category": "benefits",
        "agent_routing": "NetworkAgent", "priority": 1,
        "training_utterances": [
            "Is my doctor in network", "Find in network provider", "Network status check",
            "Out of network coverage", "Provider network search", "In network vs out of network",
            "Participating providers", "Network discount", "PPO network", "HMO network",
            "Narrow network plan", "Provider left network", "Continuity of care out of network",
            "Network exception request", "Tiered network", "Network directory"
        ],
        "keywords": ["network", "in network", "out of network", "provider", "participating", "PPO", "HMO"]
    },
    "INT-COB-0020": {
        "intent_id": "INT-COB-0020", "intent_name": "coordinationOfBenefits", "category": "benefits",
        "agent_routing": "COBAgent", "priority": 2,
        "training_utterances": [
            "I have two insurance plans", "Coordination of benefits", "Primary and secondary insurance",
            "Dual coverage", "Which plan pays first", "COB update", "Spouse has insurance too",
            "Medicare and Aetna", "Birthday rule coordination", "Other insurance question",
            "COB questionnaire", "Secondary insurance filing", "Double coverage"
        ],
        "keywords": ["coordination of benefits", "COB", "primary", "secondary", "dual coverage"]
    },
    "INT-DEN-0021": {
        "intent_id": "INT-DEN-0021", "intent_name": "dental", "category": "benefits",
        "agent_routing": "DentalAgent", "priority": 2,
        "training_utterances": [
            "Dental coverage", "Find a dentist", "Dental benefits", "Dental cleaning coverage",
            "Orthodontia coverage", "Dental maximum", "Dental deductible", "Root canal coverage",
            "Dental implants covered", "Wisdom teeth extraction", "Dental X-rays coverage",
            "Periodontal treatment", "Crown coverage", "Dental waiting period", "Dental network"
        ],
        "keywords": ["dental", "dentist", "teeth", "orthodontia", "cleaning", "crown"]
    },
    "INT-VIS-0022": {
        "intent_id": "INT-VIS-0022", "intent_name": "vision", "category": "benefits",
        "agent_routing": "VisionAgent", "priority": 2,
        "training_utterances": [
            "Vision coverage", "Eye exam coverage", "Find an eye doctor", "Glasses coverage",
            "Contact lenses allowance", "Vision benefits", "LASIK coverage", "Vision network",
            "Frames allowance", "Vision deductible", "Eye exam frequency", "Vision copay",
            "VSP or EyeMed", "Optometrist vs ophthalmologist", "Vision claim submission"
        ],
        "keywords": ["vision", "eye", "glasses", "contacts", "optometrist", "ophthalmologist"]
    },
    "INT-PRV-0023": {
        "intent_id": "INT-PRV-0023", "intent_name": "preventiveCare", "category": "benefits",
        "agent_routing": "PreventiveAgent", "priority": 2,
        "training_utterances": [
            "Preventive care coverage", "Annual physical covered", "Wellness exam",
            "Preventive services list", "Screenings covered", "Mammogram coverage",
            "Colonoscopy covered", "Immunizations covered", "Well child visits",
            "Preventive care no cost", "Health maintenance exam", "Cancer screening coverage",
            "Preventive vs diagnostic", "Annual checkup", "Flu shot coverage"
        ],
        "keywords": ["preventive", "wellness", "screening", "physical", "immunization", "vaccine"]
    },
    "INT-MAT-0024": {
        "intent_id": "INT-MAT-0024", "intent_name": "maternity", "category": "benefits",
        "agent_routing": "MaternityAgent", "priority": 2,
        "training_utterances": [
            "Maternity coverage", "Pregnancy benefits", "Prenatal care covered",
            "Delivery cost estimate", "Hospital stay for delivery", "Cesarean section coverage",
            "Midwife coverage", "Birth center coverage", "Newborn coverage",
            "Maternity deductible", "High risk pregnancy", "Breast pump coverage",
            "Fertility treatment", "IVF coverage", "Postpartum care", "NICU coverage"
        ],
        "keywords": ["maternity", "pregnancy", "prenatal", "delivery", "newborn", "fertility"]
    },
    "INT-REH-0025": {
        "intent_id": "INT-REH-0025", "intent_name": "rehabilitation", "category": "benefits",
        "agent_routing": "RehabAgent", "priority": 2,
        "training_utterances": [
            "Physical therapy coverage", "Rehabilitation services", "PT visits allowed",
            "Occupational therapy", "Speech therapy coverage", "Inpatient rehab",
            "Outpatient rehabilitation", "Rehab facility coverage", "Cardiac rehabilitation",
            "Pulmonary rehab", "Therapy visit limits", "Chiropractic coverage",
            "Acupuncture covered", "Therapy authorization", "Rehab after surgery"
        ],
        "keywords": ["physical therapy", "PT", "rehabilitation", "occupational therapy", "speech therapy"]
    },
    "INT-DME-0026": {
        "intent_id": "INT-DME-0026", "intent_name": "durableMedicalEquipment", "category": "benefits",
        "agent_routing": "DMEAgent", "priority": 2,
        "training_utterances": [
            "Durable medical equipment coverage", "DME benefits", "Wheelchair coverage",
            "CPAP machine covered", "Oxygen equipment", "Hospital bed rental",
            "Walker coverage", "Prosthetics coverage", "Orthotics benefits", "DME supplier",
            "DME authorization", "Medical supplies coverage", "Diabetic supplies",
            "Compression stockings", "DME repair coverage", "DME rental vs purchase"
        ],
        "keywords": ["DME", "durable medical equipment", "wheelchair", "CPAP", "prosthetics"]
    },
    
    # FINANCIAL (8)
    "INT-PRM-0027": {
        "intent_id": "INT-PRM-0027", "intent_name": "premium", "category": "financial",
        "agent_routing": "PremiumAgent", "priority": 1,
        "training_utterances": [
            "Pay my premium", "Premium due date", "Premium amount", "Monthly premium cost",
            "Premium payment options", "Autopay premium", "Premium grace period",
            "Missed premium payment", "Premium increase notice", "Premium billing question",
            "Payroll deduction premium", "Premium tax credit", "Reduce my premium"
        ],
        "keywords": ["premium", "payment", "bill", "monthly", "autopay", "payroll deduction"]
    },
    "INT-HSA-0028": {
        "intent_id": "INT-HSA-0028", "intent_name": "hsa", "category": "financial",
        "agent_routing": "HSAAgent", "priority": 2,
        "training_utterances": [
            "HSA balance", "Health savings account", "HSA contribution", "HSA eligible expenses",
            "HSA investment", "HSA card", "HSA maximum contribution", "HSA rollover",
            "HSA tax benefits", "Use HSA for dental", "HSA withdrawal", "Transfer HSA",
            "HSA employer contribution", "HSA catch up contribution", "PayFlex HSA"
        ],
        "keywords": ["HSA", "health savings account", "contribution", "balance", "eligible expenses"]
    },
    "INT-FSA-0029": {
        "intent_id": "INT-FSA-0029", "intent_name": "fsa", "category": "financial",
        "agent_routing": "FSAAgent", "priority": 2,
        "training_utterances": [
            "FSA balance", "Flexible spending account", "Healthcare FSA", "Dependent care FSA",
            "FSA eligible expenses", "FSA deadline", "Use it or lose it FSA", "FSA grace period",
            "FSA rollover amount", "FSA card", "FSA claim", "Limited purpose FSA",
            "FSA store", "What can I buy with FSA", "FSA reimbursement"
        ],
        "keywords": ["FSA", "flexible spending", "balance", "eligible expenses", "dependent care"]
    },
    "INT-HRA-0030": {
        "intent_id": "INT-HRA-0030", "intent_name": "hra", "category": "financial",
        "agent_routing": "HRAAgent", "priority": 2,
        "training_utterances": [
            "HRA balance", "Health reimbursement arrangement", "HRA eligible expenses",
            "HRA reimbursement", "HRA vs HSA", "Employer HRA contribution", "HRA rollover",
            "HRA claim submission", "HRA card", "What does HRA cover", "HRA for retirees",
            "ICHRA plan", "QSEHRA information", "HRA statement"
        ],
        "keywords": ["HRA", "health reimbursement", "arrangement", "employer funded"]
    },
    "INT-EST-0031": {
        "intent_id": "INT-EST-0031", "intent_name": "costEstimate", "category": "financial",
        "agent_routing": "EstimateAgent", "priority": 2,
        "training_utterances": [
            "Cost estimate for procedure", "How much will surgery cost", "Estimate my costs",
            "Price transparency", "Procedure cost lookup", "MRI cost estimate",
            "Hospital cost estimator", "Out of pocket estimate", "Treatment cost calculator",
            "Compare provider costs", "Good faith estimate", "No surprises act"
        ],
        "keywords": ["estimate", "cost", "price", "transparency", "calculator", "how much"]
    },
    "INT-PAY-0032": {
        "intent_id": "INT-PAY-0032", "intent_name": "paymentPlan", "category": "financial",
        "agent_routing": "PaymentAgent", "priority": 2,
        "training_utterances": [
            "Set up payment plan", "Payment arrangement", "Can I pay in installments",
            "Monthly payment option", "Financial hardship", "Medical bill payment plan",
            "Pay my medical bill", "Outstanding balance payment", "Payment plan options",
            "Interest free payment", "Healthcare financing", "Bill assistance program"
        ],
        "keywords": ["payment plan", "installments", "arrangement", "financial assistance"]
    },
    "INT-REI-0033": {
        "intent_id": "INT-REI-0033", "intent_name": "reimbursement", "category": "financial",
        "agent_routing": "ReimbursementAgent", "priority": 2,
        "training_utterances": [
            "Submit for reimbursement", "Get reimbursed for medical expense", "Reimbursement form",
            "Out of pocket reimbursement", "How to file for reimbursement", "Reimbursement status",
            "Direct deposit reimbursement", "Reimbursement check", "Foreign claim reimbursement",
            "Travel vaccination reimbursement", "Gym membership reimbursement", "Wellness reimbursement"
        ],
        "keywords": ["reimbursement", "reimburse", "submit", "out of pocket", "direct deposit"]
    },
    "INT-EOB-0034": {
        "intent_id": "INT-EOB-0034", "intent_name": "explanationOfBenefits", "category": "financial",
        "agent_routing": "EOBAgent", "priority": 2,
        "training_utterances": [
            "Explanation of benefits", "Read my EOB", "EOB meaning", "What is an EOB",
            "EOB vs bill", "EOB online access", "Download my EOB", "EOB for tax purposes",
            "EOB discrepancy", "EOB shows wrong amount", "Paper EOB preference", "Paperless EOB"
        ],
        "keywords": ["EOB", "explanation of benefits", "statement", "summary", "claim statement"]
    },
    
    # CLAIMS (4)
    "INT-CLM-0035": {
        "intent_id": "INT-CLM-0035", "intent_name": "claims", "category": "claims",
        "agent_routing": "ClaimsAgent", "priority": 1,
        "training_utterances": [
            "Check my claim status", "Submit a claim", "Claim denied", "Explanation of benefits",
            "How much do I owe", "Claims history", "Why was my claim rejected", "File a claim",
            "Claims appeal", "Out of pocket expense", "Claim processing time", "Resubmit a claim",
            "View my EOB", "Claim for reimbursement", "Pending claim", "Claim payment amount"
        ],
        "keywords": ["claim", "claims", "EOB", "denied", "status", "submit", "appeal"]
    },
    "INT-IDC-0036": {
        "intent_id": "INT-IDC-0036", "intent_name": "idCard", "category": "claims",
        "agent_routing": "IDCardAgent", "priority": 1,
        "training_utterances": [
            "I need a new ID card", "Order replacement card", "Where is my insurance card",
            "Digital ID card", "Print my ID card", "ID card not received", "Member ID number",
            "View my ID card", "Card shows wrong information", "ID card for dependent",
            "Temporary ID card", "ID card in app", "Rush ID card delivery", "Lost my insurance card"
        ],
        "keywords": ["ID card", "member card", "insurance card", "replacement", "digital"]
    },
    "INT-APL-0037": {
        "intent_id": "INT-APL-0037", "intent_name": "appeals", "category": "claims",
        "agent_routing": "AppealsAgent", "priority": 2,
        "training_utterances": [
            "Appeal a claim denial", "How to file an appeal", "Grievance process",
            "Appeal deadline", "First level appeal", "External review request",
            "Independent review", "Appeal status check", "Appeal letter template",
            "Medical records for appeal", "Expedited appeal", "Urgent appeal process"
        ],
        "keywords": ["appeal", "grievance", "denial", "external review", "overturn"]
    },
    "INT-FRD-0038": {
        "intent_id": "INT-FRD-0038", "intent_name": "fraudWasteAbuse", "category": "claims",
        "agent_routing": "FraudAgent", "priority": 3,
        "training_utterances": [
            "Report fraud", "Suspicious billing", "I didnt receive this service",
            "Waste and abuse hotline", "Fraudulent claim", "Doctor overbilling",
            "Identity theft insurance", "Report provider fraud", "Bill for service not received",
            "Duplicate billing complaint", "Upcoding suspected", "Report insurance fraud"
        ],
        "keywords": ["fraud", "abuse", "suspicious", "report", "waste", "identity theft"]
    },
    
    # WELLNESS (6)
    "INT-WEL-0039": {
        "intent_id": "INT-WEL-0039", "intent_name": "wellnessPrograms", "category": "wellness",
        "agent_routing": "WellnessAgent", "priority": 3,
        "training_utterances": [
            "Wellness program information", "Health incentive programs", "Wellness rewards",
            "Attain by Aetna", "Earn wellness points", "Fitness program coverage",
            "Gym membership discount", "Weight management program", "Smoking cessation program",
            "Health coaching", "Wellness challenges", "Biometric screening incentive"
        ],
        "keywords": ["wellness", "incentive", "program", "rewards", "fitness", "health coaching"]
    },
    "INT-GYM-0040": {
        "intent_id": "INT-GYM-0040", "intent_name": "gymFitness", "category": "wellness",
        "agent_routing": "FitnessAgent", "priority": 3,
        "training_utterances": [
            "Gym membership benefit", "Fitness center discount", "Active and Fit program",
            "Gym reimbursement", "Fitness facility network", "Planet Fitness discount",
            "LA Fitness coverage", "YMCA membership", "Home fitness program",
            "Peloton discount", "Fitness class coverage", "Silver Sneakers"
        ],
        "keywords": ["gym", "fitness", "exercise", "Active and Fit", "Silver Sneakers"]
    },
    "INT-SMK-0041": {
        "intent_id": "INT-SMK-0041", "intent_name": "smokingCessation", "category": "wellness",
        "agent_routing": "TobaccoAgent", "priority": 3,
        "training_utterances": [
            "Quit smoking program", "Smoking cessation coverage", "Nicotine patch coverage",
            "Tobacco quit line", "Chantix coverage", "Wellbutrin for smoking",
            "Quit tobacco support", "Smoking cessation counseling", "Nicotine gum covered",
            "E-cigarette cessation", "Vaping quit program", "Tobacco free incentive"
        ],
        "keywords": ["smoking", "tobacco", "quit", "cessation", "nicotine", "vaping"]
    },
    "INT-WGT-0042": {
        "intent_id": "INT-WGT-0042", "intent_name": "weightManagement", "category": "wellness",
        "agent_routing": "WeightAgent", "priority": 3,
        "training_utterances": [
            "Weight loss program", "Weight management coverage", "Bariatric surgery coverage",
            "Gastric bypass coverage", "Nutritional counseling", "Dietitian coverage",
            "Weight Watchers reimbursement", "Noom coverage", "Obesity treatment",
            "Medical weight loss", "Weight loss medication coverage", "Wegovy coverage"
        ],
        "keywords": ["weight", "obesity", "bariatric", "nutrition", "diet", "BMI"]
    },
    "INT-CHR-0043": {
        "intent_id": "INT-CHR-0043", "intent_name": "chronicConditionSupport", "category": "wellness",
        "agent_routing": "ChronicAgent", "priority": 2,
        "training_utterances": [
            "Chronic condition management", "Diabetes management program", "Heart disease support",
            "Asthma management", "COPD management program", "Hypertension program",
            "Chronic care management", "Disease management", "Ongoing condition support",
            "Long term condition help", "Chronic illness resources", "Health condition coaching"
        ],
        "keywords": ["chronic", "diabetes", "heart disease", "asthma", "COPD", "management"]
    },
    "INT-MOM-0044": {
        "intent_id": "INT-MOM-0044", "intent_name": "maternitySupport", "category": "wellness",
        "agent_routing": "MaternityAgent", "priority": 2,
        "training_utterances": [
            "Pregnancy support program", "Maternity management", "Prenatal program",
            "Healthy pregnancy program", "Beginning Right maternity", "High risk pregnancy support",
            "Pregnancy rewards", "Baby shower program", "Expecting mother resources",
            "Prenatal vitamins coverage", "Pregnancy app", "Maternity case manager"
        ],
        "keywords": ["pregnancy", "maternity", "prenatal", "postpartum", "baby", "expecting"]
    },
    
    # SERVICES (3)
    "INT-ADR-0045": {
        "intent_id": "INT-ADR-0045", "intent_name": "addressChange", "category": "services",
        "agent_routing": "ProfileAgent", "priority": 3,
        "training_utterances": [
            "Update my address", "Change my address", "New address update",
            "Moving to new location", "Address correction", "Wrong address on file",
            "Mailing address change", "Update contact information", "Change my phone number",
            "Email address update", "Profile update", "Personal information change"
        ],
        "keywords": ["address", "update", "change", "contact", "phone", "email", "profile"]
    },
    "INT-DEP-0046": {
        "intent_id": "INT-DEP-0046", "intent_name": "dependentChanges", "category": "services",
        "agent_routing": "EnrollmentAgent", "priority": 2,
        "training_utterances": [
            "Add a dependent", "Remove dependent from plan", "Newborn enrollment",
            "Add spouse to insurance", "Marriage enrollment", "Divorce remove spouse",
            "Dependent age out", "Adult child coverage", "Domestic partner enrollment",
            "Dependent eligibility", "Change dependent information", "Dependent turning 26"
        ],
        "keywords": ["dependent", "add", "remove", "spouse", "child", "enrollment", "family"]
    },
    "INT-CMP-0047": {
        "intent_id": "INT-CMP-0047", "intent_name": "complaint", "category": "services",
        "agent_routing": "ComplaintAgent", "priority": 2,
        "training_utterances": [
            "File a complaint", "I want to complain", "Grievance submission",
            "Unhappy with service", "Bad customer service", "Provider complaint",
            "Quality of care complaint", "Service complaint", "Formal complaint process",
            "Escalate my issue", "Speak to supervisor", "Customer relations"
        ],
        "keywords": ["complaint", "grievance", "unhappy", "dissatisfied", "escalate", "supervisor"]
    }
}

def get_all_intents():
    """Return list of all intent metadata."""
    return [
        {"intent_id": d["intent_id"], "intent_name": d["intent_name"], 
         "category": d["category"], "agent_routing": d["agent_routing"]}
        for d in INTENT_KNOWLEDGE_BASE.values()
    ]

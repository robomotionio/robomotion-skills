# Data Structure Specification

## Biochemical Test Data Structure

```json
{
  "id": "20251231123456789",
  "type": "生化检查",
  "date": "2025-12-31",
  "hospital": "XX Hospital",
  "items": [
    {
      "name": "White Blood Cell Count",
      "value": "6.5",
      "unit": "×10^9/L",
      "min_ref": "3.5",
      "max_ref": "9.5",
      "is_abnormal": false
    }
  ]
}
```

### Field Description
- `id`: Unique identifier (generated from timestamp)
- `type`: Examination type, fixed value "生化检查" (Biochemical Test)
- `date`: Examination date (YYYY-MM-DD format)
- `hospital`: Hospital name
- `items`: Array of test items
  - `name`: Test item name
  - `value`: Test result value
  - `unit`: Measurement unit
  - `min_ref`: Reference range lower limit
  - `max_ref`: Reference range upper limit
  - `is_abnormal`: Whether abnormal (boolean)

## Medical Imaging Data Structure

```json
{
  "id": "20251231123456789",
  "type": "影像检查",
  "subtype": "Ultrasound",
  "date": "2025-12-31",
  "hospital": "XX Hospital",
  "body_part": "Abdomen",
  "findings": {
    "description": "Examination findings description",
    "measurements": {
      "Size": "Specific value"
    },
    "conclusion": "Examination conclusion"
  },
  "original_image": "images/original.jpg"
}
```

### Field Description
- `id`: Unique identifier (generated from timestamp)
- `type`: Examination type, fixed value "影像检查" (Medical Imaging)
- `subtype`: Imaging examination subtype (Ultrasound, CT, MRI, X-ray, etc.)
- `date`: Examination date (YYYY-MM-DD format)
- `hospital`: Hospital name
- `body_part`: Body part examined
- `findings`: Examination findings object
  - `description`: Text description of examination findings
  - `measurements`: Measurement data object
  - `conclusion`: Examination conclusion
- `original_image`: Original image backup path

## Radiation Record Data Structure

```json
{
  "id": "20251231123456789",
  "exam_type": "CT",
  "body_part": "Chest",
  "exam_date": "2025-12-31",
  "standard_dose": 7.0,
  "body_surface_area": 1.85,
  "adjustment_factor": 1.07,
  "actual_dose": 7.5,
  "dose_unit": "mSv"
}
```

### Field Description
- `id`: Unique identifier (generated from timestamp)
- `exam_type`: Examination type (CT, X-ray, PET-CT, etc.)
- `body_part`: Body part examined
- `exam_date`: Examination date (YYYY-MM-DD format)
- `standard_dose`: Standard radiation dose (mSv)
- `body_surface_area`: User's body surface area (m²)
- `adjustment_factor`: Body surface area adjustment factor
- `actual_dose`: Actual radiation dose (mSv)
- `dose_unit`: Dose unit, fixed value "mSv"

## User Profile Data Structure

```json
{
  "basic_info": {
    "gender": "F",
    "height": 175,
    "height_unit": "cm",
    "weight": 70,
    "weight_unit": "kg",
    "birth_date": "1990-01-01"
  },
  "calculated": {
    "age": 35,
    "bmi": 22.9,
    "bmi_status": "Normal",
    "body_surface_area": 1.85,
    "bsa_unit": "m²"
  }
}
```

### Field Description
- `basic_info`: Basic information object
  - `gender`: Gender (M=Male, F=Female, other values optional)
  - `height`: Height value
  - `height_unit`: Height unit
  - `weight`: Weight value
  - `weight_unit`: Weight unit
  - `birth_date`: Birth date (YYYY-MM-DD format)
- `calculated`: Auto-calculated information object
  - `age`: Age (in years)
  - `bmi`: BMI index
  - `bmi_status`: BMI status (Underweight/Normal/Overweight/Obese)
  - `body_surface_area`: Body surface area (calculated using Mosteller formula)
  - `bsa_unit`: Body surface area unit

## Global Index Data Structure

```json
{
  "biochemical_exams": [
    {
      "id": "20251231123456789",
      "date": "2025-12-31",
      "type": "生化检查",
      "file_path": "data/生化检查/2025-12/2025-12-31_血常规.json"
    }
  ],
  "imaging_exams": [
    {
      "id": "20251231123456789",
      "date": "2025-12-31",
      "type": "影像检查",
      "subtype": "Ultrasound",
      "file_path": "data/影像检查/2025-12/2025-12-31_腹部B超.json"
    }
  ],
  "last_updated": "2025-12-31T12:34:56.789Z"
}
```

### Field Description
- `biochemical_exams`: Biochemical examination index array
- `imaging_exams`: Imaging examination index array
- `symptom_records`: Symptom record index array
- `last_updated`: Last update time (ISO 8601 format)

## Symptom Record Data Structure

```json
{
  "id": "20251231123456789",
  "record_date": "2025-12-31",
  "symptom_date": "2025-12-31",
  "original_input": "User's original input",

  "standardized": {
    "main_symptom": "Headache",
    "category": "Nervous System",
    "body_part": "Head",
    "severity": "Mild",
    "severity_level": 1,
    "characteristics": "Distending pain sensation",
    "onset_time": "2025-12-31T10:00:00",
    "duration": "2 hours",
    "frequency": "First occurrence"
  },

  "associated_symptoms": [
    {
      "name": "Nausea",
      "present": true
    },
    {
      "name": "Vomiting",
      "present": false
    }
  ],

  "triggers": {
    "possible_causes": ["Lack of sleep", "Mental stress"],
    "aggravating_factors": [],
    "relieving_factors": ["Slightly relieved after rest"]
  },

  "medical_assessment": {
    "urgency": "observation",
    "urgency_level": 1,
    "recommendation": "Home observation",
    "advice": "Recommend adequate rest and ensure sufficient sleep. If symptoms worsen or persist for more than 24 hours, seek medical attention.",
    "red_flags": []
  },

  "follow_up": {
    "needs_follow_up": false,
    "follow_up_date": null,
    "improvement": null
  },

  "metadata": {
    "created_at": "2025-12-31T12:34:56.789Z",
    "last_updated": "2025-12-31T12:34:56.789Z"
  }
}
```

### Field Description
- `id`: Unique identifier (generated from timestamp)
- `record_date`: Record creation date (YYYY-MM-DD format)
- `symptom_date`: Symptom occurrence date (YYYY-MM-DD format)
- `original_input`: User's original natural language description
- `standardized`: Standardized medical information object
  - `main_symptom`: Standard medical term for main symptom
  - `category`: System classification of symptom
  - `body_part`: Body part where symptom occurs
  - `severity`: Severity description (Mild/Moderate/Severe/Critical)
  - `severity_level`: Severity level (1-4)
  - `characteristics`: Symptom characteristic description
  - `onset_time`: Symptom onset time (ISO 8601 format)
  - `duration`: Duration description
  - `frequency`: Occurrence frequency description
- `associated_symptoms`: Associated symptoms array
  - `name`: Symptom name
  - `present`: Whether symptom is present (boolean)
- `triggers`: Triggers and relieving factors object
  - `possible_causes`: Possible causes array
  - `aggravating_factors`: Aggravating factors array
  - `relieving_factors`: Relieving factors array
- `medical_assessment`: Medical assessment object
  - `urgency`: Urgency category (observation/outpatient/urgent/emergency)
  - `urgency_level`: Urgency level (1-4)
  - `recommendation`: Medical recommendation category
  - `advice`: Specific advice content
  - `red_flags`: Red flag warning signals array
- `follow_up`: Follow-up information object
  - `needs_follow_up`: Whether follow-up is needed (boolean)
  - `follow_up_date`: Follow-up date (if applicable)
  - `improvement`: Improvement status (if applicable)
- `metadata`: Metadata object
  - `created_at`: Record creation time (ISO 8601 format)
  - `last_updated`: Last update time (ISO 8601 format)

### Urgency Classification

- **observation (Level 1)**: Home observation
- **outpatient (Level 2)**: Outpatient visit (within 1 week)
- **urgent (Level 3)**: Seek medical attention soon (today or tomorrow)
- **emergency (Level 4)**: Immediate medical attention or call emergency services

### Symptom System Classification

- Respiratory System: Cough, sputum, dyspnea, chest pain, etc.
- Cardiovascular System: Palpitations, chest tightness, edema, etc.
- Digestive System: Abdominal pain, nausea, vomiting, diarrhea, constipation, etc.
- Nervous System: Headache, dizziness, insomnia, seizures, etc.
- Urinary System: Urinary frequency, urgency, dysuria, hematuria, etc.
- Endocrine System: Polydipsia, polyuria, weight changes, etc.
- Musculoskeletal: Joint pain, muscle pain, limited mobility, etc.
- General Symptoms: Fever, fatigue, weight loss, etc.

## Medication Record Data Structure

### Medication Information Data Structure

```json
{
  "medications": [
    {
      "id": "med_20251231123456789",
      "name": "Aspirin",
      "generic_name": "Aspirin",
      "dosage": {
        "value": 100,
        "unit": "mg"
      },
      "frequency": {
        "type": "daily",
        "times_per_day": 1,
        "interval_days": 1
      },
      "schedule": [
        {
          "weekday": 1,
          "time": "08:00",
          "timing_label": "After breakfast",
          "dose": {
            "value": 100,
            "unit": "mg"
          }
        },
        {
          "weekday": 2,
          "time": "08:00",
          "timing_label": "After breakfast",
          "dose": {
            "value": 100,
            "unit": "mg"
          }
        }
        ... (continuing through Sunday, total 7 records)
      ],
      "instructions": "Take after breakfast",
      "notes": "",
      "active": true,
      "created_at": "2025-12-31T12:34:56.789Z",
      "last_updated": "2025-12-31T12:34:56.789Z"
    }
  ]
}
```

### Field Description

- `medications`: Medications array
  - `id`: Unique identifier (prefix med_ + timestamp)
  - `name`: Medication name (generic or brand name)
  - `generic_name`: Generic name
  - `dosage`: Dosage information object
    - `value`: Dosage value
    - `unit`: Dosage unit (mg, g, ml, IU, tablet, capsule, etc.)
  - `frequency`: Medication frequency object
    - `type`: Frequency type (daily/weekly/every_other_day/as_needed)
    - `times_per_day`: Number of times per day
    - `interval_days`: Medication interval in days
  - `schedule`: Medication schedule array (mandatory explicit specification for each day of week)
    - `weekday`: Day of week (1-7, 1=Monday, 7=Sunday)
    - `time`: Medication time (HH:mm format)
    - `timing_label`: Time label (after breakfast, before bed, etc.)
    - `dose`: Dose at this time
  - `instructions`: Medication instructions
  - `notes`: Note information
  - `active`: Whether active (true=currently taking, false=discontinued)
  - `created_at`: Creation time (ISO 8601 format)
  - `last_updated`: Last update time (ISO 8601 format)

### Schedule Array Generation Rules

**Important: schedule must explicitly generate medication plan records for each day of the week**

#### Once Daily Medications
Generate 7 records (1 for each day Monday through Sunday)
```json
"schedule": [
  {"weekday": 1, "time": "08:00", ...},
  {"weekday": 2, "time": "08:00", ...},
  {"weekday": 3, "time": "08:00", ...},
  {"weekday": 4, "time": "08:00", ...},
  {"weekday": 5, "time": "08:00", ...},
  {"weekday": 6, "time": "08:00", ...},
  {"weekday": 7, "time": "08:00", ...}
]
```

#### Twice Daily Medications
Generate 14 records (2 times per day × 7 days)
```json
"schedule": [
  {"weekday": 1, "time": "08:00", ...},  // Monday morning
  {"weekday": 1, "time": "20:00", ...},  // Monday evening
  {"weekday": 2, "time": "08:00", ...},  // Tuesday morning
  {"weekday": 2, "time": "20:00", ...},  // Tuesday evening
  ... (continuing through Sunday)
]
```

#### Three Times Daily Medications
Generate 21 records (3 times per day × 7 days)
```json
"schedule": [
  {"weekday": 1, "time": "08:00", ...},  // Monday after breakfast
  {"weekday": 1, "time": "12:30", ...},  // Monday after lunch
  {"weekday": 1, "time": "18:30", ...},  // Monday after dinner
  {"weekday": 2, "time": "08:00", ...},  // Tuesday after breakfast
  ... (continuing through Sunday)
]
```

#### Once Weekly Medications
Generate 1 record (specified day of week)
```json
"schedule": [
  {"weekday": 1, "time": "08:00", ...}  // Every Monday
]
```

#### Every Other Day Medications
Generate 4 records (Monday, Wednesday, Friday, Sunday OR Tuesday, Thursday, Saturday)
```json
"schedule": [
  {"weekday": 1, "time": "08:00", ...},
  {"weekday": 3, "time": "08:00", ...},
  {"weekday": 5, "time": "08:00", ...},
  {"weekday": 7, "time": "08:00", ...}
]
```

### Medication Log Data Structure

```json
{
  "date": "2025-12-31",
  "logs": [
    {
      "id": "log_20251231080000001",
      "medication_id": "med_20251231123456789",
      "medication_name": "Aspirin",
      "scheduled_time": "08:00",
      "actual_time": "2025-12-31T08:15:00",
      "status": "taken",
      "dose": {
        "value": 100,
        "unit": "mg"
      },
      "notes": "",
      "created_at": "2025-12-31T08:15:00.000Z"
    }
  ]
}
```

### Field Description

- `date`: Medication date (YYYY-MM-DD format)
- `logs`: Medication log array
  - `id`: Log unique identifier (prefix log_ + timestamp)
  - `medication_id`: Associated medication ID
  - `medication_name`: Medication name
  - `scheduled_time`: Scheduled medication time (HH:mm format)
  - `actual_time`: Actual medication time (ISO 8601 format, null if missed)
  - `status`: Medication status (taken/missed/skipped/delayed)
  - `dose`: Actual dose
  - `notes`: Notes (e.g., reason for missed dose)
  - `created_at`: Log creation time (ISO 8601 format)

### Medication Status Values

- **taken**: Taken (on time or delayed)
- **missed**: Missed (not taken)
- **skipped**: Skipped (medically discontinued or paused)
- **delayed**: Delayed (taken but time was delayed)

### Frequency Type Values

- **daily**: Daily (times_per_day indicates number of times per day)
- **weekly**: Weekly (times_per_day indicates number of times per week)
- **every_other_day**: Every other day
- **as_needed**: As needed (compliance not calculated)

### Medication Adherence Calculation

```
Adherence Percentage = (Actual doses taken / Scheduled doses) × 100%

Where:
- Actual doses taken = Number of records with status taken or delayed
- Scheduled doses = Total scheduled doses (excluding skipped and as_needed)
- Pending doses not included in statistics
```

### Adherence Levels

- **Excellent**: ≥ 90%
- **Good**: 70% - 89%
- **Needs Improvement**: < 70%

## Global Index Update (Medication Records)

```json
{
  "medications": [
    {
      "id": "med_20251231123456789",
      "name": "Aspirin",
      "dosage_value": 100,
      "dosage_unit": "mg",
      "frequency_type": "daily",
      "file_path": "data/medications/medications.json",
      "active": true,
      "created_at": "2025-12-31T12:34:56.789Z"
    }
  ],
  "medication_logs": [
    {
      "id": "log_20251231080000001",
      "date": "2025-12-31",
      "medication_id": "med_20251231123456789",
      "medication_name": "Aspirin",
      "status": "taken",
      "file_path": "data/medication-logs/2025-12/2025-12-31.json"
    }
  ]
}
```

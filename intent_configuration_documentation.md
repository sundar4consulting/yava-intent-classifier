# Intent Configuration Documentation

This document provides a comprehensive guide to managing intents in the YAVA Intent Classifier system. The configuration is stored in the `/config` directory and supports dynamic updates via Excel uploads and API endpoints.

## Configuration Overview

The intent classifier uses a JSON-based configuration system that can be updated without redeploying the agent. Key components:

- **`intents_config.json`**: Main configuration file containing all intent definitions
- **`config_loader.py`**: Handles loading and reloading configuration
- **`excel_parser.py`**: Parses Excel files into JSON format
- **`admin_api.py`**: Provides REST endpoints for configuration management

## Excel Template: `intent_business_capture_requirement_template.html`

The Excel template (`intent_business_capture_requirement_template.html`) is a structured form for capturing business requirements for new intents. It ensures all necessary information is collected before adding intents to the system.

### Template Structure

The template includes the following sections:

1. **Intent Metadata**
   - Intent ID (unique identifier)
   - Intent Name (human-readable name)
   - Category (healthcare, benefits, claims, etc.)
   - Agent Routing (target agent name)
   - Priority (1-5, higher = more important)

2. **Business Requirements**
   - Description (short summary)
   - Use Cases (when this intent should trigger)
   - Expected Outcomes (what the agent should do)

3. **Training Data**
   - Training Utterances (sample user messages)
   - Keywords (important terms)
   - Disambiguation Prompt (clarification questions)

4. **Validation Rules**
   - Confidence Thresholds
   - Fallback Behavior

## Steps to Add Intents

### Method 1: Excel Upload (Recommended for Bulk Updates)

1. **Prepare Excel File**
   - Download and fill out `intent_business_capture_requirement_template.html`
   - Ensure all required columns are populated
   - Save as `.xlsx` format

2. **Upload via Admin API**
   ```bash
   curl -X POST "http://localhost:8000/admin/upload-excel" \
        -H "Content-Type: multipart/form-data" \
        -F "file=@your_intent_config.xlsx"
   ```

3. **Reload Configuration**
   ```bash
   curl -X POST "http://localhost:8000/admin/reload-config"
   ```

4. **Validate Configuration**
   ```bash
   curl "http://localhost:8000/admin/validate-config"
   ```

### Method 2: Direct API Addition (For Single Intents)

```bash
curl -X POST "http://localhost:8000/admin/add-intent" \
     -H "Content-Type: application/json" \
     -d '{
       "intent_id": "INT-PHR-0001",
       "intent_name": "pharmacy",
       "category": "healthcare",
       "agent_routing": "PharmacyAgent",
       "priority": 4,
       "description_short": "Handle pharmacy-related inquiries",
       "disambiguation_prompt": "Are you asking about prescription refills, pharmacy locations, or medication costs?",
       "training_utterances": [
         "I need to refill my prescription",
         "Where is the nearest pharmacy?",
         "How much does my medication cost?"
       ],
       "keywords": ["prescription", "pharmacy", "medication", "refill"]
     }'
```

## Adding Disambiguation

Disambiguation helps when the classifier has low confidence in an intent. It provides clarification questions to better understand user intent.

### Steps to Add Disambiguation

1. **Identify Ambiguous Scenarios**
   - Review similar intents that might overlap
   - Test with sample utterances that could match multiple intents

2. **Create Disambiguation Prompt**
   - Write clear, specific questions
   - Include options when possible
   - Keep it conversational

3. **Add to Configuration**
   - Include in Excel template under "Disambiguation Prompt" column
   - Or add via API as shown above

### Example Disambiguation Prompts

| Intent | Disambiguation Prompt |
|--------|----------------------|
| pharmacy | "Are you asking about: 1) Refilling prescriptions, 2) Finding pharmacy locations, or 3) Medication costs?" |
| claims | "Do you want to: 1) Check claim status, 2) File a new claim, or 3) Appeal a denied claim?" |
| benefits | "Are you inquiring about: 1) Coverage details, 2) Benefit summaries, or 3) Enrollment information?" |

## Excel Columns Reference

### Required Columns

| Column Name | Type | Description | Example |
|-------------|------|-------------|---------|
| `intent_id` | String | Unique identifier (format: INT-CAT-XXXX) | INT-PHR-0001 |
| `intent_name` | String | Human-readable name | pharmacy |
| `category` | String | Intent category | healthcare |
| `agent_routing` | String | Target agent name | PharmacyAgent |
| `description_short` | String | Brief description | Handle pharmacy inquiries |
| `training_utterances` | List | Sample user messages (comma-separated) | "I need a refill","Where's the pharmacy?" |

### Optional Columns

| Column Name | Type | Description | Example |
|-------------|------|-------------|---------|
| `priority` | Integer | Importance level (1-5) | 4 |
| `disambiguation_prompt` | String | Clarification question | "Are you asking about refills or locations?" |
| `keywords` | List | Important terms (comma-separated) | prescription,medication,refill |
| `use_cases` | String | When intent should trigger | When user mentions prescriptions or pharmacies |
| `expected_outcomes` | String | What agent should do | Route to pharmacy specialist |

## Complete Example: Adding a New Intent

### 1. Excel Template Entry

| intent_id | intent_name | category | agent_routing | priority | description_short | disambiguation_prompt | training_utterances | keywords |
|-----------|-------------|----------|---------------|----------|-------------------|----------------------|---------------------|----------|
| INT-WEL-0047 | gymFitness | wellness | WellnessAgent | 3 | Handle gym and fitness inquiries | "Are you asking about gym memberships, fitness classes, or personal training?" | "How do I join the gym?","What fitness classes are available?","I want personal training" | gym,fitness,classes,membership |

### 2. API Validation

After upload, check validation:
```json
{
  "valid": true,
  "errors": [],
  "warnings": ["INT-WEL-0047: Less than 5 training utterances (recommended: 10+)"]
}
```

### 3. Test Classification

```bash
curl "http://localhost:8000/classify?text=I%20want%20to%20join%20the%20gym"
```

Expected response:
```json
{
  "intent": "gymFitness",
  "agent": "WellnessAgent", 
  "confidence": 0.89,
  "needs_clarification": false
}
```

## Best Practices

1. **Intent IDs**: Use consistent naming (INT-CAT-XXXX)
2. **Training Utterances**: Provide 10+ diverse examples
3. **Keywords**: Include synonyms and variations
4. **Disambiguation**: Add for intents with potential overlap
5. **Validation**: Always run validation after changes
6. **Testing**: Test new intents with various phrasings

## Troubleshooting

- **Upload Fails**: Check Excel format and required columns
- **Validation Errors**: Review error messages and fix missing fields
- **Classification Issues**: Add more training utterances or adjust disambiguation
- **Reload Problems**: Check file permissions and JSON syntax

This system allows for flexible, business-driven intent management with minimal technical overhead.
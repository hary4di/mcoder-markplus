# Kobo Survey Classification Automation - AI Coding Guide

## Project Overview
Survey automation system for MarkPlus Indonesia that classifies open-ended survey responses from Kobo Toolbox using OpenAI GPT-4o-mini, then optionally pushes coded results back to Kobo.

**Core Flow**: Kobo API → AI Classification → Excel Export → (Optional) Kobo Update

## Architecture

### Three-Module Design
1. **[kobo_client.py](kobo_client.py)**: Kobo Toolbox API client - fetches submissions and asset metadata
2. **[openai_classifier.py](openai_classifier.py)**: Two-phase AI classification with validation filtering
3. **[kobo_uploader.py](kobo_uploader.py)**: Reverse API - creates form fields and uploads numeric codes

### Two Entry Points
- **[main.py](main.py)**: Full automation pipeline (Kobo → Classification → Optional upload)
- **[excel_classifier.py](excel_classifier.py)**: Excel-based workflow with hybrid outlier re-analysis

### Data Flow Pattern
```
Kobo API → Filter invalid responses → Phase 1: Generate categories (sample) 
→ Phase 2: Classify all responses → Excel output → (Optional) Upload codes to Kobo
```

## Critical Conventions

### Response Validation Logic
Invalid responses are **filtered before category generation** but **retained for final output** with code 99:
- Invalid patterns defined in `OpenAIClassifier.invalid_responses` list (e.g., "TA", "tidak ada", "N/A")
- Check: `is_valid_response()` before category generation
- Final output: Invalid → code 99, Empty → null (matching Kobo logic)

### Two-Phase Classification
**Phase 1** (`generate_categories`): AI analyzes sample (default 80% with max 500) to create up to 10 categories
**Phase 2** (`classify_response`): Each response classified into generated categories with confidence score

Sampling strategy controlled by `.env`:
- `CATEGORY_SAMPLE_RATIO`: Percentage of responses to sample (default 0.8)
- `ENABLE_STRATIFIED_SAMPLING`: Stratify by response length (short/medium/long)
- `MAX_SAMPLE_SIZE`: Hard cap on sample size (default 500)

### Column Insertion Pattern
Classification results always inserted **immediately after source column**:
```python
e1_index = df.columns.get_loc(e1_field_name)
cols.insert(e1_index + 1, 'E1_category')
cols.insert(e1_index + 2, 'E1_confidence')
```

## Configuration (.env)

### Required Keys
- `KOBO_ASSET_ID`, `KOBO_API_TOKEN`: Kobo API access
- `OPENAI_API_KEY`: Must not be placeholder `your_openai_api_key_here`

### Operation Modes
- `AUTO_UPLOAD_TO_KOBO=true`: Activates Step 10 in [main.py](main.py#L296-L358) - creates Kobo field + uploads codes
- `AUTO_UPLOAD_TO_KOBO=false`: Classification-only mode (Excel export only)

### Field Naming Convention
Source field: `Group_E/E1` (Kobo group/question format)
Coded field: `Group_E/E1_coded` (suffix from `CODED_FIELD_SUFFIX`)

## Kobo API Patterns

### Asset Update (kobo_uploader.py)
Modifying Kobo form structure requires:
1. GET current asset content
2. Add choice list to `choices` array with `list_name`
3. Add field to `survey` array with `type: select_one`, referencing list
4. PATCH entire content back (full replacement)

Example in [kobo_uploader.py](kobo_uploader.py#L68-L165)

### Submission Update (Batch Pattern)
Upload uses **bulk PATCH** with payload arrays:
```python
{
    "submission_ids": [123, 456],
    "data": {"Group_E/E1_coded": 1}  # Same value for all in batch
}
```
Batched by category code for efficiency (see [kobo_uploader.py](kobo_uploader.py#L226-L283))

## AI Classification Details

### Model Configuration
- Model: `gpt-4o-mini` (most economical, ~$0.15/1M tokens)
- Temperature: 0.1 for consistency
- JSON mode enforced with response format

### Prompt Engineering
Both phases use **Indonesian language** prompts with:
- Numbered response lists for clarity
- JSON schema specification
- Question context when available (parameter `question_text`)

Category generation prompt emphasizes: "Kategori harus spesifik, tidak generik" to avoid over-generalization

## Testing & Debugging

### Test Scripts
- `explore_kobo.py`: Inspect Kobo asset structure and sample data
- `test_connection.py`: Validate Kobo API credentials
- Run these BEFORE main pipeline when troubleshooting field not found errors

### Log Files Structure
All outputs in `files/`:
- `logs/classification_YYYYMMDD_HHMMSS.log`: Full execution log with progress
- `logs/generated_categories.json`: Categories from Phase 1 (for review)
- `logs/sample_e1_responses.txt`: Sample valid/invalid responses
- `output/classified_responses_*.xlsx`: Final Excel with classifications

### Common Issues
**"Field 'Group_E/E1' not found"**: Field name varies by survey. Use `explore_kobo.py` to discover actual field name, then update `e1_field_name` in [main.py](main.py#L67)

**OpenAI rate limit**: Retry logic built-in. For persistent errors, check quota at platform.openai.com/usage

## Windows-Specific
- Batch files: [run.bat](run.bat) and [test_kobo.bat](test_kobo.bat) use `py` launcher
- UTF-8 encoding explicitly set in [excel_classifier.py](excel_classifier.py#L11-L14) for console output
- File paths use `os.path.join()` for cross-platform compatibility

## When Modifying

### Adding New Question Fields
1. Update field name (e.g., `E1` → `E2`) in main pipeline
2. Ensure field path includes group: `Group_E/E2`
3. Adjust coded field suffix: `E2_coded`
4. Categories generate fresh per field - no reuse

### Changing Category Limits
Modify `MAX_CATEGORIES` in `.env` (default 10). Note: `excel_classifier.py` passes `max_categories=None` for unlimited categories with outlier re-analysis.

### Excel vs Full Pipeline
**Use excel_classifier.py when**: Source data is Excel (not Kobo), need outlier re-analysis
**Use main.py when**: Live Kobo integration, need automated field creation and code upload

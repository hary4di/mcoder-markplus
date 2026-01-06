# Kobo Survey Classification Automation - AI Coding Guide

## Project Overview
**M-Code Pro** - MarkPlus AI-Powered Classification System

Web-based survey automation platform for MarkPlus Indonesia that classifies open-ended survey responses using OpenAI GPT-4o-mini. Supports both pure open-ended and semi open-ended questions with Kobo Toolbox integration.

**Production URL**: https://m-coder.flazinsight.com
**Stack**: Flask 3.0 + Python 3.11 + SQLite + Bootstrap 5 + OpenAI API

**Core Flow**: Excel Upload → AI Classification → Results Display → Download Excel

## Architecture

### Web Application Structure
1. **[app/](app/)**: Flask application
   - `routes.py`: Main routes, classification orchestration, progress tracking
   - `auth.py`: Login, registration, password management
   - `models.py`: User model with SQLAlchemy
   - `forms.py`: WTForms for validation
   - `templates/`: Jinja2 HTML templates
   - `static/`: CSS, JS, images

### Classification Engine
1. **[excel_classifier.py](excel_classifier.py)**: Main classification workflow with Excel I/O
2. **[openai_classifier.py](openai_classifier.py)**: Two-phase AI classification with validation filtering
3. **[parallel_classifier.py](parallel_classifier.py)**: Multi-variable parallel processing
4. **[semi_open_processor.py](semi_open_processor.py)**: Semi open-ended question handler

### Legacy/Optional Modules
- **[kobo_client.py](kobo_client.py)**: Kobo Toolbox API client (optional, for direct Kobo integration)
- **[kobo_uploader.py](kobo_uploader.py)**: Upload coded results back to Kobo (optional)
- **[main.py](main.py)**: Standalone CLI pipeline (legacy, not used in web app)

### Data Flow Pattern
```
User Upload Excel → Parse Variables → AI Classification (background thread)
→ Progress Tracking → Results Page → Download Classified Excel
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
- `OPENAI_API_KEY`: OpenAI API key for GPT-4o-mini
- `SECRET_KEY`: Flask session encryption key
- `DATABASE_URL`: SQLite database path (default: instance/mcoder.db)

### Optional Keys (Kobo Integration)
- `KOBO_ASSET_ID`, `KOBO_API_TOKEN`: For direct Kobo API access (rarely used)
- `AUTO_UPLOAD_TO_KOBO`: Enable Kobo upload feature (default: false)

### Classification Settings
- `MAX_CATEGORIES`: Default max categories (default: 10, can be None for unlimited)
- `CONFIDENCE_THRESHOLD`: Minimum confidence score (default: 0.5)
- `CATEGORY_SAMPLE_RATIO`: Sampling percentage for category generation (default: 0.8)
- `MAX_SAMPLE_SIZE`: Hard cap on sample size (default: 500)

### Branding (Current as of 2025-12-27)
- Application Name: **M-Code Pro**
- Subtitle: **MarkPlus AI-Powered Classification System**
- Logo: MarkPlus corporate logo with bold "M" styling

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

### Log Files Structure
All outputs in `files/`:
- `uploads/`: User-uploaded Excel files and classification results
- `logs/`: Classification logs and debugging info (if logging enabled)
- `logo/`: Application logo and branding assets

### Common Issues
**Results Page Error**: Session data may be cleared after app restart. Re-run classification to see results.

**File Upload Issues**: Ensure Excel files have proper column headers matching Kobo field names.

**OpenAI Rate Limit**: Retry logic built-in. Check quota at platform.openai.com/usage

### Error Handling (Added 2025-12-27)
- Results page has try-catch to handle corrupted session data
- Automatic session cleanup on error with user-friendly redirect
- Flash messages explain errors instead of showing 500 pages

## Windows-Specific
- PowerShell scripts: `quick-deploy.ps1` for deployment to VPS
- Cleanup script: `cleanup_unused_files.ps1` (already executed - 48 files removed)
- UTF-8 encoding explicitly set in classifiers for console output
- File paths use `os.path.join()` for cross-platform compatibility

## Production Deployment
- **Server**: Hostinger VPS Ubuntu 24.04
- **IP**: 145.79.10.104
- **Domain**: https://m-coder.flazinsight.com
- **Process Manager**: Supervisor (mcoder-markplus service)
- **Web Server**: Nginx reverse proxy
- **Python**: 3.11 with venv
- **Deployment**: Manual SCP upload + supervisorctl restart (no git on VPS)

## Recent Changes (2025-12-27)
See [CHANGELOG.md](../CHANGELOG.md) for detailed change history including:
- Branding update to "M-Code Pro"
- UI/UX improvements (2-line user display, spacing fixes)
- Cleanup of 48 unused files
- Documentation rewrite (PROJECT_OVERVIEW.md reduced from 2245 to 350 lines)
- Error handling improvements

## When Modifying

### Adding New Features
1. Check [PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md) for current priorities (🔴🟡🟢)
2. Review [CHANGELOG.md](../CHANGELOG.md) for recent changes
3. Test locally before deploying to VPS
4. Update documentation after completing feature

### Changing Category Limits
Modify `MAX_CATEGORIES` in `.env` (default 10). Note: `excel_classifier.py` passes `max_categories=None` for unlimited categories with outlier re-analysis.

### Excel vs Full Pipeline
**Use excel_classifier.py when**: Source data is Excel (not Kobo), need outlier re-analysis
**Use main.py when**: Live Kobo integration, need automated field creation and code upload (rarely used)

### Deployment Workflow
1. Test changes locally
2. Upload files: `scp file.py root@145.79.10.104:/opt/markplus/mcoder-markplus/`
3. Restart service: `ssh root@145.79.10.104 "supervisorctl restart mcoder-markplus"`
4. Verify: Check https://m-coder.flazinsight.com

## Key Documentation
- **[PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md)**: Master reference (350 lines, concise)
- **[CHANGELOG.md](../CHANGELOG.md)**: Change history with dates
- **[README.md](../README.md)**: User guide and setup instructions
- **This file**: Technical guide for AI agents

---

**Note**: Yes, copilot-instructions.md is similar to MCP (Model Context Protocol) - it provides structured context for AI agents to understand the project architecture, conventions, and current state.

"""
Main Automation Pipeline
Orchestrates the entire classification process from Kobo to Excel output
"""
import os
import sys
import json
import logging
from datetime import datetime
from typing import List, Dict
import pandas as pd
from dotenv import load_dotenv

from kobo_client import KoboClient
from openai_classifier import OpenAIClassifier
from kobo_uploader import KoboUploader

# Load environment variables
load_dotenv()

# Setup logging
def setup_logging():
    """Setup logging configuration"""
    log_dir = 'files/logs'
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'classification_{timestamp}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

logger = setup_logging()

def main():
    """Main automation pipeline"""
    
    logger.info("=" * 80)
    logger.info("KOBO SURVEY CLASSIFICATION AUTOMATION")
    logger.info("=" * 80)
    
    try:
        # Step 1: Initialize clients
        logger.info("\n[Step 1] Initializing clients...")
        kobo_client = KoboClient()
        openai_classifier = OpenAIClassifier()
        kobo_uploader = KoboUploader()
        logger.info("✓ Clients initialized successfully")
        
        # Step 2: Fetch data from Kobo
        logger.info("\n[Step 2] Fetching survey data from Kobo...")
        submissions = kobo_client.get_submissions()
        logger.info(f"✓ Retrieved {len(submissions)} submissions")
        
        if not submissions:
            logger.error("✗ No submissions found!")
            return
        
        # Step 3: Extract E1 responses
        logger.info("\n[Step 3] Extracting E1 responses...")
        e1_field_name = 'Group_E/E1'
        
        # Check if field exists in any submission (it might be optional)
        field_exists = False
        for submission in submissions:
            if e1_field_name in submission:
                field_exists = True
                break
        
        if not field_exists:
            # Get all field names from first submission to check
            if submissions:
                available_fields = list(submissions[0].keys())
                logger.info(f"Available fields: {', '.join(available_fields[:10])}...")
            
            logger.warning(f"✗ Field '{e1_field_name}' not found in submissions!")
            logger.info(f"Looking for E1-related fields...")
            
            # Search for any E1 field
            e1_fields = [f for f in submissions[0].keys() if 'E1' in f or 'e1' in f.lower()]
            if e1_fields:
                logger.info(f"Found E1-related fields: {e1_fields}")
            else:
                logger.error("No E1 field found in data!")
                logger.info("Available fields (full list):")
                for field in available_fields:
                    if 'Group_E' in field or 'Group_F' in field:
                        logger.info(f"  - {field}")
            return
        
        # Extract E1 responses (non-empty only)
        e1_responses = []
        for submission in submissions:
            e1_value = submission.get(e1_field_name)
            if e1_value and str(e1_value).strip():
                e1_responses.append(str(e1_value).strip())
        
        logger.info(f"✓ Found {len(e1_responses)} non-empty E1 responses")
        
        # Filter valid responses
        valid_responses = openai_classifier.filter_valid_responses(e1_responses)
        invalid_count = len(e1_responses) - len(valid_responses)
        logger.info(f"✓ Valid responses: {len(valid_responses)} (excluded {invalid_count} invalid responses like 'TA', 'tidak ada', etc.)")
        
        if not valid_responses:
            logger.error("✗ No valid E1 responses to classify!")
            return
        
        # Save sample responses for review (valid only)
        sample_file = 'files/logs/sample_e1_responses.txt'
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(f"Total responses: {len(e1_responses)}\n")
            f.write(f"Valid responses: {len(valid_responses)}\n")
            f.write(f"Invalid responses excluded: {invalid_count}\n")
            f.write("\n--- VALID RESPONSES (Sample 20) ---\n\n")
            for idx, resp in enumerate(valid_responses[:20], 1):
                f.write(f"{idx}. {resp}\n")
            if invalid_count > 0:
                f.write("\n--- INVALID RESPONSES (Sample 10) ---\n\n")
                invalid_samples = [r for r in e1_responses if not openai_classifier.is_valid_response(r)]
                for idx, resp in enumerate(invalid_samples[:10], 1):
                    f.write(f"{idx}. {resp}\n")
        logger.info(f"✓ Sample responses saved to {sample_file}")
        
        # Step 4: Generate categories (using valid responses only)
        logger.info("\n[Step 4] Generating categories using OpenAI...")
        logger.info(f"Using 80% random sample from {len(valid_responses)} valid responses")
        categories = openai_classifier.generate_categories(valid_responses)
        logger.info(f"✓ Generated {len(categories)} categories:")
        for cat in categories:
            logger.info(f"   - {cat}")
        
        # Save categories
        categories_file = 'files/logs/generated_categories.json'
        with open(categories_file, 'w', encoding='utf-8') as f:
            json.dump({"categories": categories, "count": len(categories)}, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Categories saved to {categories_file}")
        
        # Step 5: Classify all responses (including invalid ones, they will get "Invalid Response" category)
        logger.info(f"\n[Step 5] Classifying all {len(e1_responses)} responses...")
        logger.info("This may take a few minutes depending on the number of responses...")
        
        classified_results = []
        for idx, response in enumerate(e1_responses, 1):
            # Check if response is valid
            if openai_classifier.is_valid_response(response):
                category, confidence = openai_classifier.classify_response(response, categories)
            else:
                # Invalid responses get special category
                category = "Invalid Response"
                confidence = 1.0
            
            json.dump({"categories": categories, "count": len(categories)}, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Categories saved to {categories_file}")
        
        # Step 5: Classify all responses
        logger.info(f"\n[Step 5] Classifying {len(e1_responses)} responses...")
        logger.info("This may take a few minutes depending on the number of responses...")
        
        classified_results = []
        for idx, response in enumerate(e1_responses, 1):
            category, confidence = openai_classifier.classify_response(response, categories)
            classified_results.append({
                'response': response,
                'category': category,
                'confidence': confidence
            })
            
            # Progress indicator
            if idx % 10 == 0:
                logger.info(f"   Progress: {idx}/{len(e1_responses)} responses classified")
        
        logger.info(f"✓ All {len(classified_results)} responses classified")
        
        # Step 6: Merge with original submissions data
        logger.info("\n[Step 6] Merging classification results with original data...")
        
        # Create a mapping of E1 responses to classifications
        classification_map = {}
        for result in classified_results:
            classification_map[result['response']] = {
                'E1_category': result['category'],
                'E1_confidence': result['confidence']
            }
        
        # Add classification columns to submissions
        for submission in submissions:
            e1_value = submission.get(e1_field_name, '')
            if e1_value and str(e1_value).strip() in classification_map:
                classification = classification_map[str(e1_value).strip()]
                submission['E1_category'] = classification['E1_category']
                submission['E1_confidence'] = classification['E1_confidence']
            else:
                submission['E1_category'] = ''
                submission['E1_confidence'] = None  # Use None instead of '' for numeric column
        
        logger.info("✓ Classification results merged")
        
        # Step 7: Create DataFrame and reorder columns
        logger.info("\n[Step 7] Creating Excel output...")
        df = pd.DataFrame(submissions)
        
        # Find E1 column position and insert classification columns next to it
        if e1_field_name in df.columns:
            e1_index = df.columns.get_loc(e1_field_name)
            
            # Reorder columns to put classification columns right after E1
            cols = df.columns.tolist()
            
            # Remove classification columns from their current position
            cols.remove('E1_category')
            cols.remove('E1_confidence')
            
            # Insert them right after E1
            cols.insert(e1_index + 1, 'E1_category')
            cols.insert(e1_index + 2, 'E1_confidence')
            
            df = df[cols]
        
        # Step 8: Save to Excel
        output_dir = 'files/output'
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f'classified_responses_{timestamp}.xlsx')
        
        df.to_excel(output_file, index=False, engine='openpyxl')
        logger.info(f"✓ Excel file saved to: {output_file}")
        
        # Step 9: Generate summary statistics
        logger.info("\n[Step 9] Generating summary statistics...")
        
        category_counts = df['E1_category'].value_counts()
        
        # Calculate average confidence (exclude Invalid Response category and null values)
        valid_confidences = df[(df['E1_category'] != 'Invalid Response') & (df['E1_confidence'].notna())]['E1_confidence']
        avg_confidence = valid_confidences.mean() if len(valid_confidences) > 0 else 0
        
        logger.info(f"\nCategory Distribution:")
        for category, count in category_counts.items():
            if category:  # Skip empty categories
                percentage = (count / len(e1_responses)) * 100
                logger.info(f"   {category}: {count} ({percentage:.1f}%)")
        
        logger.info(f"\nStatistics:")
        logger.info(f"   Total Responses: {len(e1_responses)}")
        logger.info(f"   Valid Responses: {len(valid_responses)}")
        logger.info(f"   Invalid Responses: {invalid_count}")
        logger.info(f"   Average Confidence Score (valid only): {avg_confidence:.2f}")
        
        # Save summary
        summary_file = os.path.join(output_dir, f'classification_summary_{timestamp}.json')
        summary = {
            'timestamp': timestamp,
            'total_submissions': len(submissions),
            'total_e1_responses': len(e1_responses),
            'valid_responses': len(valid_responses),
            'invalid_responses': invalid_count,
            'sample_ratio_for_categories': openai_classifier.sample_ratio if hasattr(openai_classifier, 'sample_ratio') else 0.8,
            'categories': categories,
            'category_distribution': category_counts.to_dict(),
            'average_confidence': float(avg_confidence),
            'average_confidence_note': 'Calculated from valid responses only, excluding Invalid Response category'
        }
                percentage = (count / len(e1_responses)) * 100
                logger.info(f"   {category}: {count} ({percentage:.1f}%)")
        
        logger.info(f"\nAverage Confidence Score: {avg_confidence:.2f}")
        
        # Save summary
        summary_file = os.path.join(output_dir, f'classification_summary_{timestamp}.json')
        summary = {
            'timestamp': timestamp,
            'total_submissions': len(submissions),
            'total_e1_responses': len(e1_responses),
            'categories': categories,
            'category_distribution': category_counts.to_dict(),
            'average_confidence': float(avg_confidence)
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Summary saved to: {summary_file}")
        # Step 10: Upload to Kobo (if enabled)
        auto_upload = os.getenv('AUTO_UPLOAD_TO_KOBO', 'false').lower() == 'true'
        
        if auto_upload:
            logger.info("\n" + "=" * 80)
            logger.info("UPLOADING RESULTS TO KOBO")
            logger.info("=" * 80)
            
            # Prepare coded field name
            coded_field_suffix = os.getenv('CODED_FIELD_SUFFIX', '_coded')
            coded_field_name = f"Group_E/E1{coded_field_suffix}"
            
            # Step 10.1: Add field to Kobo asset
            logger.info(f"\n[Step 10.1] Adding field '{coded_field_name}' to Kobo form...")
            success = kobo_uploader.add_classification_field_to_asset(
                source_field=e1_field_name,
                new_field_name=coded_field_name,
                categories=categories,
                list_name="e1_categories"
            )
            
            if not success:
                logger.warning("✗ Failed to add field to Kobo. Skipping upload.")
            else:
                # Step 10.2: Prepare submission updates
                logger.info(f"\n[Step 10.2] Preparing submission updates...")
                
                # Create mapping of submission_id to category
                submission_classifications = {}
                for submission in submissions:
                    submission_id = submission.get('_id')
                    e1_category = submission.get('E1_category', '')
                    
                    # Only update if has valid category
                    if submission_id and e1_category and e1_category != 'Invalid Response':
                        submission_classifications[submission_id] = e1_category
                
                logger.info(f"   Submissions to update: {len(submission_classifications)}")
                
                # Step 10.3: Batch update submissions
                logger.info(f"\n[Step 10.3] Uploading classification codes to Kobo...")
                logger.info("   This may take 10-15 minutes for large datasets...")
                
                results = kobo_uploader.batch_update_submissions(
                    classifications=submission_classifications,
                    field_name=coded_field_name,
                    categories=categories
                )
                
                logger.info("\n" + "=" * 80)
                logger.info("KOBO UPLOAD COMPLETED")
                logger.info("=" * 80)
                logger.info(f"✓ Successfully updated: {results['success']} submissions")
                logger.info(f"✗ Failed: {results['failed']} submissions")
                logger.info(f"Field name in Kobo: {coded_field_name}")
                logger.info(f"Choices list name: e1_categories")
        else:
            logger.info("\n[Note] Auto-upload to Kobo is disabled. Set AUTO_UPLOAD_TO_KOBO=true in .env to enable.")
        
        # Final message
        logger.info("\n" + "=" * 80)
        logger.info("CLASSIFICATION COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)
        logger.info(f"Excel output: {output_file}")
        logger.info(f"Summary: {summary_file}")
        if auto_upload:
            logger.info(f"Kobo field: {coded_field_name} with codes 1-{len(categories)}")
        logger.info(f"Summary file: {summary_file}")
        
    except Exception as e:
        logger.error(f"\n✗ Error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

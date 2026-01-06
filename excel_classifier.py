"""
Excel-based Classification Processor
Proses koding otomatis untuk survey responses dengan update ke Kobo system file
Supports PARALLEL PROCESSING untuk kecepatan maksimal
"""
import pandas as pd
import os
import sys
from datetime import datetime
from openai_classifier import OpenAIClassifier
from parallel_classifier import ParallelClassifier
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load environment variables
load_dotenv()

class ExcelClassifier:
    """Excel-based classifier untuk Kobo survey data"""
    
    def __init__(self, kobo_file_path, raw_data_file_path):
        """
        Initialize classifier
        
        Args:
            kobo_file_path: Path ke file kobo_system Excel
            raw_data_file_path: Path ke file raw data Excel
        """
        self.kobo_file_path = kobo_file_path
        self.raw_data_file_path = raw_data_file_path
        self.classifier = OpenAIClassifier()
        
        # Initialize parallel processor
        # Priority: Database settings > .env > defaults
        enable_parallel = self._get_setting('enable_parallel_processing', 
                                           os.getenv('ENABLE_PARALLEL_PROCESSING', 'true')).lower() == 'true'
        max_workers = int(self._get_setting('parallel_max_workers', 
                                            os.getenv('PARALLEL_MAX_WORKERS', '5')))
        rate_limit_delay = float(self._get_setting('rate_limit_delay', 
                                                   os.getenv('RATE_LIMIT_DELAY', '0.1')))
        
        if enable_parallel:
            self.parallel_classifier = ParallelClassifier(
                self.classifier,
                max_workers=max_workers,
                rate_limit_delay=rate_limit_delay
            )
            print(f"[INIT] Parallel processing ENABLED dengan {max_workers} workers")
        else:
            self.parallel_classifier = None
            print(f"[INIT] Parallel processing DISABLED - using sequential mode")
        
        # Storage for results
        self.categories = []
        self.category_codes = {}
        self.classifications = []
        
        # Output paths (separate from input paths)
        self.output_kobo_path = None
        self.output_raw_path = None
    
    def set_output_paths(self, output_kobo_path, output_raw_path):
        """
        Set separate output paths (don't overwrite inputs)
        
        Args:
            output_kobo_path: Path for output kobo system file
            output_raw_path: Path for output raw data file
        """
        self.output_kobo_path = output_kobo_path
        self.output_raw_path = output_raw_path
    
    def _get_setting(self, key, default):
        """
        Get setting from database (SystemSettings) with fallback to default
        Priority: Database > default (.env or hardcoded)
        
        Args:
            key: Setting key name
            default: Default value if not found in database
        
        Returns:
            Setting value from database or default
        """
        try:
            # Try to import and query SystemSettings
            from app.models import SystemSettings
            from app import db, create_app
            
            # Create app context if not exists
            try:
                app = create_app()
                with app.app_context():
                    value = SystemSettings.get_setting(key, None)
                    if value is not None:
                        return value
            except:
                pass
        except ImportError:
            # SystemSettings not available (non-Flask context)
            pass
        
        # Fallback to default
        return default
        
    def process_variable(self, variable_name, question_text=None, progress_callback=None, classification_mode='incremental'):
        """
        Main process untuk mengklasifikasi satu variable dengan Hybrid Approach
        
        Args:
            variable_name: Nama variable/kolom yang akan diklasifikasi (misal: 'E1')
            question_text: Text pertanyaan untuk context-aware classification
            progress_callback: Function(message, percentage) untuk update progress
            classification_mode: 'incremental' (only empty rows) atau 'rerun' (all rows)
        
        Returns:
            dict: Summary hasil proses
        """
        # NOTE: Backup feature disabled - original files preserved with Opsi B (no overwrite)
        # import shutil
        # from datetime import datetime
        
        # backup_dir = os.path.join(os.path.dirname(self.raw_data_file_path), 'backups')
        # os.makedirs(backup_dir, exist_ok=True)
        
        # timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # raw_backup = os.path.join(backup_dir, f"{os.path.basename(self.raw_data_file_path)}.backup_{timestamp}")
        # kobo_backup = os.path.join(backup_dir, f"{os.path.basename(self.kobo_file_path)}.backup_{timestamp}")
        
        # shutil.copy2(self.raw_data_file_path, raw_backup)
        # shutil.copy2(self.kobo_file_path, kobo_backup)
        
        # print(f"✓ Backup created: {os.path.basename(raw_backup)}")
        # print(f"✓ Backup created: {os.path.basename(kobo_backup)}")
        
        print(f"\n[DEBUG] process_variable called for {variable_name}", flush=True)
        print(f"[DEBUG] progress_callback is {'SET' if progress_callback else 'NONE'}", flush=True)
        
        def update_progress(msg, pct):
            """Helper to update progress if callback exists"""
            print(f"[DEBUG] update_progress called: {msg} ({pct}%)", flush=True)
            if progress_callback:
                try:
                    progress_callback(msg, pct)
                    print(f"[DEBUG] Callback executed successfully", flush=True)
                except Exception as e:
                    print(f"[DEBUG] Callback error: {e}", flush=True)
        
        print("=" * 80, flush=True)
        print(f"EXCEL CLASSIFICATION PROCESSOR - Variable: {variable_name}", flush=True)
        print("HYBRID APPROACH: 100% Sampling + Outlier Re-analysis", flush=True)
        print("=" * 80, flush=True)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
        
        # Step 1: Load raw data
        print(f"[DEBUG] About to call update_progress for step 1", flush=True)
        update_progress(f"[1/9] Loading raw data...", 10)
        print(f"[DEBUG] About to call _load_raw_data()", flush=True)
        df_raw = self._load_raw_data()
        print(f"[DEBUG] _load_raw_data() completed, got {len(df_raw)} rows", flush=True)
        update_progress(f"   Loaded {len(df_raw)} submissions", 12)
        
        # Check if variable has been classified before
        coded_col = f"{variable_name}_coded"
        has_existing_classification = coded_col in df_raw.columns
        
        if has_existing_classification:
            # Count filled vs empty in coded column
            mask = df_raw[variable_name].notna()
            total_with_data = mask.sum()
            coded_filled = df_raw.loc[mask, coded_col].notna().sum()
            coded_empty = total_with_data - coded_filled
            
            print(f"\n{'='*80}")
            print(f"EXISTING CLASSIFICATION DETECTED")
            print(f"{'='*80}")
            print(f"  Variable: {variable_name}")
            print(f"  Total rows with data: {total_with_data}")
            print(f"  Already classified: {coded_filled}")
            print(f"  Empty/unclassified: {coded_empty}")
            print(f"  Classification mode: {classification_mode}")
            print(f"{'='*80}\n")
            
            if classification_mode == 'incremental' and coded_empty > 0:
                # INCREMENTAL MODE: Only classify empty rows
                update_progress(f"   INCREMENTAL MODE: Classifying {coded_empty} empty rows only", 14)
                print(f"[MODE] Incremental classification - processing {coded_empty} empty rows", flush=True)
                
                # We'll filter the dataframe to only process empty rows
                # But first, we need to load existing categories from the kobo system
                existing_categories = self._load_existing_categories_from_kobo(variable_name)
                
                if existing_categories:
                    print(f"[INCREMENTAL] Loaded {len(existing_categories)} existing categories from Kobo system")
                    self.categories = existing_categories
                    self.category_codes = self._create_category_codes()
                else:
                    print(f"[INCREMENTAL] No existing categories found, will generate new ones")
                    
            elif classification_mode == 'rerun':
                # RE-RUN MODE: Overwrite all
                update_progress(f"   RE-RUN MODE: Re-classifying all {total_with_data} rows", 14)
                print(f"[MODE] Re-run all - overwriting existing classifications", flush=True)
            
            elif classification_mode == 'incremental' and coded_empty == 0:
                # All rows already classified - skip
                update_progress(f"   All rows already classified - SKIPPING", 100)
                print(f"[MODE] All rows already classified - skipping variable", flush=True)
                return {
                    'variable': variable_name,
                    'status': 'skipped',
                    'reason': 'all_rows_already_classified',
                    'total_submissions': len(df_raw),
                    'classified_count': coded_filled
                }
        
        # Step 2: Extract responses
        update_progress(f"\n[2/9] Extracting {variable_name} responses...", 15)
        responses = self._extract_responses(df_raw, variable_name)
        update_progress(f"   Found {len(responses)} non-empty responses", 18)
        
        # Step 3: Filter valid responses
        update_progress(f"\n[3/9] Filtering valid responses...", 20)
        valid_responses = self.classifier.filter_valid_responses(responses)
        update_progress(f"   Valid responses: {len(valid_responses)}", 22)
        update_progress(f"   Invalid/empty responses: {len(responses) - len(valid_responses)}", 25)
        
        # Step 4: Generate categories with question context (100% sampling, max 300)
        # Skip if incremental mode with existing categories
        if has_existing_classification and classification_mode == 'incremental' and self.categories:
            update_progress(f"\n[4/9] Using existing categories...", 30)
            update_progress(f"   Loaded {len(self.categories)} existing categories", 40)
            for idx, cat in enumerate(self.categories, 1):
                print(f"      {idx}. {cat}", flush=True)
        else:
            update_progress(f"\n[4/9] Generating categories with AI...", 30)
            update_progress(f"   Analyzing {len(valid_responses)} responses with OpenAI", 32)
            self.categories = self.classifier.generate_categories(
                valid_responses,
                question_text=question_text,
                max_categories=None  # NO LIMIT
            )
            update_progress(f"   Generated {len(self.categories)} categories", 40)
            for idx, cat in enumerate(self.categories, 1):
                print(f"      {idx}. {cat}", flush=True)
        
        # Step 5: Create category codes
        update_progress(f"\n[5/9] Creating category codes...", 45)
        self.category_codes = self._create_category_codes()
        for cat, code in self.category_codes.items():
            print(f"      {code}: {cat}", flush=True)
        
        # Step 6: Classify all responses (PASS 1) with incremental support
        coded_col = f"{variable_name}_coded"
        if classification_mode == 'incremental' and has_existing_classification:
            # Count empty rows for accurate progress message
            mask = df_raw[variable_name].notna()
            coded_empty = df_raw.loc[mask, coded_col].isna().sum()
            update_progress(f"\n[6/9] Classifying {coded_empty} empty rows (incremental)...", 50)
        else:
            update_progress(f"\n[6/9] Classifying {len(df_raw)} responses with AI...", 50)
        
        self._classify_all_responses(
            df_raw, variable_name, question_text, progress_callback,
            classification_mode=classification_mode,
            existing_coded_col=coded_col if has_existing_classification else None
        )
        update_progress(f"   Classification completed: {len(self.classifications)} responses", 70)
        
        # Step 7: Identify outliers (low confidence)
        update_progress(f"\n[7/9] Analyzing classification quality...", 75)
        outliers = [c for c in self.classifications if c['confidence'] and c['confidence'] < 0.50]
        update_progress(f"   Found {len(outliers)} low-confidence responses", 78)
        
        # Step 8: Re-analyze outliers and create new categories if needed
        new_categories_added = 0
        if len(outliers) >= 10:
            print(f"\n[8/9] Re-analyzing outliers...")
            new_categories = self.classifier.analyze_outliers(outliers, question_text)
            
            if new_categories:
                # Add new categories
                for new_cat in new_categories:
                    if new_cat not in self.categories:
                        self.categories.append(new_cat)
                        new_categories_added += 1
                
                # Update category codes
                self.category_codes = self._create_category_codes()
                
                print(f"   Added {new_categories_added} new categories")
                print(f"   Total categories now: {len(self.categories)}")
                
                # Re-classify outliers only (PASS 2)
                print(f"\n   Re-classifying {len(outliers)} outliers with new categories...")
                outlier_indices = [o['index'] for o in outliers]
                self._reclassify_outliers(df_raw, variable_name, question_text, outlier_indices)
                print(f"   Re-classification completed")
            else:
                print(f"   No new categories needed (outliers too diverse)")
        else:
            print(f"\n[8/9] Skipping outlier re-analysis (< 10 outliers)")
        
        # Step 9: Update Excel files
        update_progress(f"\n[9/9] Saving results to Excel files...", 85)
        
        # Count statistics untuk summary
        empty_count = sum(1 for c in self.classifications if c['code'] is None)
        invalid_count = sum(1 for c in self.classifications if c['code'] == self.classifier.invalid_code)
        valid_classified = sum(1 for c in self.classifications if c['code'] is not None and c['code'] != self.classifier.invalid_code)
        
        output_files = self._update_excel_files(df_raw, variable_name)
        
        # Final progress update
        update_progress(f"   Files saved successfully", 95)
        update_progress(f"Classification complete!", 100)
        
        # Summary
        summary = {
            'variable': variable_name,
            'question': question_text,
            'total_submissions': len(df_raw),
            'responses_found': len(responses),
            'empty_responses': empty_count,
            'valid_responses': len(valid_responses),
            'invalid_text_responses': invalid_count,
            'valid_classified': valid_classified,
            'categories_generated': len(self.categories),
            'new_categories_added': new_categories_added,
            'outliers_found': len(outliers),
            'output_files': output_files
        }
        
        print("\n" + "=" * 80)
        print("CLASSIFICATION COMPLETED")
        print("=" * 80)
        print(f"\nSummary:")
        print(f"  Variable: {summary['variable']}")
        if summary['question']:
            print(f"  Question: {summary['question'][:80]}...")
        print(f"  Total submissions: {summary['total_submissions']}")
        print(f"  Responses found: {summary['responses_found']}")
        print(f"  Empty/Null: {summary['empty_responses']} (tidak dikode - sesuai logic Kobo)")
        print(f"  Valid responses: {summary['valid_responses']} → Classified to {summary['valid_classified']} responses")
        print(f"  Invalid text (TA/dll): {summary['invalid_text_responses']} → Code 99")
        print(f"  Initial categories: {summary['categories_generated'] - summary['new_categories_added']}")
        if summary['new_categories_added'] > 0:
            print(f"  New categories added: {summary['new_categories_added']}")
            print(f"  Final categories: {summary['categories_generated']}")
        print(f"  Outliers detected: {summary['outliers_found']}")
        print(f"\nBreakdown:")
        print(f"  - Empty/Null: {summary['empty_responses']} (dikosongkan)")
        print(f"  - Valid classified: {summary['valid_classified']} (code 1-{len(self.categories)})")
        print(f"  - Invalid text: {summary['invalid_text_responses']} (code 99)")
        print(f"\nOutput files:")
        for file in summary['output_files']:
            print(f"  - {file}")
        print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return summary
    
    def _load_raw_data(self):
        """Load raw data dari Excel file"""
        # Assume first sheet is the data
        df = pd.read_excel(self.raw_data_file_path, sheet_name=0)
        return df
    
    def _extract_responses(self, df, variable_name):
        """Extract responses dari kolom variable"""
        if variable_name not in df.columns:
            raise ValueError(f"Variable '{variable_name}' tidak ditemukan dalam raw data")
        
        # Get non-null responses
        responses = df[variable_name].dropna().astype(str).tolist()
        
        # Remove empty strings
        responses = [r.strip() for r in responses if r.strip()]
        
        return responses
    
    def _create_category_codes(self):
        """Create mapping dari category ke numeric codes"""
        codes = {}
        for idx, category in enumerate(self.categories, 1):
            codes[category] = idx
        return codes
    
    def _classify_all_responses(self, df, variable_name, question_text=None, progress_callback=None, 
                               classification_mode='incremental', existing_coded_col=None):
        """
        Classify semua responses dengan BATCH PROCESSING (10x faster!)
        AUTO-SELECT between PARALLEL (3-5x faster) or SEQUENTIAL (stable) mode
        
        Args:
            df: DataFrame with raw data
            variable_name: Variable name to classify
            question_text: Question context
            progress_callback: Progress callback function
            classification_mode: 'incremental' (only empty) or 'rerun' (all)
            existing_coded_col: Name of existing coded column (if any)
        """
        total = len(df)
        
        # Auto-select processing mode based on dataset size
        use_parallel = (
            self.parallel_classifier is not None and 
            total >= 100  # Only use parallel for datasets with >=100 rows
        )
        
        if use_parallel:
            print(f"\n[4/9] Classification: PARALLEL MODE ({total} responses - 3-5x FASTER!)")
            self._classify_responses_parallel(df, variable_name, question_text, progress_callback, classification_mode, existing_coded_col)
        else:
            print(f"\n[4/9] Classification: SEQUENTIAL MODE ({total} responses)")
            self._classify_responses_sequential(df, variable_name, question_text, progress_callback, classification_mode, existing_coded_col)
    
    def _classify_responses_parallel(self, df, variable_name, question_text=None, progress_callback=None, 
                                    classification_mode='incremental', existing_coded_col=None):
        """
        PARALLEL Classification - Process multiple batches simultaneously!
        3-5x FASTER than sequential (e.g., 17 minutes → 3-5 minutes)
        
        Args:
            df: DataFrame with raw data
            variable_name: Variable name to classify
            question_text: Question context
            progress_callback: Progress callback function
            classification_mode: 'incremental' (only empty) or 'rerun' (all)
            existing_coded_col: Name of existing coded column (if any)
        """
        self.classifications = []
        total = len(df)
        
        # Separate responses into 3 categories: existing, invalid, valid
        valid_responses = []
        valid_indices = []
        
        # Check for incremental mode
        incremental_mode = (classification_mode == 'incremental' and 
                           existing_coded_col is not None and 
                           existing_coded_col in df.columns)
        
        for idx, row in df.iterrows():
            response = row[variable_name]
            
            # INCREMENTAL MODE: Skip rows that already have classifications
            if incremental_mode:
                existing_code = row[existing_coded_col]
                if pd.notna(existing_code):
                    # Already classified - keep existing classification
                    self.classifications.append({
                        'index': idx,
                        'response': response,
                        'category': None,
                        'code': existing_code,
                        'confidence': 1.0,
                        'existing': True
                    })
                    continue
            
            # Skip null/empty responses
            if pd.isna(response) or str(response).strip() == '':
                self.classifications.append({
                    'index': idx,
                    'response': None,
                    'category': None,
                    'code': None,
                    'confidence': None,
                    'existing': False
                })
                continue
            
            # Check if valid response
            response_str = str(response).strip()
            if not self.classifier.is_valid_response(response_str):
                # Invalid (TA, tidak ada) → Code 99 WITHOUT OpenAI call
                self.classifications.append({
                    'index': idx,
                    'response': response_str,
                    'category': self.classifier.invalid_category,
                    'code': self.classifier.invalid_code,
                    'confidence': 1.0,
                    'existing': False
                })
                continue
            
            # Valid response → will classify with API
            valid_responses.append(response_str)
            valid_indices.append(idx)
        
        print(f"   Valid responses for API: {len(valid_responses)}")
        print(f"   Skipped (existing/invalid/empty): {len(self.classifications)}")
        
        # Classify valid responses in PARALLEL
        if len(valid_responses) > 0:
            results = self.parallel_classifier.classify_parallel(
                responses=valid_responses,
                categories=self.categories,
                question_text=question_text or "",
                batch_size=10,
                progress_callback=lambda msg, pct: progress_callback(msg, 50 + int(pct * 0.45)) if progress_callback else None
            )
            
            # Convert results to classifications format
            for idx, result, original_idx in zip(range(len(results)), results, valid_indices):
                if isinstance(result, list) and len(result) > 0:
                    # Multi-label or single category
                    categories_with_conf = result
                    category_names = [cat for cat, conf in categories_with_conf]
                    codes = [self.category_codes.get(cat, 0) for cat in category_names]
                    
                    # Join codes with space for Kobo format: "1 3"
                    code_str = " ".join(map(str, codes)) if len(codes) > 1 else codes[0]
                    
                    # Log multi-label
                    if len(codes) > 1:
                        print(f"\n[MULTI-LABEL] Response: '{valid_responses[idx][:60]}...'")
                        print(f"  Categories: {category_names}")
                        print(f"  Codes: {codes}")
                    
                    primary_category = category_names[0]
                    primary_confidence = categories_with_conf[0][1]
                    
                    self.classifications.append({
                        'index': original_idx,
                        'response': valid_responses[idx],
                        'category': primary_category,
                        'categories': category_names,
                        'code': code_str,
                        'codes': codes,
                        'confidence': primary_confidence,
                        'existing': False
                    })
                else:
                    # Fallback
                    self.classifications.append({
                        'index': original_idx,
                        'response': valid_responses[idx],
                        'category': 'Other',
                        'code': 0,
                        'confidence': 0.3,
                        'existing': False
                    })
        
        # Sort by original index
        self.classifications.sort(key=lambda x: x['index'])
        print(f"   Completed: {len(self.classifications)} responses classified")
    
    def _classify_responses_sequential(self, df, variable_name, question_text=None, progress_callback=None, 
                                      classification_mode='incremental', existing_coded_col=None):
        """
        SEQUENTIAL Classification (Original Implementation)
        Process one batch at a time - stable but slower
        
        Args:
            df: DataFrame with raw data
            variable_name: Variable name to classify
            question_text: Question context
            progress_callback: Progress callback function
            classification_mode: 'incremental' (only empty) or 'rerun' (all)
            existing_coded_col: Name of existing coded column (if any)
        """
        self.classifications = []
        total = len(df)
        
        # Collect all valid responses for batch processing
        valid_batch = []
        batch_indices = []
        
        BATCH_SIZE = 10  # Process 10 responses per API call
        
        BATCH_SIZE = 10  # Process 10 responses per API call
        
        # Check for incremental mode
        incremental_mode = (classification_mode == 'incremental' and 
                           existing_coded_col is not None and 
                           existing_coded_col in df.columns)
        
        for idx, row in df.iterrows():
            response = row[variable_name]
            
            # INCREMENTAL MODE: Skip rows that already have classifications
            if incremental_mode:
                existing_code = row[existing_coded_col]
                if pd.notna(existing_code):
                    # Already classified - keep existing classification
                    self.classifications.append({
                        'index': idx,
                        'response': response,
                        'category': None,  # We don't need to lookup category
                        'code': existing_code,
                        'confidence': 1.0,  # Assume existing is confident
                        'existing': True  # Flag as existing
                    })
                    continue
            
            # Skip null/empty responses - biarkan kosong sesuai logic Kobo
            if pd.isna(response) or str(response).strip() == '':
                self.classifications.append({
                    'index': idx,
                    'response': None,
                    'category': None,
                    'code': None,
                    'confidence': None,
                    'existing': False
                })
                continue
            
            # Check if valid response
            response_str = str(response).strip()
            if not self.classifier.is_valid_response(response_str):
                # Invalid (TA, tidak ada) → Code 99 WITHOUT OpenAI call (save cost!)
                invalid_category = self.classifier.invalid_category
                invalid_code = self.classifier.invalid_code
                
                self.classifications.append({
                    'index': idx,
                    'response': response_str,
                    'category': invalid_category,
                    'code': invalid_code,
                    'confidence': 1.0,
                    'existing': False
                })
                continue
            
            # Add to batch for OpenAI classification
            valid_batch.append(response_str)
            batch_indices.append(idx)
            
            # Process batch when full
            if len(valid_batch) >= BATCH_SIZE:
                if progress_callback:
                    progress = 50 + int((len(self.classifications) / total) * 45)  # 50-95%
                    progress_callback(f"   Classifying... {len(self.classifications)}/{total} ({int((len(self.classifications)/total)*100)}%)", progress)
                
                # BATCH API CALL (10x faster than individual calls!)
                results = self.classifier.classify_responses_batch(
                    valid_batch,
                    self.categories,
                    question_text=question_text
                )
                
                # DEBUG: Log first batch results to understand AI output
                if len(self.classifications) < 20:  # Only log first 2 batches
                    print(f"\n[DEBUG] Batch classification results:")
                    for i, (resp, result) in enumerate(zip(valid_batch[:3], results[:3])):
                        print(f"  Response {i+1}: '{resp[:60]}...'")
                        print(f"  AI returned: {result}")
                        print(f"  Type: {type(result)}, Length: {len(result) if isinstance(result, list) else 'N/A'}")
                
                # Store results - handle multi-label (list of tuples) or single-label (tuple)
                for batch_idx in range(min(len(results), len(batch_indices))):
                    result = results[batch_idx]
                    
                    # result is now a list of (category, confidence) tuples
                    if isinstance(result, list) and len(result) > 0:
                        # Multi-label or single category in list format
                        categories_with_conf = result
                        
                        # Get all category names and codes
                        category_names = [cat for cat, conf in categories_with_conf]
                        codes = [self.category_codes.get(cat, 0) for cat in category_names]
                        
                        # Join codes with space for Kobo format: "1 3"
                        code_str = " ".join(map(str, codes)) if len(codes) > 1 else codes[0]
                        
                        # DEBUG: Log multi-label detection
                        if len(codes) > 1:
                            print(f"\n[MULTI-LABEL DETECTED] Response: '{valid_batch[batch_idx][:60]}...'")
                            print(f"  Categories: {category_names}")
                            print(f"  Codes: {codes}")
                            print(f"  Output code_str: '{code_str}'")
                        
                        # For display, use primary category (first one)
                        primary_category = category_names[0]
                        primary_confidence = categories_with_conf[0][1]
                        
                        self.classifications.append({
                            'index': batch_indices[batch_idx],
                            'response': valid_batch[batch_idx],
                            'category': primary_category,  # Primary for display
                            'categories': category_names,  # All categories
                            'code': code_str,  # Space-separated codes: "1 3"
                            'codes': codes,  # List of codes for reference
                            'confidence': primary_confidence,  # Primary confidence
                            'existing': False
                        })
                    else:
                        # Fallback for unexpected format
                        self.classifications.append({
                            'index': batch_indices[batch_idx],
                            'response': valid_batch[batch_idx],
                            'category': 'Other',
                            'code': 0,
                            'confidence': 0.3,
                            'existing': False
                        })
                
                # Reset batch
                valid_batch = []
                batch_indices = []
        
        # Process remaining batch
        if len(valid_batch) > 0:
            if progress_callback:
                progress = 50 + int((len(self.classifications) / total) * 45)
                progress_callback(f"   Classifying... {len(self.classifications)}/{total} ({int((len(self.classifications)/total)*100)}%)", progress)
            
            results = self.classifier.classify_responses_batch(
                valid_batch,
                self.categories,
                question_text=question_text
            )
            
            # Store results - handle multi-label format
            for batch_idx in range(min(len(results), len(valid_batch))):
                result = results[batch_idx]
                
                # result is a list of (category, confidence) tuples
                if isinstance(result, list) and len(result) > 0:
                    categories_with_conf = result
                    
                    # Get all category names and codes
                    category_names = [cat for cat, conf in categories_with_conf]
                    codes = [self.category_codes.get(cat, 0) for cat in category_names]
                    
                    # Join codes with space for Kobo format: "1 3"
                    code_str = " ".join(map(str, codes)) if len(codes) > 1 else codes[0]
                    
                    # For display, use primary category (first one)
                    primary_category = category_names[0]
                    primary_confidence = categories_with_conf[0][1]
                    
                    self.classifications.append({
                        'index': batch_indices[batch_idx],
                        'response': valid_batch[batch_idx],
                        'category': primary_category,
                        'categories': category_names,
                        'code': code_str,  # "1 3" format
                        'codes': codes,
                        'confidence': primary_confidence,
                        'existing': False
                    })
                else:
                    self.classifications.append({
                        'index': batch_indices[batch_idx],
                        'response': valid_batch[batch_idx],
                        'category': 'Other',
                        'code': 0,
                        'confidence': 0.3,
                        'existing': False
                    })
        
        # Sort by original index
        self.classifications.sort(key=lambda x: x['index'])
        print(f"      Completed: {len(self.classifications)} responses classified")
    
    def _reclassify_outliers(self, df, variable_name, question_text, outlier_indices):
        """Re-classify outlier responses dengan kategori yang sudah di-update (MULTI-LABEL SUPPORT)"""
        reclassified = 0
        
        # Batch processing for efficiency (10 responses per batch)
        BATCH_SIZE = 10
        batch_responses = []
        batch_outlier_indices = []
        
        for outlier_idx in outlier_indices:
            # Get the response
            response = df.loc[outlier_idx, variable_name]
            
            if pd.isna(response) or str(response).strip() == '':
                continue
            
            response_str = str(response).strip()
            batch_responses.append(response_str)
            batch_outlier_indices.append(outlier_idx)
            
            # Process batch when full or at end
            if len(batch_responses) >= BATCH_SIZE or outlier_idx == outlier_indices[-1]:
                # BATCH CLASSIFICATION with MULTI-LABEL support
                results = self.classifier.classify_responses_batch(
                    batch_responses,
                    self.categories,
                    question_text=question_text
                )
                
                # Update classifications with multi-label results
                for batch_idx, result in enumerate(results):
                    current_outlier_idx = batch_outlier_indices[batch_idx]
                    
                    # Handle multi-label result (list of tuples)
                    if isinstance(result, list) and len(result) > 0:
                        categories_with_conf = result
                        
                        # Get all category names and codes
                        category_names = [cat for cat, conf in categories_with_conf]
                        codes = [self.category_codes.get(cat, 0) for cat in category_names]
                        
                        # Join codes with space for multi-label: "1 3"
                        code_str = " ".join(map(str, codes)) if len(codes) > 1 else codes[0]
                        
                        # Primary category and confidence
                        primary_category = category_names[0]
                        primary_confidence = categories_with_conf[0][1]
                        
                        # Update classification
                        for c in self.classifications:
                            if c['index'] == current_outlier_idx:
                                c['category'] = primary_category
                                c['categories'] = category_names  # All categories
                                c['code'] = code_str  # Space-separated codes
                                c['codes'] = codes  # List of codes
                                c['confidence'] = primary_confidence
                                reclassified += 1
                                
                                # DEBUG: Log multi-label outlier reclassification
                                if len(codes) > 1:
                                    print(f"\n[MULTI-LABEL OUTLIER] Response: '{batch_responses[batch_idx][:60]}...'")
                                    print(f"  Categories: {category_names}")
                                    print(f"  Codes: {code_str}")
                                break
                
                # Progress
                if reclassified % 10 == 0:
                    print(f"         Re-classified: {reclassified}/{len(outlier_indices)}")
                
                # Clear batch
                batch_responses = []
                batch_outlier_indices = []
        
        print(f"      Total re-classified: {reclassified} outliers")
    
    def _update_excel_files(self, df_raw, variable_name):
        """
        Update Excel files:
        1. Add coded column to raw data (right next to original column)
        2. Update choices in kobo system file
        """
        output_files = []
        
        # 1. Update raw data with coded column
        print(f"\n   [1/2] Updating raw data file...")
        
        # Determine output path
        output_path = self.output_raw_path if self.output_raw_path else self.raw_data_file_path
        
        # If output file already exists (from previous variable), read it first
        if os.path.exists(output_path) and output_path != self.raw_data_file_path:
            print(f"      Reading existing output file to preserve previous variables...")
            df_raw = pd.read_excel(output_path)
        
        # Find column position
        col_idx = df_raw.columns.get_loc(variable_name)
        
        # Create coded column name
        coded_col_name = f"{variable_name}_coded"
        
        # Extract codes from classifications
        # IMPORTANT: Convert ALL codes to STRING for consistency
        # Single-label: "1" (string)
        # Multi-label: "1 4" (string with space)
        codes = [str(c['code']) if c['code'] is not None else None for c in self.classifications]
        
        # Insert coded column right after original column (or update if exists)
        if coded_col_name in df_raw.columns:
            df_raw[coded_col_name] = codes
            print(f"      Updated existing column: {coded_col_name}")
        else:
            df_raw.insert(col_idx + 1, coded_col_name, codes)
            print(f"      Added new column: {coded_col_name}")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                df_raw.to_excel(output_path, index=False)
                output_files.append(output_path)
                print(f"      Saved: {output_path}")
                break
            except PermissionError:
                if attempt < max_retries - 1:
                    if progress_callback:
                        progress_callback(f"⚠️ File is open in another program. Attempt {attempt+1}/{max_retries}. Please close the file...", None)
                    import time
                    time.sleep(3)
                else:
                    error_msg = f"❌ Cannot save file - please close '{os.path.basename(self.raw_data_file_path)}' and try again"
                    if progress_callback:
                        progress_callback(error_msg, None)
                    raise PermissionError(error_msg)
        
        # 2. Update kobo system file - add choices
        print(f"\n   [2/2] Updating kobo system file...")
        
        # Determine kobo source path - use output if exists, otherwise original
        output_kobo_path = self.output_kobo_path if self.output_kobo_path else self.kobo_file_path
        kobo_source_path = output_kobo_path if os.path.exists(output_kobo_path) and output_kobo_path != self.kobo_file_path else self.kobo_file_path
        
        if kobo_source_path == output_kobo_path:
            print(f"      Reading existing output kobo file to preserve previous variables...")
        
        # Load kobo system file and get sheet names
        with pd.ExcelFile(kobo_source_path) as xl_kobo:
            sheet_names = xl_kobo.sheet_names
        
        # Read all sheets
        sheets = {}
        for sheet_name in sheet_names:
            sheets[sheet_name] = pd.read_excel(kobo_source_path, sheet_name=sheet_name)
        
        # Update choices sheet
        if 'choices' in sheets:
            df_choices = sheets['choices']
            
            # Create list_name for this variable
            list_name = f"{variable_name}_codes"
            
            # Remove existing entries for this list_name (if any)
            df_choices = df_choices[df_choices['list_name'] != list_name]
            
            # Add new choices (including invalid category)
            new_choices = []
            
            # Add regular categories
            for category, code in self.category_codes.items():
                new_choices.append({
                    'list_name': list_name,
                    'name': str(code),
                    'label': category,
                    'S1': None  # Keep other columns as None
                })
            
            # Add invalid category with special code
            invalid_category = self.classifier.invalid_category
            invalid_code = self.classifier.invalid_code
            new_choices.append({
                'list_name': list_name,
                'name': str(invalid_code),
                'label': invalid_category,
                'S1': None
            })
            
            # Append new choices
            df_new_choices = pd.DataFrame(new_choices)
            df_choices = pd.concat([df_choices, df_new_choices], ignore_index=True)
            
            # Update the sheet
            sheets['choices'] = df_choices
            print(f"      Added {len(new_choices)} choices to list '{list_name}'")
        
        # Update survey sheet (optional - add the coded field definition)
        if 'survey' in sheets:
            df_survey = sheets['survey']
            
            # Check if coded field already exists
            if coded_col_name not in df_survey['name'].values:
                # Find the original E1 question row
                e1_row_idx = df_survey[df_survey['name'] == variable_name].index
                
                if len(e1_row_idx) > 0:
                    # Get original E1 row
                    original_row = df_survey.loc[e1_row_idx[0]]
                    
                    # Create new row for coded field
                    new_row = {
                        'type': f"select_one {variable_name}_codes",
                        'name': coded_col_name,
                        'label': f"{original_row.get('label', variable_name)} - Coded",
                        'required': False,
                        'appearance': None,
                        'constraint': None,
                        'constraint_message': None,
                        'relevant': original_row.get('relevant'),  # Same relevance logic
                        'choice_filter': None
                    }
                    
                    # Insert after the original row
                    insert_idx = e1_row_idx[0] + 1
                    df_survey = pd.concat([
                        df_survey.iloc[:insert_idx],
                        pd.DataFrame([new_row]),
                        df_survey.iloc[insert_idx:]
                    ], ignore_index=True)
                    
                    sheets['survey'] = df_survey
                    print(f"      Added coded field '{coded_col_name}' to survey")
                else:
                    print(f"      Field '{coded_col_name}' already exists in survey")
        
        # Save to output kobo file (or overwrite if output path not set)
        output_kobo_path = self.output_kobo_path if self.output_kobo_path else self.kobo_file_path
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with pd.ExcelWriter(output_kobo_path, engine='openpyxl') as writer:
                    for sheet_name, df_sheet in sheets.items():
                        df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)
                
                output_files.append(output_kobo_path)
                print(f"      Saved: {output_kobo_path}")
                break
            except PermissionError:
                if attempt < max_retries - 1:
                    if progress_callback:
                        progress_callback(f"⚠️ File is open in another program. Attempt {attempt+1}/{max_retries}. Please close the file...", None)
                    import time
                    time.sleep(3)
                else:
                    error_msg = f"❌ Cannot save file - please close '{os.path.basename(output_kobo_path)}' and try again"
                    if progress_callback:
                        progress_callback(error_msg, None)
                    raise PermissionError(error_msg)
        
        return output_files
    
    def _load_existing_categories_from_kobo(self, variable_name):
        """
        Load existing categories from Kobo system file for incremental classification
        
        Args:
            variable_name: Variable name (e.g., 'E1')
        
        Returns:
            List of category names, or empty list if not found
        """
        try:
            # Read choices sheet
            df_choices = pd.read_excel(self.kobo_file_path, sheet_name='choices')
            
            # Find categories for this variable
            list_name = f"{variable_name}_codes"
            var_choices = df_choices[df_choices['list_name'] == list_name]
            
            if len(var_choices) == 0:
                return []
            
            # Extract category labels (exclude invalid category)
            categories = []
            for _, row in var_choices.iterrows():
                label = str(row['label'])
                code = str(row['name'])
                
                # Skip invalid category
                if code == str(self.classifier.invalid_code) or label == self.classifier.invalid_category:
                    continue
                
                categories.append(label)
            
            return categories
            
        except Exception as e:
            print(f"[ERROR] Failed to load existing categories: {e}")
            return []


def main():
    """Main function untuk run classifier"""
    # File paths
    base_path = r"c:\Users\hp\OneDrive - MarkPlus Indonesia ,PT\MARKPLUS\Automation\koding\files"
    kobo_file = os.path.join(base_path, "kobo_system_ASDP_berkendara.xlsx")
    raw_data_file = os.path.join(base_path, "Raw_Data_ASDP_Berkendara.xlsx")
    
    # Validate files exist
    if not os.path.exists(kobo_file):
        print(f"ERROR: Kobo system file tidak ditemukan: {kobo_file}")
        return
    
    if not os.path.exists(raw_data_file):
        print(f"ERROR: Raw data file tidak ditemukan: {raw_data_file}")
        return
    
    # Initialize classifier
    classifier = ExcelClassifier(kobo_file, raw_data_file)
    
    # Define questions
    questions = {
        'E1': 'Pengembangan apa yang diharapkan di Ferizy (Untuk Merak, Bakauheni, Ketapang, Danau Toba)',
        'E2': 'Bagaimana tingkat kemudahan akses dan kepuasan terhadap aplikasi atau website Ferizy'
    }
    
    # Process variables
    variables_to_process = ['E1', 'E2']
    
    for var in variables_to_process:
        try:
            print(f"\n{'='*80}")
            print(f"PROCESSING VARIABLE: {var}")
            print(f"{'='*80}\n")
            
            summary = classifier.process_variable(
                variable_name=var,
                question_text=questions.get(var)
            )
            print(f"\n[SUCCESS] Variable {var} selesai dikoding!")
            
        except Exception as e:
            print(f"\n[ERROR] Terjadi kesalahan pada variable {var}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n{'='*80}")
    print("ALL VARIABLES COMPLETED")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()

"""
Semi Open-Ended Processor
Process pre-coded questions with "Lainnya" (Other) option and merge with classifications
"""
import pandas as pd
import logging
from typing import Dict, List
from openai_classifier import OpenAIClassifier


class SemiOpenProcessor:
    """Process semi open-ended questions: merge pre-coded + open-ended responses"""
    
    def __init__(self, kobo_system_path: str, raw_data_path: str, openai_api_key: str):
        """
        Initialize processor
        
        Args:
            kobo_system_path: Path to kobo_system_*.xlsx
            raw_data_path: Path to raw data Excel
            openai_api_key: OpenAI API key for classification
        """
        self.kobo_system_path = kobo_system_path
        self.raw_data_path = raw_data_path
        self.openai_api_key = openai_api_key
        
        self.kobo_system_df = None
        self.choices_df = None
        self.raw_data_df = None
        self.classifier = OpenAIClassifier(openai_api_key)
        
        self.logger = logging.getLogger(__name__)
        
    def load_data(self):
        """Load all required data"""
        self.logger.info("Loading data files...")
        
        # Load kobo_system sheets
        self.kobo_system_df = pd.read_excel(self.kobo_system_path, sheet_name='survey')
        self.choices_df = pd.read_excel(self.kobo_system_path, sheet_name='choices')
        
        # Load raw data
        self.raw_data_df = pd.read_excel(self.raw_data_path)
        
        self.logger.info(f"✅ Loaded {len(self.raw_data_df)} responses")
        
    def get_choice_labels(self, list_name: str) -> Dict[int, str]:
        """
        Get choice labels for a select question
        
        Args:
            list_name: Name of the choice list (e.g., 'S10')
            
        Returns:
            Dict mapping code to label
            Example: {1: 'Suami / istri', 2: 'Orang tua', 96: 'Lainnya'}
        """
        if self.choices_df is None:
            return {}
        
        choice_map = {}
        
        for _, row in self.choices_df[self.choices_df['list_name'] == list_name].iterrows():
            try:
                code = int(row['name'])
                label = row['label']
                choice_map[code] = label
            except (ValueError, TypeError):
                # If code is not integer
                code = row['name']
                label = row['label']
                choice_map[code] = label
        
        return choice_map
    
    def process_semi_open_pair(self, pair: Dict, progress_callback=None) -> Dict:
        """
        Process a semi open-ended pair
        
        Args:
            pair: Dict with pair info from SemiOpenDetector
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dict with results including merged variable
        """
        select_var = pair['select_var']
        text_var = pair['text_var']
        lainnya_code = pair['lainnya_code']
        list_name = pair['list_name']
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Processing semi open-ended: {select_var} + {text_var}")
        self.logger.info(f"{'='*60}")
        
        # Step 1: Get choice labels
        choice_labels = self.get_choice_labels(list_name)
        self.logger.info(f"📋 Found {len(choice_labels)} pre-coded choices")
        
        # Step 2: Extract responses that selected "Lainnya"
        lainnya_responses = self._extract_lainnya_responses(select_var, text_var, lainnya_code)
        
        if lainnya_responses.empty:
            self.logger.warning(f"⚠️  No 'Lainnya' responses found for {text_var}")
            return {
                'success': False,
                'message': f"No responses with 'Lainnya' option",
                'select_var': select_var,
                'text_var': text_var
            }
        
        self.logger.info(f"📝 Found {len(lainnya_responses)} responses with 'Lainnya'")
        
        # Step 3: Classify the "Lainnya" text responses
        if progress_callback:
            progress_callback(f"Classifying {len(lainnya_responses)} 'Lainnya' responses for {text_var}...")
        
        categories, classified_df = self._classify_lainnya_responses(
            text_var, 
            lainnya_responses,
            pair.get('text_label', '')
        )
        
        self.logger.info(f"✅ Generated {len(categories)} new categories from 'Lainnya' responses")
        
        # Step 4: Assign new codes to categories (start after existing codes)
        max_existing_code = max(choice_labels.keys()) if choice_labels else 0
        new_code_start = max_existing_code + 1
        
        category_code_map = {}
        for i, cat in enumerate(categories, start=new_code_start):
            category_code_map[cat['category']] = i
        
        # Step 5: Create merged variable
        merged_var = f"{select_var}_merged"
        merged_df = self._create_merged_variable(
            select_var,
            text_var,
            lainnya_code,
            choice_labels,
            classified_df,
            category_code_map
        )
        
        # Step 6: Update choices sheet
        new_choices = self._create_new_choices(list_name, categories, new_code_start)
        
        result = {
            'success': True,
            'select_var': select_var,
            'text_var': text_var,
            'merged_var': merged_var,
            'merged_df': merged_df,
            'new_categories': categories,
            'new_choices': new_choices,
            'category_code_map': category_code_map,
            'choice_labels': choice_labels,
            'lainnya_code': lainnya_code,
            'stats': {
                'total_responses': len(self.raw_data_df),
                'lainnya_responses': len(lainnya_responses),
                'new_categories': len(categories),
                'pre_coded_options': len(choice_labels)
            }
        }
        
        self.logger.info(f"✅ Successfully processed {select_var} + {text_var}")
        self.logger.info(f"📊 Stats: {len(lainnya_responses)} 'Lainnya' → {len(categories)} new categories")
        
        return result
    
    def _extract_lainnya_responses(self, select_var: str, text_var: str, lainnya_code) -> pd.DataFrame:
        """Extract responses where select_var = lainnya_code"""
        if select_var not in self.raw_data_df.columns:
            self.logger.error(f"❌ Select variable '{select_var}' not found in raw data")
            return pd.DataFrame()
        
        if text_var not in self.raw_data_df.columns:
            self.logger.error(f"❌ Text variable '{text_var}' not found in raw data")
            return pd.DataFrame()
        
        # Filter rows where select_var equals lainnya_code
        mask = self.raw_data_df[select_var] == lainnya_code
        
        # Get text responses for those rows
        lainnya_df = self.raw_data_df[mask][[text_var]].copy()
        lainnya_df = lainnya_df[lainnya_df[text_var].notna()]  # Remove empty responses
        
        return lainnya_df
    
    def _classify_lainnya_responses(self, text_var: str, responses_df: pd.DataFrame, question_text: str) -> tuple:
        """
        Classify the "Lainnya" text responses using OpenAI
        
        Returns:
            Tuple of (categories, classified_df)
        """
        responses_list = responses_df[text_var].tolist()
        
        # Phase 1: Generate categories
        self.logger.info("🤖 Phase 1: Generating categories from 'Lainnya' responses...")
        categories = self.classifier.generate_categories(
            responses=responses_list,
            question_text=question_text,
            max_categories=10
        )
        
        # Phase 2: Classify all responses
        self.logger.info("🤖 Phase 2: Classifying 'Lainnya' responses...")
        classified_results = []
        
        for response in responses_list:
            result = self.classifier.classify_response(
                response=response,
                categories=categories,
                question_text=question_text
            )
            classified_results.append(result)
        
        # Create DataFrame with results
        classified_df = responses_df.copy()
        classified_df['category'] = [r['category'] for r in classified_results]
        classified_df['category_number'] = [r['category_number'] for r in classified_results]
        classified_df['confidence'] = [r['confidence'] for r in classified_results]
        
        return categories, classified_df
    
    def _create_merged_variable(self, select_var: str, text_var: str, lainnya_code,
                                choice_labels: Dict, classified_df: pd.DataFrame,
                                category_code_map: Dict) -> pd.DataFrame:
        """
        Create merged variable combining pre-coded and classified responses
        
        Logic:
        - If select_var != lainnya_code → use pre-coded label (from choice_labels)
        - If select_var == lainnya_code → use classified category (from classified_df)
        """
        merged_df = self.raw_data_df.copy()
        
        # Initialize merged columns
        merged_code_col = []
        merged_label_col = []
        
        # Create lookup for classified responses (text -> category code)
        text_to_category = {}
        if not classified_df.empty:
            for _, row in classified_df.iterrows():
                text = row[text_var]
                category = row['category']
                code = category_code_map.get(category)
                text_to_category[text] = code
        
        # Iterate through all rows
        for _, row in merged_df.iterrows():
            select_value = row[select_var]
            text_value = row[text_var] if text_var in row else None
            
            if pd.isna(select_value):
                # No selection made
                merged_code_col.append(None)
                merged_label_col.append(None)
            elif select_value == lainnya_code:
                # "Lainnya" selected - use classified category
                if pd.notna(text_value) and text_value in text_to_category:
                    code = text_to_category[text_value]
                    # Find category label
                    category = next((k for k, v in category_code_map.items() if v == code), "Unknown")
                    merged_code_col.append(code)
                    merged_label_col.append(category)
                else:
                    # Lainnya selected but no text or not classified
                    merged_code_col.append(lainnya_code)
                    merged_label_col.append(choice_labels.get(lainnya_code, "Lainnya"))
            else:
                # Pre-coded option selected
                merged_code_col.append(select_value)
                merged_label_col.append(choice_labels.get(select_value, f"Code {select_value}"))
        
        # Add merged columns to dataframe
        merged_var_code = f"{select_var}_merged"
        merged_var_label = f"{select_var}_merged_label"
        
        merged_df[merged_var_code] = merged_code_col
        merged_df[merged_var_label] = merged_label_col
        
        return merged_df
    
    def _create_new_choices(self, list_name: str, categories: List[Dict], start_code: int) -> pd.DataFrame:
        """
        Create new rows for choices sheet
        
        Returns:
            DataFrame with new choices to be inserted
        """
        new_choices = []
        
        for i, cat in enumerate(categories, start=start_code):
            new_choices.append({
                'list_name': list_name,
                'name': i,
                'label': cat['category']
            })
        
        return pd.DataFrame(new_choices)
    
    def save_results(self, result: Dict, output_path: str):
        """
        Save results to Excel file
        
        Args:
            result: Result dict from process_semi_open_pair
            output_path: Path to save output Excel
        """
        self.logger.info(f"💾 Saving results to {output_path}...")
        
        # Get merged data
        merged_df = result['merged_df']
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Save merged raw data
            merged_df.to_excel(writer, sheet_name='data', index=False)
            
            # Update and save choices
            updated_choices = self._update_choices_sheet(result)
            updated_choices.to_excel(writer, sheet_name='choices', index=False)
            
            # Save survey sheet (unchanged)
            self.kobo_system_df.to_excel(writer, sheet_name='survey', index=False)
            
            # Save category summary
            summary_df = self._create_summary_df(result)
            summary_df.to_excel(writer, sheet_name='category_summary', index=False)
        
        self.logger.info(f"✅ Results saved successfully!")
    
    def _update_choices_sheet(self, result: Dict) -> pd.DataFrame:
        """Update choices sheet with new categories"""
        # Start with existing choices
        updated_choices = self.choices_df.copy()
        
        # Append new choices
        new_choices = result['new_choices']
        updated_choices = pd.concat([updated_choices, new_choices], ignore_index=True)
        
        return updated_choices
    
    def _create_summary_df(self, result: Dict) -> pd.DataFrame:
        """Create summary DataFrame for reporting"""
        summary_data = []
        
        # Pre-coded options
        for code, label in result['choice_labels'].items():
            summary_data.append({
                'Type': 'Pre-coded',
                'Code': code,
                'Label': label,
                'Source': 'Original choices'
            })
        
        # New categories from classification
        for category, code in result['category_code_map'].items():
            summary_data.append({
                'Type': 'New (from Lainnya)',
                'Code': code,
                'Label': category,
                'Source': 'AI Classification'
            })
        
        return pd.DataFrame(summary_data)

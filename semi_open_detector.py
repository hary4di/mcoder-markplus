"""
Semi Open-Ended Detector
Detect and process pre-coded questions with "Lainnya" (Other) option
"""
import pandas as pd
import re
from typing import Dict, List, Tuple, Optional


class SemiOpenDetector:
    """Detect semi open-ended question pairs from Kobo system file"""
    
    def __init__(self, kobo_system_path: str):
        """
        Initialize detector with kobo_system file
        
        Args:
            kobo_system_path: Path to kobo_system_*.xlsx file
        """
        self.kobo_system_path = kobo_system_path
        self.survey_df = None
        self.choices_df = None
        self.semi_open_pairs = []
        
    def load_sheets(self):
        """Load survey and choices sheets"""
        self.survey_df = pd.read_excel(self.kobo_system_path, sheet_name='survey')
        self.choices_df = pd.read_excel(self.kobo_system_path, sheet_name='choices')
        
    def detect_lainnya_in_choices(self) -> Dict[str, int]:
        """
        Detect "Lainnya" option in choices sheet
        
        Returns:
            Dict mapping list_name to lainnya code
            Example: {'S9': 96, 'S10': 96}
        """
        lainnya_map = {}
        
        if self.choices_df is None or self.choices_df.empty:
            return lainnya_map
        
        # Find rows with "lainnya" in label (case-insensitive)
        lainnya_pattern = re.compile(r'lainnya', re.IGNORECASE)
        
        for _, row in self.choices_df.iterrows():
            list_name = row.get('list_name', '')
            name = row.get('name', '')
            label = str(row.get('label', '')).lower()
            
            if lainnya_pattern.search(label):
                # Store the list_name and the code (name)
                try:
                    code = int(name)
                    lainnya_map[list_name] = code
                except (ValueError, TypeError):
                    # If code is not integer, store as string
                    lainnya_map[list_name] = name
                    
        return lainnya_map
    
    def detect_semi_open_pairs(self) -> List[Dict]:
        """
        Detect semi open-ended question pairs
        
        Logic:
        1. Find select_one/select_multiple questions with "Lainnya" in choices
        2. Find corresponding text field (usually with _L or _lainnya suffix)
        
        Returns:
            List of dicts with pair information:
            [
                {
                    'select_var': 'S10',
                    'text_var': 'S10_L',
                    'lainnya_code': 96,
                    'select_label': 'Dengan siapa Anda paling sering bepergian...',
                    'text_label': 'Lainnya, sebutkan__',
                    'list_name': 'S10'
                }
            ]
        """
        if self.survey_df is None:
            self.load_sheets()
        
        pairs = []
        lainnya_map = self.detect_lainnya_in_choices()
        
        if not lainnya_map:
            print("⚠️  No 'Lainnya' options found in choices sheet")
            return pairs
        
        # Iterate through survey rows
        for idx, row in self.survey_df.iterrows():
            var_type = row.get('type', '')
            var_name = row.get('name', '')
            
            # Check if this is a select question with lainnya option
            if var_type in ['select_one', 'select_multiple']:
                # Extract list_name from type (e.g., "select_one S10" -> "S10")
                type_parts = var_type.split()
                if len(type_parts) > 1:
                    list_name = type_parts[1]
                else:
                    # Try to get from name if not in type
                    list_name = var_name
                
                # Check if this list has lainnya option
                if list_name in lainnya_map:
                    lainnya_code = lainnya_map[list_name]
                    
                    # Look for corresponding text field
                    # Common patterns: S10_L, S10_lainnya, S10_other
                    text_var = self._find_text_pair(var_name, idx)
                    
                    if text_var:
                        pair = {
                            'select_var': var_name,
                            'text_var': text_var['name'],
                            'lainnya_code': lainnya_code,
                            'select_label': row.get('label', ''),
                            'text_label': text_var['label'],
                            'list_name': list_name,
                            'select_type': var_type
                        }
                        pairs.append(pair)
                        print(f"✅ Detected semi open-ended pair: {var_name} + {text_var['name']} (code: {lainnya_code})")
        
        self.semi_open_pairs = pairs
        return pairs
    
    def _find_text_pair(self, select_var: str, select_idx: int) -> Optional[Dict]:
        """
        Find corresponding text field for select variable
        
        Args:
            select_var: Name of select variable (e.g., 'S10')
            select_idx: Index of select variable in survey df
            
        Returns:
            Dict with text variable info or None
        """
        # Common suffixes for "lainnya" text fields
        suffixes = ['_L', '_l', '_lainnya', '_Lainnya', '_other', '_Other']
        
        # Check next few rows (usually text field comes right after select)
        search_range = min(select_idx + 5, len(self.survey_df))
        
        for idx in range(select_idx + 1, search_range):
            row = self.survey_df.iloc[idx]
            var_type = row.get('type', '')
            var_name = row.get('name', '')
            label = str(row.get('label', '')).lower()
            
            # Check if this is a text field
            if var_type == 'text':
                # Check if name matches pattern
                for suffix in suffixes:
                    if var_name == f"{select_var}{suffix}":
                        return {
                            'name': var_name,
                            'label': row.get('label', ''),
                            'type': var_type
                        }
                
                # Also check if label contains "lainnya" or "sebutkan"
                if 'lainnya' in label or 'sebutkan' in label:
                    # Verify it's related to select_var
                    if var_name.startswith(select_var):
                        return {
                            'name': var_name,
                            'label': row.get('label', ''),
                            'type': var_type
                        }
        
        return None
    
    def get_summary(self) -> str:
        """Get summary of detected semi open-ended pairs"""
        if not self.semi_open_pairs:
            return "No semi open-ended pairs detected"
        
        summary = f"📊 Found {len(self.semi_open_pairs)} semi open-ended pair(s):\n\n"
        
        for i, pair in enumerate(self.semi_open_pairs, 1):
            summary += f"{i}. {pair['select_var']} (code {pair['lainnya_code']}: Lainnya) + {pair['text_var']}\n"
            summary += f"   Label: {pair['select_label'][:60]}...\n"
            summary += f"   Text field: {pair['text_label'][:60]}...\n\n"
        
        return summary


def test_detector():
    """Test function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python semi_open_detector.py <kobo_system_file.xlsx>")
        return
    
    file_path = sys.argv[1]
    
    print(f"🔍 Analyzing: {file_path}\n")
    
    detector = SemiOpenDetector(file_path)
    detector.load_sheets()
    
    # Show choices with lainnya
    lainnya_map = detector.detect_lainnya_in_choices()
    print(f"📋 Lainnya options found: {lainnya_map}\n")
    
    # Detect pairs
    pairs = detector.detect_semi_open_pairs()
    
    # Show summary
    print(detector.get_summary())


if __name__ == "__main__":
    test_detector()

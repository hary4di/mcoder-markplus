"""
File Upload and Processing Utilities
"""
import os
import pandas as pd
from werkzeug.utils import secure_filename
from typing import Dict, List, Tuple
from semi_open_detector import SemiOpenDetector

class FileProcessor:
    """Process uploaded files for classification"""
    
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    
    def __init__(self, upload_folder: str):
        self.upload_folder = upload_folder
        os.makedirs(upload_folder, exist_ok=True)
    
    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def save_file(self, file, prefix: str = '', add_timestamp: bool = True) -> tuple:
        """
        Save uploaded file securely with optional timestamp
        
        Args:
            file: FileStorage object
            prefix: Prefix for filename (e.g., 'input_kobo', 'input_raw')
            add_timestamp: Add timestamp to filename (default: True)
        
        Returns:
            tuple: (filepath, original_filename)
        """
        from datetime import datetime
        
        original_filename = secure_filename(file.filename)
        base_name, extension = os.path.splitext(original_filename)
        
        if add_timestamp:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if prefix:
                filename = f"{prefix}_{timestamp}{extension}"
            else:
                filename = f"{base_name}_{timestamp}{extension}"
        else:
            filename = original_filename if not prefix else f"{prefix}_{original_filename}"
        
        filepath = os.path.join(self.upload_folder, filename)
        file.save(filepath)
        return filepath, original_filename
    
    def detect_open_ended_variables(self, kobo_system_path: str) -> List[Dict]:
        """
        Auto-detect open-ended variables from Kobo System file
        
        Strategy:
        1. Read survey sheet from kobo_system file
        2. Filter: type="text" AND starts with evaluation prefix (E, F, G) 
        3. Exclude: Profil fields (nama, alamat, telepon, email, ktp, dll)
        4. Exclude: Screening fields (S*) and semi open-ended (label contains "lainnya/sebutkan")
        
        Args:
            kobo_system_path: Path to kobo_system Excel file
        
        Returns:
            List of dicts with variable info: {name, label, type}
        """
        try:
            with pd.ExcelFile(kobo_system_path) as xl:
                if 'survey' not in xl.sheet_names:
                    return []
            
            df_survey = pd.read_excel(kobo_system_path, sheet_name='survey')
            
            # Required columns
            if 'type' not in df_survey.columns or 'name' not in df_survey.columns:
                return []
            
            # Field profil yang harus di-exclude
            profile_fields = [
                'nama', 'name', 'alamat', 'address', 'telepon', 'telpon', 'phone',
                'hp', 'handphone', 'email', 'ktp', 'nik', 'interviewer', 'enumerator',
                'tanggal', 'date', 'waktu', 'time', 'lokasi', 'location', 'wilayah'
            ]
            
            detected_vars = []
            
            for idx, row in df_survey.iterrows():
                var_type = str(row['type']).lower().strip()
                var_name = str(row['name']).strip()
                var_label = str(row.get('label', var_name))
                
                # Filter 1: Must be text type
                if var_type != 'text':
                    continue
                
                # Filter 2: Exclude profile fields
                if var_name.lower() in profile_fields:
                    continue
                
                # Filter 3: Exclude screening fields (dimulai dengan S)
                if var_name.upper().startswith('S'):
                    continue
                
                # Filter 4: Exclude semi open-ended (pre-coded)
                label_lower = var_label.lower()
                if any(keyword in label_lower for keyword in ['lainnya', 'sebutkan', 'lain nya', 'other', 'others']):
                    continue
                
                detected_vars.append({
                    'name': var_name,
                    'label': var_label,
                    'type': var_type
                })
            
            return detected_vars
            
        except Exception as e:
            print(f"Error detecting variables: {e}")
            return []
    
    def detect_semi_open_pairs(self, kobo_system_path: str) -> List[Dict]:
        """
        Detect semi open-ended pairs (select + text with 'Lainnya' option)
        
        Args:
            kobo_system_path: Path to kobo_system Excel file
        
        Returns:
            List of detected pairs
        """
        try:
            detector = SemiOpenDetector(kobo_system_path)
            pairs = detector.detect_semi_open_pairs()
            return pairs
        except Exception as e:
            print(f"Error detecting semi open-ended pairs: {e}")
            return []
    
    def get_semi_open_statistics(self, raw_data_path: str, pair: Dict) -> Dict:
        """
        Get statistics for semi open-ended pair
        
        Args:
            raw_data_path: Path to raw data Excel file
            pair: Semi open-ended pair info
        
        Returns:
            Dict with statistics
        """
        try:
            df = pd.read_excel(raw_data_path, sheet_name=0)
            
            select_var = pair['select_var']
            text_var = pair['text_var']
            lainnya_code = pair['lainnya_code']
            
            if select_var not in df.columns or text_var not in df.columns:
                return {'error': 'Variables not found'}
            
            # Count responses where 'Lainnya' was selected
            lainnya_mask = df[select_var] == lainnya_code
            lainnya_count = lainnya_mask.sum()
            
            # Count how many have text filled
            text_filled = df.loc[lainnya_mask, text_var].notna().sum()
            
            # Sample text
            sample_texts = df.loc[lainnya_mask & df[text_var].notna(), text_var].head(3).tolist()
            
            # Check if merged column exists
            merged_col = f"{select_var}_merged"
            has_merged = merged_col in df.columns
            
            stats = {
                'lainnya_count': int(lainnya_count),
                'text_filled_count': int(text_filled),
                'sample_texts': sample_texts,
                'has_merged_column': has_merged,
                'classification_status': 'completed' if has_merged else 'not_started'
            }
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_variable_statistics(self, raw_data_path: str, var_name: str) -> Dict:
        """
        Get statistics for a specific variable from raw data
        
        Args:
            raw_data_path: Path to raw data Excel file
            var_name: Variable name
        
        Returns:
            Dict with statistics
        """
        try:
            df = pd.read_excel(raw_data_path, sheet_name=0)
            
            if var_name not in df.columns:
                return {'error': 'Variable not found'}
            
            non_null_values = df[var_name].dropna().astype(str)
            
            if len(non_null_values) == 0:
                return {
                    'response_count': 0,
                    'avg_length': 0,
                    'sample_data': '',
                    'classification_status': 'empty'
                }
            
            avg_length = non_null_values.str.len().mean()
            sample = non_null_values.iloc[0] if len(non_null_values) > 0 else ""
            
            stats = {
                'response_count': int(len(non_null_values)),
                'avg_length': round(avg_length, 1),
                'sample_data': sample[:100] + '...' if len(str(sample)) > 100 else sample
            }
            
            # Check if variable has been classified before
            coded_col = f"{var_name}_coded"
            if coded_col in df.columns:
                # Count filled vs empty in coded column
                # Only check rows where original column has data
                mask = df[var_name].notna()
                total_with_data = mask.sum()
                coded_filled = df.loc[mask, coded_col].notna().sum()
                coded_empty = total_with_data - coded_filled
                
                stats['has_coded_column'] = True
                stats['coded_filled_count'] = int(coded_filled)
                stats['coded_empty_count'] = int(coded_empty)
                
                if coded_empty == 0:
                    stats['classification_status'] = 'completed'
                else:
                    stats['classification_status'] = 'partial'
            else:
                stats['has_coded_column'] = False
                stats['classification_status'] = 'not_started'
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def validate_excel_structure(self, excel_path: str) -> Tuple[bool, str]:
        """
        Validate Excel file structure
        
        Args:
            excel_path: Path to Excel file
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            df = pd.read_excel(excel_path, sheet_name=0)
            
            if df.empty:
                return False, "Excel file is empty"
            
            if len(df.columns) == 0:
                return False, "No columns found in Excel file"
            
            return True, "Valid"
            
        except Exception as e:
            return False, f"Error reading Excel: {str(e)}"
    
    def get_file_info(self, excel_path: str) -> Dict:
        """
        Get basic information about Excel file
        
        Args:
            excel_path: Path to Excel file
        
        Returns:
            Dict with file info
        """
        try:
            df = pd.read_excel(excel_path, sheet_name=0)
            
            return {
                'rows': len(df),
                'columns': len(df.columns),
                'file_size_mb': round(os.path.getsize(excel_path) / (1024 * 1024), 2)
            }
        except Exception as e:
            return {'error': str(e)}

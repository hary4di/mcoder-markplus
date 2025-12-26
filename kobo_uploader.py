"""
Kobo Uploader
Module untuk upload hasil klasifikasi ke Kobo sebagai field baru dengan kode numerik
"""
import requests
import json
import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

class KoboUploader:
    """Uploader untuk menambahkan field dan choices ke Kobo Asset"""
    
    def __init__(self):
        """Initialize Kobo uploader"""
        self.asset_id = os.getenv('KOBO_ASSET_ID')
        self.api_token = os.getenv('KOBO_API_TOKEN')
        self.base_url = os.getenv('KOBO_BASE_URL', 'https://kf.kobotoolbox.org')
        
        self.headers = {
            'Authorization': f'Token {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def create_category_codes(self, categories: List[str]) -> Dict[str, int]:
        """
        Create numeric codes for categories
        
        Args:
            categories: List of category names
        
        Returns:
            Dict mapping category name to numeric code
        """
        category_codes = {}
        for idx, category in enumerate(categories, start=1):
            category_codes[category] = idx
        return category_codes
    
    def generate_choices_list(self, categories: List[str], list_name: str = "e1_categories") -> List[Dict]:
        """
        Generate choices list for Kobo
        
        Args:
            categories: List of category names
            list_name: Name of the choice list
        
        Returns:
            List of choice dictionaries
        """
        choices = []
        category_codes = self.create_category_codes(categories)
        
        for category, code in category_codes.items():
            choices.append({
                "list_name": list_name,
                "name": str(code),
                "label": [category]  # Kobo format: label as list
            })
        
        return choices
    
    def add_classification_field_to_asset(self, 
                                          source_field: str,
                                          new_field_name: str,
                                          categories: List[str],
                                          list_name: str = None) -> bool:
        """
        Add classification field to Kobo asset
        
        Args:
            source_field: Original field name (e.g., 'Group_E/E1')
            new_field_name: New field name for classification (e.g., 'Group_E/E1_coded')
            categories: List of category names
            list_name: Name for the choice list (default: auto-generated)
        
        Returns:
            bool: True if successful
        """
        if list_name is None:
            list_name = f"{new_field_name.replace('/', '_')}_list"
        
        try:
            print(f"\n[Kobo Asset Update]")
            print(f"   Source field: {source_field}")
            print(f"   New field: {new_field_name}")
            print(f"   Categories: {len(categories)}")
            print(f"   List name: {list_name}")
            
            # Step 1: Get current asset structure
            asset_url = f"{self.base_url}/api/v2/assets/{self.asset_id}/"
            response = requests.get(asset_url, headers=self.headers)
            response.raise_for_status()
            asset_data = response.json()
            
            content = asset_data.get('content', {})
            survey = content.get('survey', [])
            choices = content.get('choices', [])
            
            print(f"   Current survey questions: {len(survey)}")
            print(f"   Current choices: {len(choices)}")
            
            # Step 2: Check if field already exists
            field_exists = any(q.get('name') == new_field_name or q.get('$xpath') == new_field_name for q in survey)
            if field_exists:
                print(f"   ⚠ Field '{new_field_name}' already exists in asset. Skipping field creation.")
                print(f"   Will proceed to update submissions only.")
                return True
            
            # Step 3: Find the source field group
            # For Group_E/E1, we need to find Group_E and add field inside it
            source_parts = source_field.split('/')
            
            if len(source_parts) > 1:
                # Field is inside a group
                group_name = source_parts[0]
                field_name = source_parts[-1]
                
                # Find the group and field position
                in_group = False
                insert_index = -1
                
                for idx, question in enumerate(survey):
                    if question.get('type') == 'begin_group' and question.get('name') == group_name:
                        in_group = True
                    elif in_group and question.get('name') == field_name:
                        insert_index = idx + 1
                        break
                    elif in_group and question.get('type') == 'end_group':
                        insert_index = idx  # Insert before end_group
                        break
                
                if insert_index == -1:
                    print(f"   ✗ Could not find position for new field")
                    return False
            else:
                # Top-level field
                for idx, question in enumerate(survey):
                    if question.get('name') == source_field:
                        insert_index = idx + 1
                        break
                
                if insert_index == -1:
                    print(f"   ✗ Source field '{source_field}' not found")
                    return False
            
            # Step 4: Generate choices for categories
            new_choices = self.generate_choices_list(categories, list_name)
            
            # Step 5: Create new field
            # Use simple name without group prefix for the field itself
            simple_field_name = new_field_name.split('/')[-1] if '/' in new_field_name else new_field_name
            
            new_field = {
                "type": "select_one",
                "name": simple_field_name,
                "label": [f"AI Classification - {field_name if len(source_parts) > 1 else source_field}"],
                "select_from_list_name": list_name,
                "required": False,
                "appearance": "minimal"
            }
            
            # Insert new field
            survey.insert(insert_index, new_field)
            
            # Add choices to choices list (avoid duplicates)
            existing_list_names = set(c.get('list_name') for c in choices)
            if list_name not in existing_list_names:
                choices.extend(new_choices)
                print(f"   ✓ Added {len(new_choices)} choices to list '{list_name}'")
            else:
                print(f"   ⚠ Choice list '{list_name}' already exists")
            
            # Step 6: Update asset with new structure
            content['survey'] = survey
            content['choices'] = choices
            
            update_payload = {
                "content": content
            }
            
            print(f"   Updating Kobo asset...")
            response = requests.patch(
                asset_url,
                headers=self.headers,
                json=update_payload
            )
            response.raise_for_status()
            
            print(f"   ✓ Successfully added field '{simple_field_name}' to Kobo asset")
            print(f"   ✓ Field type: select_one with {len(categories)} options")
            return True
            
        except requests.exceptions.HTTPError as e:
            print(f"   ✗ HTTP Error: {e}")
            print(f"   Response: {e.response.text[:500]}")
            return False
        except Exception as e:
            print(f"   ✗ Error adding field to asset: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def update_submission_data(self, 
                                submission_id: int,
                                field_name: str,
                                category_code: int) -> bool:
        """
        Update single submission with classification code
        
        Args:
            submission_id: Submission ID
            field_name: Field name to update (simple name, not path)
            category_code: Category code (numeric)
        
        Returns:
            bool: True if successful
        """
        try:
            # Kobo API endpoint for updating submission
            # Use simple field name without group prefix
            simple_field_name = field_name.split('/')[-1] if '/' in field_name else field_name
            
            url = f"{self.base_url}/api/v2/assets/{self.asset_id}/data/{submission_id}/"
            
            # Kobo expects the field with group prefix in the path
            # But for Group_E/E1_coded, we use Group_E/E1_coded in the payload
            payload = {
                field_name: str(category_code)
            }
            
            response = requests.patch(
                url,
                headers=self.headers,
                json=payload
            )
            
            if response.status_code not in [200, 201, 204]:
                print(f"   Warning: Unexpected status {response.status_code} for submission {submission_id}")
                return False
            
            return True
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                # Submission not found, skip silently
                return False
            print(f"   ✗ HTTP Error updating submission {submission_id}: {e}")
            return False
        except Exception as e:
            print(f"   ✗ Error updating submission {submission_id}: {e}")
            return False
    
    def batch_update_submissions(self,
                                  classifications: Dict[int, str],
                                  field_name: str,
                                  categories: List[str]) -> Dict:
        """
        Batch update submissions with classification codes
        
        Args:
            classifications: Dict mapping submission_id to category name
            field_name: Field name to update
            categories: List of categories
        
        Returns:
            Dict with success/failure counts
        """
        category_codes = self.create_category_codes(categories)
        
        results = {
            'success': 0,
            'failed': 0,
            'total': len(classifications)
        }
        
        print(f"\nUpdating {results['total']} submissions in Kobo...")
        
        for idx, (submission_id, category) in enumerate(classifications.items(), 1):
            if category in category_codes:
                code = category_codes[category]
                success = self.update_submission_data(submission_id, field_name, code)
                
                if success:
                    results['success'] += 1
                else:
                    results['failed'] += 1
            else:
                print(f"Warning: Category '{category}' not found in category list")
                results['failed'] += 1
            
            # Progress indicator
            if idx % 50 == 0:
                print(f"   Progress: {idx}/{results['total']} ({results['success']} success, {results['failed']} failed)")
        
        print(f"\n✓ Update completed: {results['success']} success, {results['failed']} failed")
        return results


if __name__ == "__main__":
    # Test the uploader
    uploader = KoboUploader()
    
    # Example: Add field for E1 classification
    test_categories = [
        "Pilihan Pembayaran",
        "Sosialisasi dan Promosi",
        "Fasilitas Pelabuhan",
        "Kebersihan dan Kenyamanan",
        "Jam Keberangkatan",
        "Tarif dan Kuota",
        "Teknologi Pembayaran",
        "Kualitas Kapal",
        "Area Tunggu",
        "Other"
    ]
    
    print("Testing Kobo Uploader...")
    print("=" * 80)
    
    # Generate and display choices
    choices = uploader.generate_choices_list(test_categories, "e1_categories")
    print("\nGenerated Choices:")
    for choice in choices:
        print(f"   Code {choice['name']}: {choice['label'][0]}")
    
    print("\nTo add field to Kobo asset, call:")
    print("uploader.add_classification_field_to_asset('Group_E/E1', 'E1_coded', categories)")

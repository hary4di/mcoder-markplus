"""
Kobo API Client
Module untuk berinteraksi dengan Kobo Toolbox API
"""
import requests
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class KoboClient:
    """Client untuk Kobo Toolbox API"""
    
    def __init__(self):
        """Initialize Kobo client dengan credentials dari .env"""
        self.asset_id = os.getenv('KOBO_ASSET_ID')
        self.api_token = os.getenv('KOBO_API_TOKEN')
        self.base_url = os.getenv('KOBO_BASE_URL', 'https://kf.kobotoolbox.org')
        
        if not self.asset_id or not self.api_token:
            raise ValueError("KOBO_ASSET_ID dan KOBO_API_TOKEN harus diset di .env file")
        
        self.headers = {
            'Authorization': f'Token {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def get_asset_info(self) -> Dict:
        """
        Mendapatkan informasi asset (survey form)
        
        Returns:
            Dict: Asset information
        """
        url = f"{self.base_url}/api/v2/assets/{self.asset_id}/"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_submissions(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Mendapatkan semua submissions dari survey
        
        Args:
            limit: Maksimal jumlah submissions yang diambil (None = semua)
        
        Returns:
            List[Dict]: List of submissions
        """
        url = f"{self.base_url}/api/v2/assets/{self.asset_id}/data/"
        
        all_submissions = []
        next_url = url
        
        if limit:
            next_url += f"?limit={limit}"
        
        while next_url:
            response = requests.get(next_url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            results = data.get('results', [])
            all_submissions.extend(results)
            
            # Check if there's more data
            next_url = data.get('next')
            
            # If limit is set and we've reached it, stop
            if limit and len(all_submissions) >= limit:
                all_submissions = all_submissions[:limit]
                break
        
        return all_submissions
    
    def get_field_responses(self, field_name: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Mendapatkan responses untuk field tertentu
        
        Args:
            field_name: Nama field (e.g., 'E1')
            limit: Maksimal jumlah submissions yang diambil
        
        Returns:
            List[Dict]: List of {id, response} untuk field tersebut
        """
        submissions = self.get_submissions(limit=limit)
        
        field_responses = []
        for submission in submissions:
            response_value = submission.get(field_name)
            if response_value:  # Only include non-empty responses
                field_responses.append({
                    'submission_id': submission.get('_id'),
                    'response': response_value
                })
        
        return field_responses
    
    def get_survey_questions(self) -> List[Dict]:
        """
        Mendapatkan daftar semua pertanyaan dalam survey
        
        Returns:
            List[Dict]: List of questions dengan name, type, dan label
        """
        asset_info = self.get_asset_info()
        content = asset_info.get('content', {})
        survey = content.get('survey', [])
        
        questions = []
        for question in survey:
            q_name = question.get('name')
            q_type = question.get('type')
            q_label = question.get('label', 'N/A')
            
            # Handle label (could be list or string)
            if isinstance(q_label, list):
                q_label = q_label[0] if q_label else 'N/A'
            
            questions.append({
                'name': q_name,
                'type': q_type,
                'label': q_label
            })
        
        return questions


if __name__ == "__main__":
    # Test the client
    try:
        client = KoboClient()
        
        print("Testing Kobo API Client...")
        print("=" * 80)
        
        # Test 1: Get asset info
        print("\n1. Asset Information:")
        asset_info = client.get_asset_info()
        print(f"   Name: {asset_info.get('name')}")
        print(f"   Submissions: {asset_info.get('deployment__submission_count', 0)}")
        
        # Test 2: Get questions
        print("\n2. Survey Questions:")
        questions = client.get_survey_questions()
        for q in questions[:10]:  # Show first 10
            print(f"   - {q['name']}: {q['label']}")
        
        # Test 3: Get E1 responses (sample)
        print("\n3. Sample E1 Responses:")
        e1_responses = client.get_field_responses('E1', limit=5)
        for idx, item in enumerate(e1_responses, 1):
            print(f"   [{idx}] {item['response']}")
        
        print("\n✓ Kobo API Client working successfully!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")

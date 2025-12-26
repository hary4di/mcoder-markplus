"""
OpenAI Classifier
Module untuk klasifikasi text menggunakan OpenAI GPT-4o-mini
Supports PARALLEL PROCESSING untuk kecepatan maksimal
"""
import os
import json
import random
import time
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenAIClassifier:
    """Classifier untuk kategorisasi jawaban open-ended menggunakan OpenAI"""
    
    def __init__(self):
        """Initialize OpenAI client with settings from database or .env"""
        # Try to load from database first, fallback to .env
        try:
            from app.models import SystemSettings
            from app import app
            with app.app_context():
                api_key = SystemSettings.get_setting('openai_api_key') or os.getenv('OPENAI_API_KEY')
                model = SystemSettings.get_setting('openai_model') or 'gpt-4o-mini'
                invalid_patterns_str = SystemSettings.get_setting('invalid_patterns')
                invalid_category = SystemSettings.get_setting('invalid_category') or os.getenv('INVALID_RESPONSE_CATEGORY', 'Tidak Ada Jawaban')
                invalid_code = int(SystemSettings.get_setting('invalid_code') or os.getenv('INVALID_RESPONSE_CODE', '99'))
        except:
            # Fallback to .env if database not available
            api_key = os.getenv('OPENAI_API_KEY')
            model = 'gpt-4o-mini'
            invalid_patterns_str = None
            invalid_category = os.getenv('INVALID_RESPONSE_CATEGORY', 'Tidak Ada Jawaban')
            invalid_code = int(os.getenv('INVALID_RESPONSE_CODE', '99'))
        
        if not api_key or api_key == 'your_openai_api_key_here':
            raise ValueError("OPENAI_API_KEY harus diset di Admin Settings atau .env file")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_categories = int(os.getenv('MAX_CATEGORIES', '10'))
        self.sample_ratio = float(os.getenv('CATEGORY_SAMPLE_RATIO', '1.0'))
        self.max_sample_size = int(os.getenv('MAX_SAMPLE_SIZE', '500'))
        self.min_confidence = float(os.getenv('MIN_CONFIDENCE_THRESHOLD', '0.50'))
        self.enable_stratified = os.getenv('ENABLE_STRATIFIED_SAMPLING', 'true').lower() == 'true'
        self.invalid_category = invalid_category
        self.invalid_code = invalid_code
        
        # PARALLEL PROCESSING CONFIGURATION
        self.enable_parallel = os.getenv('ENABLE_PARALLEL_PROCESSING', 'true').lower() == 'true'
        self.max_workers = int(os.getenv('PARALLEL_MAX_WORKERS', '5'))  # 5 concurrent workers
        self.rate_limit_delay = float(os.getenv('RATE_LIMIT_DELAY', '0.1'))  # 100ms between requests
        
        # Thread-safe counter for progress tracking
        self._progress_lock = Lock()
        self._processed_count = 0
        
        # Multi-label configuration
        self.enable_multi_label = os.getenv('ENABLE_MULTI_LABEL', 'true').lower() == 'true'
        self.min_category_confidence = float(os.getenv('MIN_CATEGORY_CONFIDENCE', '0.6'))
        self.max_categories_per_response = int(os.getenv('MAX_CATEGORIES_PER_RESPONSE', '3'))
        self.single_category_threshold = float(os.getenv('SINGLE_CATEGORY_THRESHOLD', '0.85'))
        
        # Load invalid responses from database or use defaults
        if invalid_patterns_str:
            self.invalid_responses = [p.strip().lower() for p in invalid_patterns_str.split('\n') if p.strip()]
        else:
            # Default invalid responses
            self.invalid_responses = [
                'ta', 't.a', 'tidak ada', 'tdk ada', 'tdkada', 'tidakada',
                'tidak tahu', 'tdk tahu', 'tdktahu', 'tidaktahu',
                'tidak tau', 'tdk tau', 'tdktau', 'tidaktau',
                'n/a', 'na', 'none', '-', '--', '---',
                'tidak', 'tdk', 'kosong', 'empty',
                'tidak ada jawaban', 'tidak ada saran',
                'belum ada', 'belum', 'nothing'
            ]
    
    def is_valid_response(self, response: str) -> bool:
        """
        Check if response is valid (not TA, tidak tahu, etc.)
        
        Args:
            response: Text response to validate
        
        Returns:
            bool: True if valid, False if invalid
        """
        if not response or not isinstance(response, str):
            return False
        
        # Normalize response
        response_lower = response.lower().strip()
        
        if len(response_lower) < 3:
            return False
        
        # Check against invalid responses list
        for invalid in self.invalid_responses:
            if response_lower == invalid or response_lower.startswith(invalid + ' '):
                return False
        
        return True
    
    def filter_valid_responses(self, responses: List[str]) -> List[str]:
        """
        Filter out invalid responses BEFORE sending to OpenAI
        This saves API costs and improves category quality
        
        Args:
            responses: List of all responses
        
        Returns:
            List[str]: List of valid responses only (excludes TA, tidak ada, etc)
        """
        return [r for r in responses if self.is_valid_response(r)]
    
    def _stratified_sample(self, responses: List[str], sample_size: int) -> List[str]:
        """
        Stratified sampling berdasarkan panjang response untuk lebih representatif
        
        Args:
            responses: List of responses
            sample_size: Target sample size
        
        Returns:
            List[str]: Stratified sample
        """
        if len(responses) <= sample_size:
            return responses
        
        # Define strata berdasarkan word count
        short = []    # 1-5 words
        medium = []   # 6-15 words
        long = []     # 16+ words
        
        for response in responses:
            word_count = len(response.split())
            if word_count <= 5:
                short.append(response)
            elif word_count <= 15:
                medium.append(response)
            else:
                long.append(response)
        
        total = len(short) + len(medium) + len(long)
        
        # Proportional sampling dari setiap stratum
        n_short = int(len(short) / total * sample_size)
        n_medium = int(len(medium) / total * sample_size)
        n_long = sample_size - n_short - n_medium  # Sisa untuk long
        
        # Sample dari setiap stratum
        sampled = []
        if short and n_short > 0:
            sampled.extend(random.sample(short, min(n_short, len(short))))
        if medium and n_medium > 0:
            sampled.extend(random.sample(medium, min(n_medium, len(medium))))
        if long and n_long > 0:
            sampled.extend(random.sample(long, min(n_long, len(long))))
        
        # Jika masih kurang (karena rounding), ambil dari pool
        if len(sampled) < sample_size:
            remaining = [r for r in responses if r not in sampled]
            needed = sample_size - len(sampled)
            sampled.extend(random.sample(remaining, min(needed, len(remaining))))
        
        print(f"   Stratified sampling breakdown:")
        print(f"      Short (1-5 words): {len(short)} responses → {min(n_short, len(short))} sampled")
        print(f"      Medium (6-15 words): {len(medium)} responses → {min(n_medium, len(medium))} sampled")
        print(f"      Long (16+ words): {len(long)} responses → {min(n_long, len(long))} sampled")
        
        return sampled
    
    def generate_categories(self, responses: List[str], question_text: str = None, max_categories: int = None) -> List[str]:
        """
        Phase 1: Generate categories dinamis berdasarkan sample responses dengan question context
        
        Args:
            responses: List of text responses
            question_text: Question text for context
            max_categories: Maximum categories (None = unlimited)
        
        Returns:
            List[str]: List of category names
        """
        # Filter valid responses first
        valid_responses = self.filter_valid_responses(responses)
        
        if not valid_responses:
            print("Warning: No valid responses found!")
            return ["Other"]
        
        # Calculate sample size (100% of valid responses with max limit)
        total_valid = len(valid_responses)
        sample_size = int(total_valid * self.sample_ratio)
        
        # Minimum 50, maximum from config (default 500)
        sample_size = max(50, min(sample_size, self.max_sample_size))
        
        # Sampling strategy
        if sample_size >= total_valid:
            # Use all data if <= max_sample_size
            sample_responses = valid_responses
            print(f"Category generation: Using ALL {len(sample_responses)} valid responses (100%)")
        else:
            # Use stratified or random sampling
            if self.enable_stratified and total_valid > 500:
                sample_responses = self._stratified_sample(valid_responses, sample_size)
                print(f"Category generation: Using stratified sample of {len(sample_responses)} from {total_valid} valid responses ({len(sample_responses)/total_valid*100:.1f}%)")
            else:
                sample_responses = random.sample(valid_responses, sample_size)
                print(f"Category generation: Using random sample of {len(sample_responses)} from {total_valid} valid responses ({len(sample_responses)/total_valid*100:.1f}%)")
        
        responses_text = "\n".join([f"{i+1}. {r}" for i, r in enumerate(sample_responses)])
        
        # Determine max categories instruction
        if max_categories is None:
            max_cat_instruction = "Buat kategori sebanyak yang diperlukan untuk mencakup semua tema yang muncul (tidak ada batasan jumlah)"
        else:
            max_cat_instruction = f"Buat maksimal {max_categories} kategori yang mencakup sebagian besar jawaban"
        
        # Add question context if provided
        question_context = ""
        if question_text:
            question_context = f"""\n\nKONTEKS PERTANYAAN:
"{question_text}"

Klasifikasi harus mempertimbangkan konteks pertanyaan di atas. Kategori harus relevan dengan apa yang ditanyakan."""
        
        prompt = f"""Kamu adalah ahli analisis data survei. Tugas kamu adalah menganalisis jawaban-jawaban responden dan membuat kategori-kategori yang tepat.{question_context}

Berikut adalah {len(sample_responses)} jawaban responden:

{responses_text}

Instruksi:
1. Analisis semua jawaban di atas secara menyeluruh
2. Identifikasi tema-tema utama dan pola yang muncul
3. {max_cat_instruction}
4. Kategori harus:
   - Spesifik dan jelas
   - Relevan dengan konteks pertanyaan
   - Mutually exclusive (tidak overlap)
   - Comprehensive (mencakup mayoritas jawaban)
5. Gunakan bahasa Indonesia untuk nama kategori
6. WAJIB ada kategori "Other" untuk jawaban yang tidak masuk kategori lain

Format output (JSON):
{{
    "categories": [
        "Nama Kategori 1",
        "Nama Kategori 2",
        ...
        "Other"
    ]
}}

PENTING: Hanya output JSON, tidak ada text tambahan."""

        try:
            print(f"[OPENAI] Calling OpenAI API for category generation...", flush=True)
            print(f"[OPENAI] Sample size: {len(sample_responses)}, Model: {self.model}", flush=True)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Kamu adalah ahli analisis data survei yang memberikan output dalam format JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            print(f"[OPENAI] Category generation API call completed", flush=True)
            
            result = json.loads(response.choices[0].message.content)
            categories = result.get('categories', [])
            
            print(f"[OPENAI] Received {len(categories)} categories from API", flush=True)
            
            # Ensure "Other" is included
            if "Other" not in categories:
                categories.append("Other")
            
            # Use all categories from OpenAI (no artificial limit)
            return categories
            
        except Exception as e:
            print(f"Error generating categories: {e}")
            # Fallback categories
            return [
                "Peningkatan Fasilitas",
                "Peningkatan Layanan",
                "Infrastruktur",
                "Harga/Tarif",
                "Kebersihan",
                "Keamanan",
                "Jadwal/Frekuensi",
                "Kenyamanan",
                "Teknologi/Digitalisasi",
                "Other"
            ]
    
    def classify_responses_batch(self, responses: List[str], categories: List[str], question_text: str = None):
        """
        Phase 2: Classify MULTIPLE responses in one API call (MUCH FASTER)
        Supports MULTI-LABEL classification (one response → multiple categories)
        
        Args:
            responses: List of responses to classify (max 10 per batch)
            categories: List of available categories
            question_text: Question text for context
        
        Returns:
            List: Each item is a list of (category, confidence) tuples
                  Single-label: [(category, confidence)]
                  Multi-label: [(cat1, conf1), (cat2, conf2), ...]
        """
        if not responses:
            return []
        
        categories_text = "\n".join([f"- {cat}" for cat in categories])
        
        # Add question context if provided
        question_context = ""
        if question_text:
            question_context = f"\n\nKONTEKS PERTANYAAN: \"{question_text}\"\n"
        
        # Format responses for batch
        responses_text = "\n".join([f"{idx+1}. \"{resp}\"" for idx, resp in enumerate(responses)])
        
        # Build prompt based on multi-label setting
        # CRITICAL FIX: Generate examples dynamically based on ACTUAL categories
        # to avoid AI confusion with mismatched category names
        
        # Get first 5 categories (excluding "Other") for concrete examples
        example_cats = [c for c in categories if c.lower() != 'other'][:5]
        
        # Try to load custom prompts from database, fallback to defaults
        try:
            from app.models import SystemSettings
            
            if self.enable_multi_label:
                # Load multi-label prompt template
                prompt_template = SystemSettings.get_setting('prompt_multi_label', None)
                if not prompt_template:
                    # Default multi-label prompt WITH DYNAMIC EXAMPLES
                    prompt_template = """Instruksi MULTI-LABEL CLASSIFICATION:

SANGAT PENTING: Jawaban responden BISA mengandung MULTIPLE tema sekaligus!

Analisis SETIAP jawaban dengan cermat:
1. Identifikasi SEMUA tema/topik yang disebutkan dalam jawaban
2. Jika jawaban menyebutkan 2+ tema berbeda, WAJIB assign ke SEMUA kategori yang relevan
3. Berikan confidence score (0.0-1.0) untuk SETIAP kategori yang terdeteksi
4. Hanya include kategori dengan confidence ≥ {min_category_confidence}
5. Maksimal {max_categories_per_response} kategori per jawaban
6. EXCEPTION: Jika ada 1 kategori dengan confidence ≥ {single_category_threshold} (very dominant), gunakan HANYA kategori tersebut
7. Jika tidak ada yang cocok → "Other"

IMPORTANT: Match jawaban dengan kategori yang tersedia di atas! Lihat KATA KUNCI dalam jawaban yang cocok dengan nama kategori.

CONTOH MATCHING (gunakan kategori yang tersedia):
{examples}

Format output (JSON):
{{
  "classifications": [
    {{
      "response_number": 1,
      "categories": [
        {{"category": "KategoriYangSesuai", "confidence": 0.85}}
      ]
    }}
  ]
}}"""
                
                # Generate dynamic examples using actual categories
                examples_list = []
                if len(example_cats) >= 1:
                    examples_list.append(f'- Jika jawaban menyebut "{example_cats[0].lower()}" → {example_cats[0]}')
                if len(example_cats) >= 2:
                    examples_list.append(f'- Jika jawaban menyebut "{example_cats[1].lower()}" → {example_cats[1]}')
                if len(example_cats) >= 3:
                    examples_list.append(f'- Jika jawaban menyebut "{example_cats[0].lower()}" DAN "{example_cats[2].lower()}" → [{example_cats[0]}, {example_cats[2]}]')
                examples_list.append('- Jika tidak jelas atau tidak cocok → Other')
                examples_text = "\n".join(examples_list)
                
                # Replace template variables
                instruction = prompt_template.format(
                    min_category_confidence=self.min_category_confidence,
                    max_categories_per_response=self.max_categories_per_response,
                    single_category_threshold=self.single_category_threshold,
                    examples=examples_text
                )
            else:
                # Load single-label prompt template
                prompt_template = SystemSettings.get_setting('prompt_single_label', None)
                if not prompt_template:
                    # Default single-label prompt WITH DYNAMIC EXAMPLES
                    prompt_template = """Instruksi SINGLE-LABEL CLASSIFICATION:

Pilih SATU kategori yang PALING relevan untuk setiap jawaban:
1. Analisis tema utama dari jawaban responden
2. Pilih kategori yang paling tepat menggambarkan maksud utama jawaban
3. Berikan confidence score (0.0-1.0)
4. Hanya assign jika confidence ≥ {min_category_confidence}
5. Jika tidak ada yang cocok → "Other"

IMPORTANT: Match jawaban dengan kategori yang tersedia di atas! Lihat KATA KUNCI dalam jawaban yang cocok dengan nama kategori.

CONTOH MATCHING (gunakan kategori yang tersedia):
{examples}

Format output (JSON):
{{
  "classifications": [
    {{"response_number": 1, "category": "KategoriYangSesuai", "confidence": 0.95}},
    {{"response_number": 2, "category": "Other", "confidence": 0.60}}
  ]
}}"""
                
                # Generate dynamic examples using actual categories
                examples_list = []
                if len(example_cats) >= 1:
                    examples_list.append(f'- Jika jawaban tentang "{example_cats[0].lower()}" → {example_cats[0]}')
                if len(example_cats) >= 2:
                    examples_list.append(f'- Jika jawaban tentang "{example_cats[1].lower()}" → {example_cats[1]}')
                if len(example_cats) >= 3:
                    examples_list.append(f'- Jika jawaban tentang "{example_cats[2].lower()}" → {example_cats[2]}')
                examples_list.append('- Jika tidak jelas atau tidak cocok → Other')
                examples_text = "\n".join(examples_list)
                
                # Replace template variables
                instruction = prompt_template.format(
                    min_category_confidence=self.min_category_confidence,
                    examples=examples_text
                )
        except Exception as e:
            # Fallback if database not available (e.g., running standalone scripts)
            print(f"[WARNING] Could not load custom prompts from database: {e}")
            print("[WARNING] Using default hardcoded prompts")
            
            # Generate dynamic examples using actual categories
            examples_list = []
            if len(example_cats) >= 1:
                examples_list.append(f'- Jika jawaban menyebut "{example_cats[0].lower()}" → {example_cats[0]}')
            if len(example_cats) >= 2:
                examples_list.append(f'- Jika jawaban menyebut "{example_cats[1].lower()}" → {example_cats[1]}')
            if len(example_cats) >= 3:
                examples_list.append(f'- Jika jawaban menyebut "{example_cats[0].lower()}" DAN "{example_cats[2].lower()}" → [{example_cats[0]}, {example_cats[2]}]')
            examples_list.append('- Jika tidak jelas atau tidak cocok → Other')
            examples_text = "\n".join(examples_list)
            
            if self.enable_multi_label:
                instruction = f"""Instruksi MULTI-LABEL CLASSIFICATION:

SANGAT PENTING: Jawaban responden BISA mengandung MULTIPLE tema sekaligus!

Analisis SETIAP jawaban dengan cermat:
1. Identifikasi SEMUA tema/topik yang disebutkan dalam jawaban
2. Jika jawaban menyebutkan 2+ tema berbeda (misal: "harga mahal DAN pelayanan buruk"), WAJIB assign ke SEMUA kategori yang relevan
3. Berikan confidence score (0.0-1.0) untuk SETIAP kategori yang terdeteksi
4. Hanya include kategori dengan confidence ≥ {self.min_category_confidence}
5. Maksimal {self.max_categories_per_response} kategori per jawaban
6. EXCEPTION: Jika ada 1 kategori dengan confidence ≥ {self.single_category_threshold} (very dominant), gunakan HANYA kategori tersebut
7. Jika tidak ada yang cocok → "Other"

IMPORTANT: Match jawaban dengan kategori yang tersedia di atas! Lihat KATA KUNCI dalam jawaban yang cocok dengan nama kategori.

CONTOH MATCHING (gunakan kategori yang tersedia):
{examples_text}

Format output (JSON):
{{
  "classifications": [
    {{
      "response_number": 1,
      "categories": [
        {{"category": "KategoriYangSesuai", "confidence": 0.85}}
      ]
    }}
  ]
}}"""
            else:
                instruction = f"""Instruksi SINGLE-LABEL CLASSIFICATION:

Pilih SATU kategori yang PALING relevan untuk setiap jawaban:
1. Analisis tema utama dari jawaban responden
2. Pilih kategori yang paling tepat menggambarkan maksud utama jawaban
3. Berikan confidence score (0.0-1.0)
4. Hanya assign jika confidence ≥ {self.min_confidence}
5. Jika tidak ada yang cocok → "Other"

IMPORTANT: Match jawaban dengan kategori yang tersedia di atas! Lihat KATA KUNCI dalam jawaban yang cocok dengan nama kategori.

CONTOH MATCHING (gunakan kategori yang tersedia):
{examples_text}

Format output (JSON):
{{
  "classifications": [
    {{"response_number": 1, "category": "KategoriYangSesuai", "confidence": 0.95}},
    {{"response_number": 2, "category": "Other", "confidence": 0.60}}
  ]
}}"""
        
        prompt = f"""Tugas kamu adalah mengklasifikasikan MULTIPLE jawaban responden ke dalam kategori yang sesuai.{question_context}

Kategori yang Tersedia:
{categories_text}

Jawaban Responden ({len(responses)} responses):
{responses_text}

{instruction}"""
        
        try:
            print(f"[OPENAI] Batch classifying {len(responses)} responses (multi-label: {self.enable_multi_label})...", flush=True)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Kamu adalah expert data analyst untuk survey data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            classifications = result.get('classifications', [])
            
            # Process results based on format
            results = []
            for item in classifications:
                if self.enable_multi_label and 'categories' in item:
                    # Multi-label: List of categories
                    cats = item['categories']
                    
                    # Filter by confidence threshold
                    filtered = [(c['category'], float(c['confidence'])) 
                               for c in cats 
                               if float(c['confidence']) >= self.min_category_confidence]
                    
                    # Check for single clear winner
                    if filtered and filtered[0][1] >= self.single_category_threshold:
                        results.append([(filtered[0][0], filtered[0][1])])
                    else:
                        # Limit max categories and sort by confidence
                        filtered = sorted(filtered, key=lambda x: x[1], reverse=True)
                        filtered = filtered[:self.max_categories_per_response]
                        results.append(filtered if filtered else [('Other', 0.3)])
                else:
                    # Single-label: One category
                    category = item.get('category', 'Other')
                    confidence = float(item.get('confidence', 0.5))
                    results.append([(category, confidence)])
            
            print(f"[OPENAI] Batch completed: {len(results)} classifications", flush=True)
            return results
            
        except Exception as e:
            print(f"Error in batch classification: {e}")
            # Fallback: return "Other" for all
            return [[("Other", 0.5)] for _ in responses]
    
    def classify_response(self, response: str, categories: List[str], question_text: str = None) -> Tuple[str, float]:
        """
        Phase 2: Klasifikasi satu response ke kategori yang sesuai
        
        Args:
            response: Text response to classify
            categories: List of available categories
            question_text: Question text for context
        
        Returns:
            Tuple[str, float]: (category, confidence_score)
        """
        categories_text = "\n".join([f"- {cat}" for cat in categories])
        
        # Add question context if provided
        question_context = ""
        if question_text:
            question_context = f"\n\nKONTEKS PERTANYAAN: \"{question_text}\"\n"
        
        prompt = f"""Tugas kamu adalah mengklasifikasikan jawaban responden ke dalam salah satu kategori yang tersedia.{question_context}

Jawaban Responden:
"{response}"

Kategori yang Tersedia:
{categories_text}

Instruksi:
1. Baca dan pahami jawaban responden
2. Pilih SATU kategori yang paling sesuai
3. Jika jawaban tidak jelas, ambiguous, atau tidak masuk kategori manapun, pilih "Other"
4. Berikan confidence score (0.0 - 1.0)

Format output (JSON):
{{
    "category": "Nama Kategori",
    "confidence": 0.95,
    "reasoning": "Penjelasan singkat kenapa memilih kategori ini"
}}

PENTING: Hanya output JSON, tidak ada text tambahan."""

        try:
            response_obj = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Kamu adalah classifier yang akurat dan memberikan output dalam format JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response_obj.choices[0].message.content)
            category = result.get('category', 'Other')
            confidence = result.get('confidence', 0.5)
            
            # Ensure category is valid
            if category not in categories:
                category = "Other"
                confidence = 0.5
            
            return category, confidence
            
        except Exception as e:
            print(f"Error classifying response: {e}")
            return "Other", 0.0
    
    def analyze_outliers(self, outliers: List[Dict], question_text: str = None) -> List[str]:
        """
        Analyze outliers to potentially create new categories
        
        Args:
            outliers: List of outlier responses with low confidence
            question_text: Question text for context
        
        Returns:
            List[str]: List of new category names (if any)
        """
        if not outliers or len(outliers) < int(os.getenv('MIN_OUTLIERS_FOR_NEW_CATEGORY', '10')):
            return []
        
        outlier_texts = [o['response'] for o in outliers]
        responses_text = "\n".join([f"{i+1}. {r}" for i, r in enumerate(outlier_texts)])
        
        question_context = ""
        if question_text:
            question_context = f"\n\nKONTEKS PERTANYAAN: \"{question_text}\"\n"
        
        max_new = int(os.getenv('MAX_NEW_CATEGORIES', '3'))
        
        prompt = f"""Kamu adalah ahli analisis data survei. {len(outlier_texts)} jawaban berikut TIDAK cocok dengan kategori existing (confidence rendah).{question_context}

Jawaban-jawaban tersebut:
{responses_text}

Analisis:
1. Apakah jawaban-jawaban ini membentuk tema/pola yang jelas?
2. Jika YA, buat maksimal {max_new} kategori BARU yang spesifik untuk jawaban ini
3. Jika TIDAK (terlalu random/diverse), return empty array
4. Kategori baru harus:
   - Spesifik dan jelas
   - Berbeda dari kategori existing
   - Mencakup minimal 5 jawaban dari list di atas

Format output (JSON):
{{
    "new_categories": ["Nama Kategori Baru 1", "Nama Kategori Baru 2"],
    "reasoning": "Alasan mengapa kategori ini dibuat"
}}

Jika tidak perlu kategori baru, return:
{{
    "new_categories": [],
    "reasoning": "Jawaban terlalu diverse/random"
}}

PENTING: Hanya output JSON, tidak ada text tambahan."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Kamu adalah ahli analisis data survei yang memberikan output dalam format JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            new_categories = result.get('new_categories', [])
            reasoning = result.get('reasoning', '')
            
            if new_categories:
                print(f"\n   Outlier analysis: Found {len(new_categories)} new categories")
                print(f"   Reasoning: {reasoning}")
                for idx, cat in enumerate(new_categories, 1):
                    print(f"      {idx}. {cat}")
            else:
                print(f"\n   Outlier analysis: No new categories needed")
                print(f"   Reasoning: {reasoning}")
            
            return new_categories
            
        except Exception as e:
            print(f"\n   Error analyzing outliers: {e}")
            return []
    
    def classify_batch(self, responses: List[str], categories: List[str], 
                       batch_size: int = 10) -> List[Dict]:
        """
        Klasifikasi multiple responses dalam batch
        
        Args:
            responses: List of text responses
            categories: List of available categories
            batch_size: Number of responses to process in one API call
        
        Returns:
            List[Dict]: List of classification results
        """
        results = []
        
        for i in range(0, len(responses), batch_size):
            batch = responses[i:i+batch_size]
            
            for response in batch:
                category, confidence = self.classify_response(response, categories)
                results.append({
                    'response': response,
                    'category': category,
                    'confidence': confidence
                })
                
                # Progress indicator
                if (len(results) % 10) == 0:
                    print(f"   Processed {len(results)}/{len(responses)} responses...")
        
        return results


if __name__ == "__main__":
    # Test the classifier
    try:
        classifier = OpenAIClassifier()
        
        print("Testing OpenAI Classifier...")
        print("=" * 80)
        
        # Sample responses for testing
        sample_responses = [
            "Perlu ditambah fasilitas toilet yang lebih bersih",
            "Harga tiket terlalu mahal, perlu diturunkan",
            "Jadwal keberangkatan kapal perlu lebih sering",
            "Ruang tunggu kurang nyaman, perlu AC",
            "Sistem pembelian tiket online perlu diperbaiki"
        ]
        
        print("\n1. Generating Categories...")
        categories = classifier.generate_categories(sample_responses)
        print(f"   Generated {len(categories)} categories:")
        for cat in categories:
            print(f"   - {cat}")
        
        print("\n2. Classifying Sample Responses...")
        for idx, response in enumerate(sample_responses, 1):
            category, confidence = classifier.classify_response(response, categories)
            print(f"   [{idx}] {response}")
            print(f"       → Category: {category} (Confidence: {confidence:.2f})")
        
        print("\n✓ OpenAI Classifier working successfully!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        if "OPENAI_API_KEY" in str(e):
            print("\nCatatan: Pastikan sudah mengisi OPENAI_API_KEY di file .env")

"""
Quick test for multi-label classification
"""
from openai_classifier import OpenAIClassifier

# Initialize classifier
classifier = OpenAIClassifier()

# Test responses
test_responses = [
    "Pilihan pembayaran dan Penambahan Jam Keberangkatan",
    "saluran pembayaran , Penambahan Jam Keberangkatan",
    "Disediakan coffe shop dan Informasi perjalanan harus jelas"
]

# Categories (from actual classification)
categories = [
    "Pilihan Pembayaran",
    "Sosialisasi dan Promosi",
    "Fasilitas dan Kenyamanan",
    "Jadwal dan Keberangkatan",
    "Kualitas Kapal",
    "Informasi Perjalanan",
    "Perbaikan Aplikasi",
    "Layanan Pelanggan",
    "Lainnya",
    "Other"
]

print("=" * 80)
print("MULTI-LABEL CLASSIFICATION TEST")
print("=" * 80)
print(f"\nSettings:")
print(f"  ENABLE_MULTI_LABEL: {classifier.enable_multi_label}")
print(f"  MIN_CATEGORY_CONFIDENCE: {classifier.min_category_confidence}")
print(f"  MAX_CATEGORIES_PER_RESPONSE: {classifier.max_categories_per_response}")
print(f"  SINGLE_CATEGORY_THRESHOLD: {classifier.single_category_threshold}")

print(f"\n\nTesting {len(test_responses)} responses...")
print("=" * 80)

results = classifier.classify_responses_batch(
    test_responses,
    categories,
    question_text="Pengembangan apa yang diharapkan di Ferizy"
)

for i, (response, result) in enumerate(zip(test_responses, results), 1):
    print(f"\n[{i}] Response: \"{response}\"")
    print(f"    AI Result: {result}")
    print(f"    Type: {type(result)}")
    print(f"    Number of categories: {len(result) if isinstance(result, list) else 'N/A'}")
    
    if isinstance(result, list):
        for cat, conf in result:
            print(f"      → {cat}: {conf:.2f}")

print("\n" + "=" * 80)
print("TEST COMPLETED")
print("=" * 80)

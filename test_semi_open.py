"""
Test script untuk Semi Open-Ended processing
"""
import os
from dotenv import load_dotenv
from semi_open_detector import SemiOpenDetector
from semi_open_processor import SemiOpenProcessor
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_detection():
    """Test detection of semi open-ended pairs"""
    print("\n" + "="*70)
    print("TEST 1: DETECTION OF SEMI OPEN-ENDED PAIRS")
    print("="*70 + "\n")
    
    # Example file paths - adjust these
    kobo_system_path = "files/uploads/kobo_system_example.xlsx"
    
    if not os.path.exists(kobo_system_path):
        print(f"❌ File not found: {kobo_system_path}")
        print("📝 Please provide a kobo_system file with semi open-ended questions")
        return None
    
    # Initialize detector
    detector = SemiOpenDetector(kobo_system_path)
    detector.load_sheets()
    
    # Detect lainnya options
    print("🔍 Step 1: Detecting 'Lainnya' options in choices...")
    lainnya_map = detector.detect_lainnya_in_choices()
    print(f"   Found: {lainnya_map}\n")
    
    # Detect pairs
    print("🔍 Step 2: Detecting semi open-ended pairs...")
    pairs = detector.detect_semi_open_pairs()
    
    # Show summary
    print("\n" + detector.get_summary())
    
    return pairs


def test_processing(pairs):
    """Test processing of semi open-ended pairs"""
    print("\n" + "="*70)
    print("TEST 2: PROCESSING SEMI OPEN-ENDED")
    print("="*70 + "\n")
    
    if not pairs:
        print("❌ No pairs to process")
        return
    
    # Load environment variables
    load_dotenv()
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_api_key or openai_api_key == 'your_openai_api_key_here':
        print("❌ OpenAI API key not configured in .env file")
        return
    
    # Example file paths - adjust these
    kobo_system_path = "files/uploads/kobo_system_example.xlsx"
    raw_data_path = "files/uploads/raw_data_example.xlsx"
    
    if not os.path.exists(raw_data_path):
        print(f"❌ File not found: {raw_data_path}")
        return
    
    # Initialize processor
    processor = SemiOpenProcessor(
        kobo_system_path=kobo_system_path,
        raw_data_path=raw_data_path,
        openai_api_key=openai_api_key
    )
    
    # Load data
    print("📂 Loading data files...")
    processor.load_data()
    
    # Process first pair (for testing)
    pair = pairs[0]
    print(f"\n🔄 Processing: {pair['select_var']} + {pair['text_var']}")
    
    try:
        result = processor.process_semi_open_pair(pair)
        
        if result['success']:
            print("\n✅ Processing successful!")
            print(f"\n📊 Statistics:")
            for key, value in result['stats'].items():
                print(f"   {key}: {value}")
            
            # Save results
            output_path = "files/output/semi_open_result.xlsx"
            os.makedirs("files/output", exist_ok=True)
            
            processor.save_results(result, output_path)
            print(f"\n💾 Results saved to: {output_path}")
            
            # Show sample merged data
            print(f"\n📋 Sample merged data:")
            merged_var = result['merged_var']
            merged_label = f"{result['select_var']}_merged_label"
            
            sample = result['merged_df'][[result['select_var'], result['text_var'], 
                                         merged_var, merged_label]].head(10)
            print(sample.to_string(index=False))
            
        else:
            print(f"\n❌ Processing failed: {result.get('message')}")
            
    except Exception as e:
        print(f"\n❌ Error during processing: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Main test function"""
    print("\n" + "🧪 SEMI OPEN-ENDED TEST SUITE".center(70, "="))
    
    # Test 1: Detection
    pairs = test_detection()
    
    if not pairs:
        print("\n⚠️  No semi open-ended pairs detected. Test suite stopped.")
        return
    
    # Ask user if want to continue with processing
    print("\n" + "="*70)
    response = input("Continue with processing test? (y/n): ")
    
    if response.lower() == 'y':
        # Test 2: Processing
        test_processing(pairs)
    else:
        print("\n✅ Test suite completed (detection only)")


if __name__ == "__main__":
    main()

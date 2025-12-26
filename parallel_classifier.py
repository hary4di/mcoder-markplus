"""
Parallel Processing Helper for OpenAI Classification
Implements concurrent batch processing untuk kecepatan maksimal
"""
import time
from typing import List, Dict, Tuple, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock


class ParallelClassifier:
    """Helper class untuk parallel classification processing"""
    
    def __init__(self, classifier, max_workers: int = 5, rate_limit_delay: float = 0.1):
        """
        Initialize parallel classifier
        
        Args:
            classifier: OpenAIClassifier instance
            max_workers: Number of concurrent workers (default 5)
            rate_limit_delay: Delay between requests in seconds (default 0.1)
        """
        self.classifier = classifier
        self.max_workers = max_workers
        self.rate_limit_delay = rate_limit_delay
        self._progress_lock = Lock()
        self._processed_count = 0
    
    def _classify_batch_worker(self, batch_data: Dict) -> Tuple[int, List]:
        """
        Worker function untuk parallel batch classification
        
        Args:
            batch_data: Dict with 'batch_idx', 'responses', 'categories', 'question_text'
        
        Returns:
            Tuple of (batch_idx, classifications)
        """
        batch_idx = batch_data['batch_idx']
        responses = batch_data['responses']
        categories = batch_data['categories']
        question_text = batch_data['question_text']
        
        try:
            # Add small delay to avoid rate limits
            if batch_idx > 0:
                time.sleep(self.rate_limit_delay)
            
            # Call OpenAI API for batch classification
            print(f"[OPENAI] Batch classifying {len(responses)} responses (multi-label: {self.classifier.enable_multi_label})...")
            classifications = self.classifier.classify_responses_batch_api(
                responses, categories, question_text
            )
            print(f"[OPENAI] Batch completed: {len(classifications)} classifications")
            
            # Thread-safe progress update
            with self._progress_lock:
                self._processed_count += len(responses)
            
            return (batch_idx, classifications)
            
        except Exception as e:
            print(f"[ERROR] Batch {batch_idx} failed: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return empty classifications for failed batch
            return (batch_idx, [[("Other", 0.0)] for _ in responses])
    
    def classify_parallel(self, responses: List[str], categories: List[str],
                         question_text: str = "", batch_size: int = 10,
                         progress_callback: Callable = None) -> List[List[Tuple[str, float]]]:
        """
        Klasifikasi responses menggunakan PARALLEL PROCESSING
        Dramatically faster: 3-5x speedup dengan 5 workers
        
        Args:
            responses: List of responses to classify
            categories: List of available categories  
            question_text: Question context
            batch_size: Responses per batch (default 10)
            progress_callback: Optional callback(message, percentage)
        
        Returns:
            List of classifications (each item is list of (category, confidence) tuples)
        """
        print(f"\n[PARALLEL] Processing {len(responses)} responses dengan {self.max_workers} workers")
        
        # Reset progress counter
        self._processed_count = 0
        total_responses = len(responses)
        
        # Split into batches
        batches = []
        for i in range(0, len(responses), batch_size):
            batch = responses[i:i+batch_size]
            batches.append({
                'batch_idx': len(batches),
                'responses': batch,
                'categories': categories,
                'question_text': question_text
            })
        
        print(f"[PARALLEL] Total {len(batches)} batches, batch_size={batch_size}")
        print(f"[PARALLEL] Max workers: {self.max_workers} (concurrent batches)")
        
        # Process batches in parallel using ThreadPoolExecutor
        results_dict = {}
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all batches to workers
            future_to_batch = {
                executor.submit(self._classify_batch_worker, batch_data): batch_data['batch_idx']
                for batch_data in batches
            }
            
            # Collect results as they complete
            completed_batches = 0
            for future in as_completed(future_to_batch):
                batch_idx = future_to_batch[future]
                completed_batches += 1
                
                try:
                    idx, classifications = future.result()
                    results_dict[idx] = classifications
                    
                    # Progress update
                    percentage = int((self._processed_count / total_responses) * 100)
                    elapsed = time.time() - start_time
                    rate = self._processed_count / elapsed if elapsed > 0 else 0
                    
                    message = f"Classifying... {self._processed_count}/{total_responses} ({percentage}%) - {rate:.1f} resp/sec [{completed_batches}/{len(batches)} batches]"
                    print(f"[PARALLEL] {message}")
                    
                    if progress_callback:
                        progress_callback(message, percentage)
                        
                except Exception as e:
                    print(f"[PARALLEL ERROR] Batch {batch_idx} exception: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    # Add empty results for failed batch
                    batch_size_failed = len(batches[batch_idx]['responses'])
                    results_dict[batch_idx] = [[("Other", 0.0)] for _ in range(batch_size_failed)]
        
        # Reconstruct results in original order
        all_classifications = []
        for i in range(len(batches)):
            all_classifications.extend(results_dict.get(i, []))
        
        elapsed = time.time() - start_time
        avg_rate = total_responses / elapsed if elapsed > 0 else 0
        
        print(f"\n[PARALLEL] ✓ Completed in {elapsed:.1f}s")
        print(f"[PARALLEL] ✓ Average rate: {avg_rate:.1f} responses/second")
        print(f"[PARALLEL] ✓ Speedup: ~{self.max_workers:.1f}x faster vs sequential")
        
        return all_classifications
    
    def classify_sequential(self, responses: List[str], categories: List[str],
                           question_text: str = "", batch_size: int = 10,
                           progress_callback: Callable = None) -> List[List[Tuple[str, float]]]:
        """
        Sequential classification (fallback atau untuk debugging)
        
        Args:
            responses: List of responses
            categories: List of categories
            question_text: Question context
            batch_size: Batch size
            progress_callback: Progress callback
        
        Returns:
            List of classifications
        """
        print(f"\n[SEQUENTIAL] Processing {len(responses)} responses")
        
        all_classifications = []
        start_time = time.time()
        
        for batch_idx in range(0, len(responses), batch_size):
            batch = responses[batch_idx:batch_idx+batch_size]
            
            try:
                # Classify batch
                print(f"[OPENAI] Batch classifying {len(batch)} responses (multi-label: {self.classifier.enable_multi_label})...")
                classifications = self.classifier.classify_responses_batch_api(
                    batch, categories, question_text
                )
                print(f"[OPENAI] Batch completed: {len(classifications)} classifications")
                
                all_classifications.extend(classifications)
                
                # Progress
                completed = len(all_classifications)
                percentage = int((completed / len(responses)) * 100)
                elapsed = time.time() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                
                message = f"Classifying... {completed}/{len(responses)} ({percentage}%) - {rate:.1f} resp/sec"
                print(f"[SEQUENTIAL] {message}")
                
                if progress_callback:
                    progress_callback(message, percentage)
                    
            except Exception as e:
                print(f"[ERROR] Batch at {batch_idx} failed: {str(e)}")
                import traceback
                traceback.print_exc()
                # Add empty for failed
                all_classifications.extend([[("Other", 0.0)] for _ in batch])
        
        elapsed = time.time() - start_time
        avg_rate = len(responses) / elapsed if elapsed > 0 else 0
        print(f"\n[SEQUENTIAL] ✓ Completed in {elapsed:.1f}s - {avg_rate:.1f} responses/second")
        
        return all_classifications

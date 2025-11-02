# Incremental Processing Implementation

## Overview

This implementation improves data processing efficiency by processing websites incrementally rather than collecting all data first. Each website is now:
1. Scraped
2. Sent to AI for analysis
3. Added to the response
4. Then the next website is processed

## Key Changes

### 1. Incremental Processing Method (`processor.py`)

**New Method: `process_jobs_incrementally()`**
- Generator function that yields results as they're processed
- Processes one company at a time
- Memory efficient for large datasets

**New Method: `_process_single_entry_incremental()`**
- Processes content sources separately:
  1. Main page → AI analysis → add results
  2. PDFs (up to 2) → AI analysis per PDF → add results
  3. Job detail pages (up to 2) → AI analysis per page → add results
- Each content source is analyzed independently for better accuracy
- Reduced limits (from 3→2) for faster processing

### 2. API Endpoints (`main.py`)

**Modified: GET `/jobs`**
- Now uses incremental processing internally
- Still returns complete Table object for backward compatibility
- Processes entries sequentially: scrape → AI → add to response → next

**New: GET `/jobs/stream`**
- True streaming response
- Results streamed as JSON as they become available
- Useful for monitoring progress with many companies
- Format: `{"rows": [...]}` streamed incrementally

### 3. AI Performance Improvements (`ai_agent.py`)

**Optimization:**
- Reduced `max_content_length` from 10,000 to 8,000 characters
- Faster AI processing with focused content
- Content truncated per-source (10,000 chars each) before combining

## Performance Benefits

1. **Faster Time-to-First-Result**: Users see results immediately rather than waiting for all processing
2. **Lower Memory Usage**: Process one entry at a time instead of accumulating all data
3. **Better Error Recovery**: Single failure doesn't block entire batch
4. **Reduced AI Token Usage**: Smaller content chunks = faster AI responses
5. **Progressive User Experience**: Frontend can display results as they arrive

## Backward Compatibility

- Original `/jobs` endpoint maintains same response format (Table with rows)
- Internal implementation changed to incremental processing
- No breaking changes for existing clients
- New `/jobs/stream` endpoint available for streaming use cases

## Usage Examples

### Standard Endpoint (backward compatible)
```python
import requests

response = requests.get('http://localhost:8000/jobs')
data = response.json()
print(f"Found {len(data['rows'])} job entries")
```

### Streaming Endpoint (new)
```python
import requests

response = requests.get('http://localhost:8000/jobs/stream', stream=True)
for line in response.iter_content(chunk_size=1024):
    # Process each chunk as it arrives
    print(line.decode('utf-8'))
```

## Testing

Run the incremental processing tests:
```bash
python test_incremental_processing.py
```

## Future Enhancements

Possible improvements for future iterations:
1. Parallel processing of independent sources (PDFs, pages)
2. Caching of AI results to avoid re-processing
3. WebSocket support for real-time updates
4. Progress indicators in streaming response

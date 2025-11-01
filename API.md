# API Documentation

Complete API reference for the Application Information Backend.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required. In production, implement proper authentication mechanisms.

## Endpoints

### 1. Root Endpoint

**GET /**

Get basic information about the API.

**Response:**
```json
{
  "message": "Application Information Backend API",
  "version": "1.0.0",
  "status": "running"
}
```

**Status Codes:**
- `200 OK` - Success

---

### 2. Health Check

**GET /health**

Check the health status of the API and configuration.

**Response:**
```json
{
  "status": "healthy",
  "openai_configured": true
}
```

**Fields:**
- `status` (string) - Health status ("healthy" or "unhealthy")
- `openai_configured` (boolean) - Whether OpenAI API key is configured

**Status Codes:**
- `200 OK` - Success

---

### 3. Get Applications List

**GET /applications**

Retrieve the list of applications from the Excel file without processing them.

**Response:**
```json
{
  "success": true,
  "count": 3,
  "applications": [
    {
      "id": 1,
      "name": "Example Company",
      "url": "https://www.example.com",
      "description": "A sample company website"
    }
  ]
}
```

**Fields:**
- `success` (boolean) - Whether the request was successful
- `count` (integer) - Number of applications
- `applications` (array) - List of application objects

**Application Object:**
- `id` (integer) - Unique identifier
- `name` (string) - Application name
- `url` (string) - Website URL
- `description` (string, optional) - Application description

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Excel file not found
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl http://localhost:8000/applications
```

---

### 4. Process Applications

**POST /process**

Process all applications from the Excel file. This is the main endpoint that:
1. Reads entries from the Excel file
2. Scrapes each website
3. Extracts links (PDFs, images, webpages)
4. Extracts content from PDFs and images
5. Uses AI to analyze and summarize
6. Returns structured JSON data

**⚠️ Note:** This operation can take several minutes depending on the number of applications and content.

**Response:**
```json
{
  "success": true,
  "message": "Successfully processed 3 applications",
  "data": [
    {
      "id": 1,
      "name": "Example Company",
      "main_url": "https://www.example.com",
      "description": "A sample company website",
      "extracted_links": [
        {
          "url": "https://www.example.com/about",
          "link_type": "webpage",
          "title": "About Us"
        },
        {
          "url": "https://www.example.com/brochure.pdf",
          "link_type": "pdf",
          "title": "Company Brochure"
        },
        {
          "url": "https://www.example.com/logo.png",
          "link_type": "image",
          "title": "Company Logo"
        }
      ],
      "extracted_contents": [
        {
          "url": "https://www.example.com",
          "content_type": "webpage",
          "text_content": "Welcome to Example Company...",
          "metadata": {
            "is_main_page": true
          },
          "extracted_at": "2025-11-01T11:37:13.317Z"
        },
        {
          "url": "https://www.example.com/brochure.pdf",
          "content_type": "pdf",
          "text_content": "PDF content...",
          "metadata": {
            "title": "Company Brochure"
          },
          "extracted_at": "2025-11-01T11:37:15.123Z"
        }
      ],
      "summary": "Example Company is a leading provider of...",
      "processed_at": "2025-11-01T11:37:20.456Z"
    }
  ],
  "error": null
}
```

**Response Fields:**

**Top Level:**
- `success` (boolean) - Whether processing was successful
- `message` (string) - Status message
- `data` (array) - List of processed ApplicationInfo objects
- `error` (string, optional) - Error message if failed

**ApplicationInfo Object:**
- `id` (integer) - Application identifier
- `name` (string) - Application name
- `main_url` (string) - Main website URL
- `description` (string, optional) - Description
- `extracted_links` (array) - All links found on the website
- `extracted_contents` (array) - Extracted content from various sources
- `summary` (string) - AI-generated summary
- `processed_at` (string) - ISO 8601 timestamp

**ExtractedLink Object:**
- `url` (string) - Link URL
- `link_type` (string) - Type: "webpage", "pdf", "image", or "other"
- `title` (string, optional) - Link title or alt text

**ExtractedContent Object:**
- `url` (string) - Content source URL
- `content_type` (string) - Type: "webpage", "pdf", or "image"
- `text_content` (string) - Extracted text
- `metadata` (object) - Additional metadata
- `extracted_at` (string) - ISO 8601 timestamp

**Status Codes:**
- `200 OK` - Success (check `success` field for actual status)
- `404 Not Found` - Excel file not found
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl -X POST http://localhost:8000/process
```

**Example with Python:**
```python
import requests
response = requests.post('http://localhost:8000/process')
data = response.json()
print(data)
```

**Example with JavaScript:**
```javascript
fetch('http://localhost:8000/process', {method: 'POST'})
  .then(response => response.json())
  .then(data => console.log(data));
```

---

### 5. Upload Excel File

**POST /upload-excel**

Upload a new Excel file with website applications. The file replaces the current Excel file.

**Request:**
- Content-Type: `multipart/form-data`
- Field name: `file`

**Excel File Requirements:**
- Must be a valid Excel file (.xlsx)
- Must contain required columns: `id`, `name`, `url`
- Optional column: `description`

**Response:**
```json
{
  "success": true,
  "message": "Excel file uploaded successfully",
  "file_path": "data/applications.xlsx"
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Upload failed

**Example with curl:**
```bash
curl -X POST http://localhost:8000/upload-excel \
  -F "file=@/path/to/your/applications.xlsx"
```

**Example with Python:**
```python
import requests

with open('applications.xlsx', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/upload-excel', files=files)
    print(response.json())
```

**Example with JavaScript (HTML form):**
```html
<form id="uploadForm">
  <input type="file" name="file" id="fileInput" accept=".xlsx">
  <button type="submit">Upload</button>
</form>

<script>
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData();
  formData.append('file', document.getElementById('fileInput').files[0]);
  
  const response = await fetch('http://localhost:8000/upload-excel', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  console.log(data);
});
</script>
```

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message here"
}
```

Common HTTP status codes:
- `200 OK` - Success
- `400 Bad Request` - Invalid request
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Rate Limiting

Currently no rate limiting is implemented. In production:
- Implement rate limiting per IP/user
- Consider caching for GET requests
- Use background tasks for long-running operations

## CORS

CORS is currently configured to allow all origins. In production, configure specific allowed origins:

```python
allow_origins=["https://yourfrontend.com"]
```

## Interactive Documentation

The API provides interactive documentation powered by Swagger UI and ReDoc:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Explore all endpoints
- Test API calls directly from the browser
- View detailed request/response schemas
- Download OpenAPI specification

## WebSocket Support

WebSocket support for real-time progress updates is not currently implemented but could be added for long-running processing tasks.

## Best Practices

### For Frontend Integration

1. **Show loading indicators** during POST /process (can take minutes)
2. **Handle errors gracefully** - display user-friendly messages
3. **Cache responses** where appropriate
4. **Validate Excel files** before uploading
5. **Implement pagination** if dealing with many applications

### For Large-Scale Usage

1. **Use background tasks** (Celery, RQ) for processing
2. **Implement job queue** and status tracking
3. **Add database** for storing results
4. **Configure rate limiting**
5. **Set up monitoring** and logging
6. **Use caching** (Redis) for frequently accessed data

## Security Considerations

For production deployment:

1. **Add authentication** - API keys, OAuth, JWT
2. **Validate file uploads** - check file types, size limits
3. **Sanitize inputs** - prevent injection attacks
4. **Configure CORS** properly
5. **Use HTTPS** in production
6. **Implement rate limiting**
7. **Set up proper logging** and monitoring
8. **Keep API keys secure** - never commit to Git

## Support

For issues and questions:
- Check the [README](README.md)
- Review [QUICKSTART](QUICKSTART.md)
- Open an issue on GitHub

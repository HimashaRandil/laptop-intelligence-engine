# API Documentation

The Laptop Intelligence Engine provides two main API services for accessing laptop data and AI-powered features.

## Base URLs

- **Backend API**: `http://localhost:8000`
- **AI Service**: `http://localhost:8001`
- **Interactive Documentation**: 
  - Backend: `http://localhost:8000/docs`
  - AI Service: `http://localhost:8001/ai/docs`

## Authentication

Currently, no authentication is required for API access. All endpoints are publicly accessible.

---

## Backend API Endpoints

### Health & Status

#### Health Check
```http
GET /health
```

**Description**: Check API health and database connectivity

**Response**:
```json
{
  "status": "healthy",
  "database": "connected", 
  "laptop_count": 4
}
```

#### Root Information
```http
GET /
```

**Response**:
```json
{
  "message": "Laptop Intelligence Engine API",
  "version": "1.0.0",
  "docs_url": "/docs"
}
```

### Laptop Catalog

#### Get All Laptops
```http
GET /laptops
```

**Parameters**:
- `brand` (optional): Filter by brand (Lenovo, HP)

**Response**:
```json
[
  {
    "id": 1,
    "brand": "Lenovo",
    "full_model_name": "ThinkPad E14 Gen 5 (Intel)",
    "product_page_url": "https://...",
    "image_url": "https://...",
    "latest_price": 1149.00,
    "availability": "In Stock",
    "average_rating": 4.3,
    "review_count": 12
  }
]
```

**Example**:
```bash
curl "http://localhost:8000/laptops?brand=Lenovo"
```

#### Get Laptop Details
```http
GET /laptops/{laptop_id}
```

**Parameters**:
- `laptop_id` (required): Laptop ID (1-4)

**Response**: Complete laptop object with specifications, price history, and reviews

**Example**:
```bash
curl "http://localhost:8000/laptops/1"
```

#### Compare Laptops
```http
GET /laptops/compare
```

**Parameters**:
- `ids` (required): Comma-separated laptop IDs (max 5)

**Example**:
```bash
curl "http://localhost:8000/laptops/compare?ids=1,2,3"
```

### Specifications

#### Get Laptop Specifications
```http
GET /laptops/{laptop_id}/specifications
```

**Parameters**:
- `laptop_id` (required): Laptop ID
- `category` (optional): Filter by category (Processor, Memory, Storage, etc.)

**Response**:
```json
[
  {
    "category": "Processor",
    "specification_name": "Core i7-1355U 10 - Cores",
    "specification_value": "2",
    "unit": null,
    "structured_value": {
      "brand": "Intel",
      "cores": 10,
      "model": "Core i7-1355U"
    }
  }
]
```

#### Search Specifications
```http
GET /specifications/search
```

**Parameters**:
- `query` (required): Search term
- `category` (optional): Filter by category

**Example**:
```bash
curl "http://localhost:8000/specifications/search?query=Intel&category=Processor"
```

### Pricing

#### Get Price History
```http
GET /laptops/{laptop_id}/prices
```

**Parameters**:
- `laptop_id` (required): Laptop ID
- `limit` (optional): Number of price snapshots (default: 10)

**Response**:
```json
[
  {
    "price": 1149.00,
    "currency": "USD",
    "availability_status": "In Stock",
    "configuration_summary": "Core i7-1355U / 16GB RAM / 512GB SSD",
    "scraped_at": "2025-09-25T19:32:07.098972Z"
  }
]
```

### Reviews

#### Get Laptop Reviews
```http
GET /laptops/{laptop_id}/reviews
```

**Parameters**:
- `laptop_id` (required): Laptop ID
- `min_rating` (optional): Minimum rating filter (1-5)
- `limit` (optional): Number of reviews (default: 10)

**Response**:
```json
[
  {
    "rating": 5,
    "review_title": "Excellent business laptop",
    "review_text": "Been using this ThinkPad for 6 months...",
    "reviewer_name": "TechManager_Sarah",
    "reviewer_verified": false,
    "helpful_count": 0
  }
]
```

### Questions & Answers

#### Get Laptop Q&A
```http
GET /laptops/{laptop_id}/questions
```

**Parameters**:
- `laptop_id` (required): Laptop ID
- `limit` (optional): Number of Q&A pairs (default: 10)

**Response**:
```json
[
  {
    "question_text": "Can this laptop handle video editing?",
    "answer_text": "Yes, it handles basic video editing well...",
    "asker_name": "MarketingManager_Pete",
    "answerer_name": "VideoProducer_Kate",
    "helpful_count": 8,
    "configuration_summary": "Core i7-1355U / 16GB RAM / 512GB SSD"
  }
]
```

#### Search Q&A
```http
GET /questions/search
```

**Parameters**:
- `query` (required): Search term in questions/answers

**Example**:
```bash
curl "http://localhost:8000/questions/search?query=programming"
```

### Metadata

#### Get Categories
```http
GET /categories
```

**Response**:
```json
{
  "categories": ["Processor", "Memory", "Storage", "Graphics", "Battery", "Physical"]
}
```

#### Get Brands
```http
GET /brands
```

**Response**:
```json
{
  "brands": ["Lenovo", "HP"]
}
```

---

## AI Service Endpoints

### Health & Status

#### AI Health Check
```http
GET /ai/health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "AI Service",
  "version": "1.0.0",
  "openai_configured": true
}
```

### Chat Interface

#### Chat with AI Assistant
```http
POST /ai/chat
```

**Request Body**:
```json
{
  "message": "What laptops are under $1000?",
  "conversation_id": "conv_12345"
}
```

**Response**:
```json
{
  "response": "I found 3 laptops under $1000: ThinkPad E14 Gen 5 (AMD), HP ProBook 450 G10, and HP ProBook 440 G11...",
  "conversation_id": "conv_12345",
  "status": "success"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8001/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What laptops are under $1000?"}'
```

#### Get Recommendations
```http
POST /ai/recommend
```

**Request Body**:
```json
{
  "message": "I need a laptop for programming work",
  "conversation_id": "rec_67890"
}
```

**Response**: Same format as chat endpoint but with enhanced recommendation prompting

**Example**:
```bash
curl -X POST "http://localhost:8001/ai/recommend" \
  -H "Content-Type: application/json" \
  -d '{"message": "Best laptop for video editing?"}'
```

---

## AI Capabilities

### Supported Query Types

1. **Budget Queries**
   - "Show me laptops under $1200"
   - "What's the cheapest ThinkPad?"

2. **Specification Queries**
   - "I need a laptop with Intel i7 processor"
   - "Which laptops have 16GB RAM?"

3. **Use Case Queries**
   - "Best laptop for programming"
   - "Good laptop for business presentations"

4. **Review-Based Queries**
   - "What do users say about battery life?"
   - "ThinkPad keyboard reviews"

5. **Comparison Queries**
   - "Compare ThinkPad vs ProBook"
   - "Intel vs AMD variants"

### AI Features

- **Natural Language Processing**: Understands complex, conversational queries
- **Vector Search**: Semantic search through customer reviews and Q&A
- **Multi-tool Orchestration**: Combines database queries with vector search
- **Contextual Responses**: Maintains conversation context across multiple turns
- **Citation Support**: References source data in responses (backend only)

---

## Error Handling

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
  "detail": "Error description",
  "status_code": 400
}
```

### Common Error Scenarios

1. **Invalid Laptop ID**
   ```json
   {
     "detail": "Laptop not found",
     "status_code": 404
   }
   ```

2. **Invalid Comparison Request**
   ```json
   {
     "detail": "Cannot compare more than 5 laptops at once",
     "status_code": 400
   }
   ```

3. **AI Service Error**
   ```json
   {
     "detail": "Error processing chat request: OpenAI API error",
     "status_code": 500
   }
   ```

---

## Rate Limits

Currently, no rate limiting is implemented. For production use, consider:
- Backend API: 1000 requests/hour per IP
- AI Service: 100 requests/hour per IP (due to LLM costs)

---

## Data Models

### Laptop Object
```json
{
  "id": 1,
  "brand": "Lenovo",
  "model_name": "ThinkPad E14 Gen 5",
  "variant": "Intel",
  "full_model_name": "ThinkPad E14 Gen 5 (Intel)",
  "product_page_url": "https://...",
  "pdf_spec_url": "https://...",
  "image_url": "https://...",
  "specifications": [...],
  "price_snapshots": [...],
  "reviews": [...]
}
```

### Specification Object
```json
{
  "category": "Processor",
  "specification_name": "Core i7-1355U 10 - Cores",
  "specification_value": "2",
  "unit": null,
  "structured_value": {
    "brand": "Intel",
    "cores": 10,
    "model": "Core i7-1355U"
  }
}
```

### Price Snapshot Object
```json
{
  "price": 1149.00,
  "currency": "USD",
  "availability_status": "In Stock",
  "shipping_info": null,
  "promotion_text": null,
  "configuration_summary": "Core i7-1355U / 16GB RAM / 512GB SSD",
  "scraped_at": "2025-09-25T19:32:07.098972Z"
}
```

### Review Object
```json
{
  "rating": 5,
  "review_title": "Excellent business laptop",
  "review_text": "Been using this ThinkPad for 6 months...",
  "reviewer_name": "TechManager_Sarah",
  "reviewer_verified": false,
  "review_date": "2025-08-15",
  "helpful_count": 0,
  "configuration_summary": "Core i7-1355U / 16GB RAM / 512GB SSD"
}
```

---

## Usage Examples

### Complete Laptop Research Workflow

```bash
# 1. Get all available laptops
curl "http://localhost:8000/laptops"

# 2. Get detailed specs for a specific laptop
curl "http://localhost:8000/laptops/1"

# 3. Check reviews for that laptop
curl "http://localhost:8000/laptops/1/reviews"

# 4. Ask AI for recommendations
curl -X POST "http://localhost:8001/ai/recommend" \
  -H "Content-Type: application/json" \
  -d '{"message": "I need a laptop for programming under $1200"}'

# 5. Compare with similar models
curl "http://localhost:8000/laptops/compare?ids=1,2"
```

### AI-Powered Search

```bash
# Natural language queries
curl -X POST "http://localhost:8001/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Which laptop has the best keyboard for coding?"}'

curl -X POST "http://localhost:8001/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me user reviews about battery life"}'
```

---

## SDK & Client Libraries

Currently, no official SDKs are provided. The API follows REST conventions and can be used with any HTTP client library.

### JavaScript/TypeScript Example
```typescript
const API_BASE = 'http://localhost:8000';
const AI_BASE = 'http://localhost:8001';

// Get laptops
const response = await fetch(`${API_BASE}/laptops`);
const laptops = await response.json();

// Chat with AI
const chatResponse = await fetch(`${AI_BASE}/ai/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'What laptops are under $1000?' })
});
const result = await chatResponse.json();
```

### Python Example
```python
import requests

# Get laptops
response = requests.get('http://localhost:8000/laptops')
laptops = response.json()

# Chat with AI
chat_response = requests.post(
    'http://localhost:8001/ai/chat',
    json={'message': 'What laptops are under $1000?'}
)
result = chat_response.json()
```

---

## Support & Development

- **Interactive API Documentation**: Available at `/docs` endpoints
- **OpenAPI Specification**: Available at `/openapi.json` endpoints
- **Issues & Bugs**: Report via GitHub repository
- **Feature Requests**: Submit via GitHub issues
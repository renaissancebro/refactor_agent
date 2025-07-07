# Refactor Agent API

A FastAPI-based service that provides AI-powered code refactoring capabilities with Stripe integration for monetization.

## Features

- **AI-Powered Refactoring**: Uses OpenAI GPT-4 to intelligently refactor code
- **Multiple Refactor Types**: Supports refactoring, optimization, documentation, style improvements, and security reviews
- **Stripe Payment Integration**: Secure payment processing with credit-based usage
- **API Key Management**: Secure authentication and usage tracking
- **Rate Limiting**: Built-in protection against abuse
- **Usage Analytics**: Track API usage and remaining credits

## Setup Instructions

### 1. Environment Setup

```bash
# Navigate to the API directory
cd /Users/joshuafreeman/Desktop/agent_projects/autogen/refactor_agent/api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the API directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Security (generate strong random strings)
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Stripe Setup

1. Create a Stripe account at https://stripe.com
2. Get your API keys from the Stripe dashboard
3. Set up webhooks for payment confirmations (optional but recommended)

### 4. Running the Server

```bash
# Development server
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication
All API endpoints (except payment and health) require a Bearer token with your API key:
```
Authorization: Bearer your_api_key_here
```

### Endpoints

#### 1. Health Check
```http
GET /api/v1/health
```
Returns API health status and configuration info.

#### 2. Pricing Information
```http
GET /api/v1/pricing
```
Returns available pricing plans and credit information.

#### 3. Create Payment Intent
```http
POST /api/v1/payment/create-intent
Content-Type: application/json

{
  "amount": 500,
  "currency": "usd",
  "description": "Refactor Agent API Credits"
}
```

#### 4. Confirm Payment
```http
POST /api/v1/payment/confirm
Content-Type: application/json

{
  "api_key": "rfa_your_api_key_here",
  "payment_intent_id": "pi_stripe_payment_intent_id"
}
```

#### 5. Refactor Code
```http
POST /api/v1/refactor
Authorization: Bearer your_api_key_here
Content-Type: application/json

{
  "code": "def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b",
  "suggestion_type": "refactor",
  "language": "python"
}
```

**Suggestion Types:**
- `refactor`: Extract reusable components into utility modules
- `optimize`: Improve performance and efficiency
- `document`: Add comprehensive documentation
- `style`: Apply PEP 8 style improvements
- `security`: Review for security vulnerabilities

#### 6. Usage Statistics
```http
GET /api/v1/usage
Authorization: Bearer your_api_key_here
```

## Usage Examples

### Python Client Example

```python
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

# Step 1: Create payment intent
payment_response = requests.post(f"{BASE_URL}/api/v1/payment/create-intent", 
    json={
        "amount": 500,  # $5.00
        "currency": "usd",
        "description": "Refactor Agent Credits"
    }
)

payment_data = payment_response.json()
api_key = payment_data["api_key"]

# Step 2: (Process payment with Stripe frontend)
# After successful payment, confirm it
confirm_response = requests.post(f"{BASE_URL}/api/v1/payment/confirm", 
    json={
        "api_key": api_key,
        "payment_intent_id": "pi_your_payment_intent_id"
    }
)

# Step 3: Use the API to refactor code
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

refactor_response = requests.post(f"{BASE_URL}/api/v1/refactor", 
    headers=headers,
    json={
        "code": '''
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price * item.quantity
    return total

def apply_discount(total, discount_percent):
    return total * (1 - discount_percent / 100)
        ''',
        "suggestion_type": "refactor",
        "language": "python"
    }
)

result = refactor_response.json()
print("Refactored Code:")
print(result["refactored_main"])
```

### JavaScript/Node.js Client Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

async function refactorCode() {
    try {
        // Create payment intent
        const paymentResponse = await axios.post(`${BASE_URL}/api/v1/payment/create-intent`, {
            amount: 500,
            currency: 'usd',
            description: 'Refactor Agent Credits'
        });
        
        const apiKey = paymentResponse.data.api_key;
        
        // After payment confirmation, use the API
        const refactorResponse = await axios.post(`${BASE_URL}/api/v1/refactor`, {
            code: `
def hello_world():
    print("Hello, World!")
    
def goodbye_world():
    print("Goodbye, World!")
            `,
            suggestion_type: 'document',
            language: 'python'
        }, {
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            }
        });
        
        console.log('Refactored code:', refactorResponse.data.refactored_main);
        
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
    }
}

refactorCode();
```

### cURL Examples

```bash
# Check API health
curl -X GET http://localhost:8000/api/v1/health

# Get pricing information
curl -X GET http://localhost:8000/api/v1/pricing

# Create payment intent
curl -X POST http://localhost:8000/api/v1/payment/create-intent \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500,
    "currency": "usd",
    "description": "Refactor Agent Credits"
  }'

# Refactor code (with API key)
curl -X POST http://localhost:8000/api/v1/refactor \
  -H "Authorization: Bearer your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def add(a, b):\n    return a + b",
    "suggestion_type": "refactor",
    "language": "python"
  }'

# Check usage
curl -X GET http://localhost:8000/api/v1/usage \
  -H "Authorization: Bearer your_api_key_here"
```

## Pricing Model

- **Starter Plan**: $5.00 → 5 credits
- **Professional Plan**: $20.00 → 25 credits  
- **Enterprise Plan**: $50.00 → 75 credits

Each refactor request consumes 1 credit.

## Security Features

- **API Key Authentication**: Secure bearer token authentication
- **Rate Limiting**: Protection against abuse
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Secure error responses without sensitive data exposure
- **Logging**: Comprehensive logging for monitoring and debugging

## Production Deployment

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Docker Compose

```yaml
version: '3.8'

services:
  refactor-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
    depends_on:
      - redis
      - postgres
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: refactor_agent
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Monitoring and Analytics

The API includes built-in monitoring endpoints:

- Health checks at `/api/v1/health`
- Usage statistics per API key
- Request/response logging
- Error tracking and reporting

## Support

For issues or questions:
1. Check the logs in the console output
2. Verify your environment variables are set correctly
3. Ensure you have sufficient credits
4. Check the API documentation at `http://localhost:8000/docs`

## License

This project is proprietary software. All rights reserved.
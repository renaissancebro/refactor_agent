"""
FastAPI application for the refactor agent with Stripe integration.
Provides paid API access to the refactor agent functionality.
"""

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import os
import sys
import json
import uuid
import time
from datetime import datetime, timedelta
from pathlib import Path
import stripe
import logging
from contextlib import asynccontextmanager
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Add the agent directory to path
current_dir = Path(__file__).parent.parent
agent_dir = current_dir / "agent"
sys.path.append(str(agent_dir))

from main_agent import assistant, user
from refactor_cli import refactor_file, get_suggestion_prompt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
if not stripe.api_key:
    logger.warning("STRIPE_SECRET_KEY not set. Payment processing disabled.")

# Security
security = HTTPBearer()

# In-memory storage (replace with proper database in production)
api_keys = {}
usage_tracking = {}
active_sessions = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app"""
    # Startup
    logger.info("Starting Refactor Agent API...")
    yield
    # Shutdown
    logger.info("Shutting down Refactor Agent API...")

app = FastAPI(
    title="Refactor Agent API",
    description="AI-powered code refactoring service with Stripe integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread pool for blocking operations
thread_pool = ThreadPoolExecutor(max_workers=5)

class RefactorRequest(BaseModel):
    """Request model for refactor endpoint"""
    code: str = Field(..., description="The code to refactor")
    suggestion_type: str = Field(default="refactor", description="Type of refactoring")
    language: str = Field(default="python", description="Programming language")
    
    class Config:
        schema_extra = {
            "example": {
                "code": "def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b",
                "suggestion_type": "refactor",
                "language": "python"
            }
        }

class RefactorResponse(BaseModel):
    """Response model for refactor endpoint"""
    success: bool
    refactored_main: Optional[str] = None
    utility_modules: Optional[Dict[str, str]] = None
    backup_file: Optional[str] = None
    message: str
    usage_count: int
    session_id: str

class PaymentRequest(BaseModel):
    """Request model for payment processing"""
    amount: int = Field(..., description="Amount in cents")
    currency: str = Field(default="usd", description="Currency code")
    description: str = Field(default="Refactor Agent API Credits", description="Payment description")

class PaymentResponse(BaseModel):
    """Response model for payment processing"""
    success: bool
    client_secret: Optional[str] = None
    api_key: Optional[str] = None
    credits: Optional[int] = None
    message: str

class UsageResponse(BaseModel):
    """Response model for usage tracking"""
    api_key: str
    total_requests: int
    remaining_credits: int
    created_at: str
    last_used: Optional[str] = None

def generate_api_key() -> str:
    """Generate a unique API key"""
    return f"rfa_{uuid.uuid4().hex[:32]}"

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key and check usage limits"""
    if not credentials:
        raise HTTPException(status_code=401, detail="API key required")
    
    api_key = credentials.credentials
    
    if api_key not in api_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    key_info = api_keys[api_key]
    
    # Check if key is expired
    if key_info.get("expires_at") and datetime.now() > key_info["expires_at"]:
        raise HTTPException(status_code=401, detail="API key expired")
    
    # Check credit balance
    if key_info.get("credits", 0) <= 0:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    return api_key

async def refactor_code_async(code: str, suggestion_type: str) -> Dict[str, Any]:
    """Async wrapper for refactor functionality"""
    loop = asyncio.get_event_loop()
    
    def refactor_sync():
        try:
            # Import required modules
            from io import StringIO
            from contextlib import redirect_stdout
            
            # Get suggestion prompt
            suggestion_prompt = get_suggestion_prompt(suggestion_type)
            
            # Prepare message
            message = f"""
            {suggestion_prompt}

            Return the structured JSON output with these exact keys:
            - 'refactored_main': The improved version of the original file
            - 'backup_file': The old code to be saved to a separate file
            - 'utility_modules': Dictionary of extracted utility modules (filename -> code)

            Code to improve:
            ```python
            {code}
            ```
            """
            
            # Capture stdout to get the agent's response
            output_buffer = StringIO()
            with redirect_stdout(output_buffer):
                user.initiate_chat(assistant, message=message)
            
            # Get the captured output
            captured_output = output_buffer.getvalue()
            
            # Parse the JSON response
            json_start = captured_output.find('```json')
            if json_start == -1:
                json_start = captured_output.find('{')
            
            json_end = captured_output.rfind('```')
            if json_end == -1:
                json_end = captured_output.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = captured_output[json_start:json_end].replace('```json', '').replace('```', '').strip()
                parsed_response = json.loads(json_str)
                return parsed_response
            else:
                raise Exception("No JSON block found in response")
                
        except Exception as e:
            logger.error(f"Refactor error: {e}")
            raise e
    
    return await loop.run_in_executor(thread_pool, refactor_sync)

@app.post("/api/v1/payment/create-intent", response_model=PaymentResponse)
async def create_payment_intent(request: PaymentRequest):
    """Create a Stripe payment intent and generate API key"""
    try:
        if not stripe.api_key:
            raise HTTPException(status_code=503, detail="Payment processing unavailable")
        
        # Calculate credits based on pricing tiers
        credits_mapping = {
            990: 10,   # Starter
            2990: 50,  # Professional  
            9990: 250  # Enterprise
        }
        credits = credits_mapping.get(request.amount, request.amount // 100)
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=request.amount,
            currency=request.currency,
            description=request.description,
            metadata={
                "service": "refactor_agent",
                "credits": str(credits),
                "api_key": generate_api_key()
            }
        )
        
        # Generate API key
        api_key = generate_api_key()
        
        # Store API key info (pending payment confirmation)
        api_keys[api_key] = {
            "credits": 0,  # Will be activated after payment
            "total_requests": 0,
            "created_at": datetime.now(),
            "payment_intent": intent.id,
            "pending_credits": credits,
            "status": "pending"
        }
        
        return PaymentResponse(
            success=True,
            client_secret=intent.client_secret,
            api_key=api_key,
            credits=credits,
            message="Payment intent created successfully"
        )
        
    except Exception as e:
        logger.error(f"Payment creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Payment creation failed: {str(e)}")

@app.post("/api/v1/payment/confirm")
async def confirm_payment(api_key: str, payment_intent_id: str):
    """Confirm payment and activate API key"""
    try:
        if not stripe.api_key:
            raise HTTPException(status_code=503, detail="Payment processing unavailable")
        
        # Verify payment intent
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status != "succeeded":
            raise HTTPException(status_code=400, detail="Payment not confirmed")
        
        # Activate API key
        if api_key in api_keys:
            key_info = api_keys[api_key]
            if key_info["payment_intent"] == payment_intent_id:
                key_info["credits"] = key_info["pending_credits"]
                key_info["status"] = "active"
                key_info["activated_at"] = datetime.now()
                
                return {"success": True, "message": "API key activated successfully"}
        
        raise HTTPException(status_code=400, detail="Invalid API key or payment intent")
        
    except Exception as e:
        logger.error(f"Payment confirmation error: {e}")
        raise HTTPException(status_code=500, detail=f"Payment confirmation failed: {str(e)}")

@app.post("/api/v1/refactor", response_model=RefactorResponse)
async def refactor_code(request: RefactorRequest, api_key: str = Depends(verify_api_key)):
    """Refactor code using the AI agent"""
    try:
        # Check OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(status_code=503, detail="OpenAI API key not configured")
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Track usage
        key_info = api_keys[api_key]
        key_info["total_requests"] += 1
        key_info["credits"] -= 1
        key_info["last_used"] = datetime.now()
        
        # Store session info
        active_sessions[session_id] = {
            "api_key": api_key,
            "started_at": datetime.now(),
            "request": request.dict()
        }
        
        # Validate suggestion type
        valid_types = ["refactor", "optimize", "document", "style", "security"]
        if request.suggestion_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid suggestion_type. Must be one of: {valid_types}")
        
        # Refactor the code
        result = await refactor_code_async(request.code, request.suggestion_type)
        
        # Clean up session
        active_sessions.pop(session_id, None)
        
        return RefactorResponse(
            success=True,
            refactored_main=result.get("refactored_main"),
            utility_modules=result.get("utility_modules"),
            backup_file=result.get("backup_file"),
            message="Code refactored successfully",
            usage_count=key_info["total_requests"],
            session_id=session_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Refactor error: {e}")
        # Clean up session on error
        active_sessions.pop(session_id, None)
        raise HTTPException(status_code=500, detail=f"Refactoring failed: {str(e)}")

@app.get("/api/v1/usage", response_model=UsageResponse)
async def get_usage(api_key: str = Depends(verify_api_key)):
    """Get usage statistics for an API key"""
    key_info = api_keys[api_key]
    
    return UsageResponse(
        api_key=api_key,
        total_requests=key_info["total_requests"],
        remaining_credits=key_info["credits"],
        created_at=key_info["created_at"].isoformat(),
        last_used=key_info["last_used"].isoformat() if key_info.get("last_used") else None
    )

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "stripe_configured": bool(stripe.api_key)
    }

@app.get("/api/v1/pricing")
async def get_pricing():
    """Get pricing information"""
    return {
        "plans": {
            "starter": {
                "price": 990,  # $9.90
                "credits": 10,
                "description": "10 refactor requests - Perfect for trying the service",
                "price_per_refactor": "$0.99",
                "best_for": "Individual developers, small projects"
            },
            "professional": {
                "price": 2990,  # $29.90
                "credits": 50,
                "description": "50 refactor requests - Most popular plan",
                "price_per_refactor": "$0.60",
                "best_for": "Professional developers, medium projects",
                "savings": "40% vs Starter"
            },
            "enterprise": {
                "price": 9990,  # $99.90
                "credits": 250,
                "description": "250 refactor requests - Maximum value",
                "price_per_refactor": "$0.40",
                "best_for": "Teams, large codebases, frequent refactoring",
                "savings": "60% vs Starter"
            }
        },
        "currency": "usd",
        "note": "Prices are in cents. 1 credit = 1 refactor request. Credits never expire."
    }

@app.post("/api/v1/payment/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks for payment confirmation"""
    try:
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        if not webhook_secret:
            logger.warning("Stripe webhook secret not configured")
            return {"status": "webhook_secret_missing"}
        
        payload = await request.body()
        signature = request.headers.get("stripe-signature")
        
        if not signature:
            raise HTTPException(status_code=400, detail="Missing Stripe signature")
        
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, signature, webhook_secret
        )
        
        logger.info(f"Received webhook event: {event['type']}")
        
        # Handle payment confirmation
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            api_key = payment_intent.get("metadata", {}).get("api_key")
            credits = int(payment_intent.get("metadata", {}).get("credits", 0))
            
            if api_key and api_key in api_keys:
                # Activate the API key
                api_keys[api_key]["credits"] = credits
                api_keys[api_key]["status"] = "active"
                api_keys[api_key]["activated_at"] = datetime.now()
                logger.info(f"Activated API key {api_key} with {credits} credits")
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def landing_page():
    """Landing page for the Refactor Agent API"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Refactor Agent API - AI-Powered Code Refactoring</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #333; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; color: white; padding: 60px 0; }
            .header h1 { font-size: 3.5em; margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
            .header p { font-size: 1.4em; margin-bottom: 30px; opacity: 0.9; }
            .stats { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; margin: 40px 0; text-align: center; color: white; }
            .stats h2 { margin-bottom: 20px; }
            .stat-item { display: inline-block; margin: 0 30px; }
            .stat-number { font-size: 2.5em; font-weight: bold; display: block; }
            .content { background: white; border-radius: 20px; padding: 40px; margin: 20px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            .pricing { display: flex; justify-content: space-around; gap: 30px; margin: 40px 0; flex-wrap: wrap; }
            .plan { border: 2px solid #e0e0e0; border-radius: 15px; padding: 30px; text-align: center; flex: 1; min-width: 280px; transition: transform 0.3s ease; }
            .plan:hover { transform: translateY(-5px); box-shadow: 0 15px 40px rgba(0,0,0,0.1); }
            .plan.popular { border-color: #667eea; background: linear-gradient(135deg, #f8f9ff 0%, #e6eaff 100%); position: relative; }
            .plan.popular::before { content: 'MOST POPULAR'; position: absolute; top: -10px; left: 50%; transform: translateX(-50%); background: #667eea; color: white; padding: 5px 20px; border-radius: 20px; font-size: 0.8em; font-weight: bold; }
            .plan h3 { font-size: 1.8em; margin-bottom: 10px; color: #333; }
            .plan .price { font-size: 3em; color: #667eea; margin: 20px 0; font-weight: bold; }
            .plan .price small { font-size: 0.4em; color: #666; }
            .plan .per-refactor { color: #666; font-size: 1.1em; margin-bottom: 20px; }
            .plan ul { text-align: left; margin: 20px 0; list-style: none; padding: 0; }
            .plan li { padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
            .plan li:before { content: '✓'; color: #28a745; font-weight: bold; margin-right: 10px; }
            .plan button { background: #667eea; color: white; border: none; padding: 15px 30px; border-radius: 25px; cursor: pointer; font-size: 1.1em; font-weight: bold; margin-top: 20px; transition: background 0.3s ease; width: 100%; }
            .plan button:hover { background: #5a6fd8; }
            .features { margin: 40px 0; }
            .features h2 { text-align: center; margin-bottom: 40px; font-size: 2.5em; }
            .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; }
            .feature { padding: 30px; border: 1px solid #e0e0e0; border-radius: 15px; text-align: center; }
            .feature-icon { font-size: 3em; margin-bottom: 20px; }
            .cta { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 60px 40px; border-radius: 20px; margin: 40px 0; }
            .cta h2 { font-size: 2.5em; margin-bottom: 20px; }
            .cta button { background: white; color: #667eea; border: none; padding: 20px 40px; border-radius: 25px; cursor: pointer; font-size: 1.2em; font-weight: bold; margin: 20px 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Refactor Agent API</h1>
                <p>Transform your code with AI-powered refactoring</p>
                <p>Extract utilities • Optimize performance • Add documentation • Improve style • Enhance security</p>
            </div>
            
            <div class="stats">
                <h2>Trusted by 57+ developers in just 4 days!</h2>
                <div class="stat-item">
                    <span class="stat-number">57+</span>
                    <span>GitHub Clones</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">5</span>
                    <span>Refactor Types</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">API</span>
                    <span>Ready</span>
                </div>
            </div>
            
            <div class="content">
                <div class="features">
                    <h2>🚀 Powerful AI Refactoring</h2>
                    <div class="feature-grid">
                        <div class="feature">
                            <div class="feature-icon">🧠</div>
                            <h3>Extract Utilities</h3>
                            <p>Identify and extract reusable functions into organized modules</p>
                        </div>
                        <div class="feature">
                            <div class="feature-icon">⚡</div>
                            <h3>Optimize Performance</h3>
                            <p>Improve algorithms, reduce complexity, and enhance efficiency</p>
                        </div>
                        <div class="feature">
                            <div class="feature-icon">📚</div>
                            <h3>Add Documentation</h3>
                            <p>Generate comprehensive docstrings and type hints</p>
                        </div>
                        <div class="feature">
                            <div class="feature-icon">✨</div>
                            <h3>Style Improvements</h3>
                            <p>Apply PEP 8 standards and improve code readability</p>
                        </div>
                        <div class="feature">
                            <div class="feature-icon">🔒</div>
                            <h3>Security Review</h3>
                            <p>Identify vulnerabilities and apply security best practices</p>
                        </div>
                        <div class="feature">
                            <div class="feature-icon">🎯</div>
                            <h3>Smart Analysis</h3>
                            <p>Context-aware suggestions based on your specific codebase</p>
                        </div>
                    </div>
                </div>
                
                <div class="pricing">
                    <div class="plan">
                        <h3>Starter</h3>
                        <div class="price">$9.90</div>
                        <div class="per-refactor">$0.99 per refactor</div>
                        <ul>
                            <li>10 refactor requests</li>
                            <li>All 5 refactor types</li>
                            <li>API access</li>
                            <li>Credits never expire</li>
                            <li>Perfect for trying the service</li>
                        </ul>
                        <button onclick="buyPlan(990, 'Starter')">Get Started</button>
                    </div>
                    
                    <div class="plan popular">
                        <h3>Professional</h3>
                        <div class="price">$29.90</div>
                        <div class="per-refactor">$0.60 per refactor</div>
                        <ul>
                            <li>50 refactor requests</li>
                            <li>All 5 refactor types</li>
                            <li>API access</li>
                            <li>Credits never expire</li>
                            <li>40% savings vs Starter</li>
                            <li>Best for regular use</li>
                        </ul>
                        <button onclick="buyPlan(2990, 'Professional')">Most Popular</button>
                    </div>
                    
                    <div class="plan">
                        <h3>Enterprise</h3>
                        <div class="price">$99.90</div>
                        <div class="per-refactor">$0.40 per refactor</div>
                        <ul>
                            <li>250 refactor requests</li>
                            <li>All 5 refactor types</li>
                            <li>API access</li>
                            <li>Credits never expire</li>
                            <li>60% savings vs Starter</li>
                            <li>Perfect for teams</li>
                        </ul>
                        <button onclick="buyPlan(9990, 'Enterprise')">Maximum Value</button>
                    </div>
                </div>
            </div>
            
            <div class="cta">
                <h2>Ready to transform your code?</h2>
                <p>Join the developers already using AI to write better, cleaner code</p>
                <button onclick="buyPlan(2990, 'Professional')">Start Refactoring Now</button>
                <button onclick="window.open('/docs', '_blank')" style="background: transparent; border: 2px solid white; color: white;">View API Docs</button>
            </div>
        </div>
        
        <script src="https://js.stripe.com/v3/"></script>
        <script>
        async function buyPlan(amount, planName) {
            try {
                const response = await fetch('/api/v1/payment/create-intent', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        amount: amount,
                        currency: 'usd',
                        description: `Refactor Agent ${planName} Plan`
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // Redirect to Stripe checkout or show payment form
                    alert(`Payment created! API Key: ${result.api_key}\\nCredits: ${result.credits}\\n\\nIntegrate with Stripe checkout for production.`);
                } else {
                    alert('Error: ' + result.message);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
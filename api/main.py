"""
FastAPI application for the refactor agent with Stripe integration.
Provides paid API access to the refactor agent functionality.
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=request.amount,
            currency=request.currency,
            description=request.description,
            metadata={
                "service": "refactor_agent",
                "credits": request.amount // 100  # 1 credit per dollar
            }
        )
        
        # Generate API key
        api_key = generate_api_key()
        credits = request.amount // 100  # 1 credit per dollar
        
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
                "price": 500,  # $5.00
                "credits": 5,
                "description": "5 refactor requests"
            },
            "professional": {
                "price": 2000,  # $20.00
                "credits": 25,
                "description": "25 refactor requests"
            },
            "enterprise": {
                "price": 5000,  # $50.00
                "credits": 75,
                "description": "75 refactor requests"
            }
        },
        "currency": "usd",
        "note": "Prices are in cents. 1 credit = 1 refactor request"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
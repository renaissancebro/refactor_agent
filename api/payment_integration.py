"""
Enhanced Stripe Payment Integration for Refactor Agent
Includes checkout sessions, webhook handling, and proper error handling
"""

import stripe
import os
import json
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RefactorAgentPayments:
    """Enhanced payment processing for Refactor Agent"""
    
    def __init__(self):
        self.stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        if self.stripe_secret_key:
            stripe.api_key = self.stripe_secret_key
        
        # Price mapping (update these with your actual Stripe Price IDs)
        self.price_mapping = {
            "starter": {
                "price_id": "price_starter_id_here",  # Replace with actual Stripe Price ID
                "amount": 990,
                "credits": 10,
                "name": "Starter"
            },
            "professional": {
                "price_id": "price_professional_id_here",  # Replace with actual Stripe Price ID
                "amount": 2990, 
                "credits": 50,
                "name": "Professional"
            },
            "enterprise": {
                "price_id": "price_enterprise_id_here",  # Replace with actual Stripe Price ID
                "amount": 9990,
                "credits": 250,
                "name": "Enterprise"
            }
        }
    
    def create_checkout_session(self, plan: str, success_url: str, cancel_url: str, 
                              customer_email: Optional[str] = None) -> Dict:
        """Create a Stripe Checkout session"""
        
        if plan not in self.price_mapping:
            raise ValueError(f"Invalid plan: {plan}")
        
        plan_info = self.price_mapping[plan]
        
        try:
            session_params = {
                "payment_method_types": ["card"],
                "line_items": [{
                    "price": plan_info["price_id"],
                    "quantity": 1,
                }],
                "mode": "payment",
                "success_url": success_url + "?session_id={CHECKOUT_SESSION_ID}",
                "cancel_url": cancel_url,
                "metadata": {
                    "service": "refactor_agent",
                    "plan": plan,
                    "credits": str(plan_info["credits"])
                }
            }
            
            if customer_email:
                session_params["customer_email"] = customer_email
            
            session = stripe.checkout.Session.create(**session_params)
            
            return {
                "success": True,
                "session_id": session.id,
                "checkout_url": session.url,
                "amount": plan_info["amount"],
                "credits": plan_info["credits"]
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def handle_webhook(self, payload: str, signature: str) -> Dict:
        """Handle Stripe webhook events"""
        
        if not self.webhook_secret:
            return {"status": "error", "message": "Webhook secret not configured"}
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            return {"status": "error", "message": "Invalid payload"}
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            return {"status": "error", "message": "Invalid signature"}
        
        logger.info(f"Received webhook event: {event['type']}")
        
        # Handle different event types
        if event["type"] == "checkout.session.completed":
            return self._handle_checkout_completed(event["data"]["object"])
        elif event["type"] == "payment_intent.succeeded":
            return self._handle_payment_succeeded(event["data"]["object"])
        elif event["type"] == "payment_intent.payment_failed":
            return self._handle_payment_failed(event["data"]["object"])
        else:
            return {"status": "ignored", "message": f"Unhandled event type: {event['type']}"}
    
    def _handle_checkout_completed(self, session) -> Dict:
        """Handle completed checkout session"""
        
        customer_email = session.get("customer_email")
        customer_id = session.get("customer")
        metadata = session.get("metadata", {})
        plan = metadata.get("plan")
        credits = int(metadata.get("credits", 0))
        
        logger.info(f"Checkout completed: {customer_email}, Plan: {plan}, Credits: {credits}")
        
        # Generate API key and activate credits
        api_key = self._generate_api_key()
        
        # Store in your database (implement this)
        # self.activate_api_key(api_key, credits, customer_email, customer_id)
        
        # Send confirmation email (implement this)
        # self.send_welcome_email(customer_email, api_key, credits)
        
        return {
            "status": "success",
            "message": "Checkout completed successfully",
            "api_key": api_key,
            "credits": credits
        }
    
    def _handle_payment_succeeded(self, payment_intent) -> Dict:
        """Handle successful payment"""
        
        logger.info(f"Payment succeeded: {payment_intent.get('id')}")
        
        # Additional processing if needed
        return {"status": "success", "message": "Payment processed successfully"}
    
    def _handle_payment_failed(self, payment_intent) -> Dict:
        """Handle failed payment"""
        
        logger.warning(f"Payment failed: {payment_intent.get('id')}")
        
        # Handle failed payment (notify user, etc.)
        return {"status": "failed", "message": "Payment failed"}
    
    def _generate_api_key(self) -> str:
        """Generate a unique API key"""
        import uuid
        return f"rfa_{uuid.uuid4().hex[:32]}"
    
    def get_payment_link(self, plan: str) -> str:
        """Get a payment link for a specific plan"""
        
        if plan not in self.price_mapping:
            raise ValueError(f"Invalid plan: {plan}")
        
        # Create a payment link (you can also do this in Stripe Dashboard)
        try:
            payment_link = stripe.PaymentLink.create(
                line_items=[{
                    "price": self.price_mapping[plan]["price_id"],
                    "quantity": 1,
                }],
                metadata={
                    "service": "refactor_agent",
                    "plan": plan,
                    "credits": str(self.price_mapping[plan]["credits"])
                }
            )
            
            return payment_link.url
            
        except stripe.error.StripeError as e:
            logger.error(f"Error creating payment link: {e}")
            raise e

# Test function
def test_integration():
    """Test the payment integration"""
    
    payments = RefactorAgentPayments()
    
    # Test checkout session creation
    try:
        result = payments.create_checkout_session(
            plan="professional",
            success_url="https://yourdomain.com/success",
            cancel_url="https://yourdomain.com/cancel",
            customer_email="test@example.com"
        )
        
        if result["success"]:
            print("✅ Checkout session created successfully!")
            print(f"   Session ID: {result['session_id']}")
            print(f"   Checkout URL: {result['checkout_url']}")
        else:
            print(f"❌ Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_integration()
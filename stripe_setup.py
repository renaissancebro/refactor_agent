"""
Stripe Setup Script for Refactor Agent
Run this to create products and prices in your Stripe account
"""

import stripe
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_products_and_prices():
    """Create products and prices in Stripe"""
    
    products = [
        {
            "name": "Refactor Agent - Starter",
            "description": "10 AI-powered code refactoring requests. Perfect for trying the service.",
            "price": 990,  # $9.90 in cents
            "credits": 10
        },
        {
            "name": "Refactor Agent - Professional", 
            "description": "50 AI-powered code refactoring requests. Most popular plan with 40% savings.",
            "price": 2990,  # $29.90 in cents
            "credits": 50
        },
        {
            "name": "Refactor Agent - Enterprise",
            "description": "250 AI-powered code refactoring requests. Maximum value with 60% savings.", 
            "price": 9990,  # $99.90 in cents
            "credits": 250
        }
    ]
    
    created_products = []
    
    for product_data in products:
        try:
            # Create product
            product = stripe.Product.create(
                name=product_data["name"],
                description=product_data["description"],
                metadata={
                    "credits": str(product_data["credits"]),
                    "service": "refactor_agent"
                }
            )
            
            # Create price
            price = stripe.Price.create(
                unit_amount=product_data["price"],
                currency="usd",
                product=product.id,
                metadata={
                    "credits": str(product_data["credits"])
                }
            )
            
            created_products.append({
                "product": product,
                "price": price,
                "credits": product_data["credits"]
            })
            
            print(f"✅ Created: {product.name}")
            print(f"   Product ID: {product.id}")
            print(f"   Price ID: {price.id}")
            print(f"   Amount: ${product_data['price']/100:.2f}")
            print(f"   Credits: {product_data['credits']}")
            print()
            
        except Exception as e:
            print(f"❌ Error creating {product_data['name']}: {e}")
    
    return created_products

def create_checkout_session_example():
    """Example of how to create a checkout session"""
    
    # This is how you'd create a checkout session in production
    example_code = '''
# Example checkout session creation
session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
        'price': 'price_1234567890',  # Use the price ID from Stripe
        'quantity': 1,
    }],
    mode='payment',
    success_url='https://yourdomain.com/success?session_id={{CHECKOUT_SESSION_ID}}',
    cancel_url='https://yourdomain.com/cancel',
    metadata={
        'service': 'refactor_agent',
        'credits': '50'
    }
)
'''
    print("💡 Checkout Session Example:")
    print(example_code)

if __name__ == "__main__":
    if not stripe.api_key:
        print("❌ Please set STRIPE_SECRET_KEY in your .env file")
        exit(1)
    
    print("🚀 Creating Refactor Agent products in Stripe...\n")
    
    products = create_products_and_prices()
    
    print(f"✅ Successfully created {len(products)} products!")
    print("\n" + "="*50)
    print("📋 NEXT STEPS:")
    print("1. Copy the Price IDs above")
    print("2. Update your payment integration to use these Price IDs")
    print("3. Set up webhooks in Stripe Dashboard")
    print("4. Test with test cards: 4242424242424242")
    print("="*50)
    
    create_checkout_session_example()
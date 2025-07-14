#!/bin/bash

echo "🚀 Setting up Stripe for Refactor Agent..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from sample..."
    cp .env.sample .env
    echo "⚠️  Please edit .env file with your actual Stripe keys!"
fi

# Install required packages
echo "📦 Installing required packages..."
pip install stripe python-dotenv

# Run the Stripe setup script
echo "🏗️  Creating products in Stripe..."
python stripe_setup.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 NEXT STEPS:"
echo "1. Edit .env file with your Stripe keys"
echo "2. Update price IDs in payment_integration.py"
echo "3. Set up webhook endpoint in Stripe Dashboard"
echo "4. Test with: python -m uvicorn api.main:app --reload"
echo ""
echo "🔗 Useful Links:"
echo "   Stripe Dashboard: https://dashboard.stripe.com"
echo "   Test Cards: https://stripe.com/docs/testing#cards"
echo "   Webhook Testing: https://stripe.com/docs/webhooks/test"
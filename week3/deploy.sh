#!/bin/bash

# Deployment script for Crypto Finance MCP Server

echo "======================================"
echo "Crypto Finance MCP Server Deployment"
echo "======================================"
echo ""

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI is not installed."
    echo "📦 Install it with: npm install -g vercel"
    exit 1
fi

echo "✅ Vercel CLI found"
echo ""

# Navigate to week3 directory
cd "$(dirname "$0")/.."

# Check if .env file exists
if [ ! -f "server/.env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp server/.env.example server/.env
    echo "📝 Please edit server/.env and set your MCP_API_KEY"
    echo "   You can generate a secure key with:"
    echo "   python -c \"import secrets; print(secrets.token_urlsafe(32))\""
    exit 1
fi

echo "📋 Deployment checklist:"
echo "  ✓ Vercel CLI installed"
echo "  ✓ .env file exists"
echo ""

# Ask user for confirmation
read -p "🚀 Ready to deploy? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Deploy to Vercel
echo ""
echo "🚀 Deploying to Vercel..."
echo ""

vercel --prod

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Go to Vercel dashboard: https://vercel.com/dashboard"
echo "  2. Find your project and go to Settings > Environment Variables"
echo "  3. Add MCP_API_KEY with your secure API key"
echo "  4. Redeploy for the environment variable to take effect"
echo ""
echo "🔗 Your MCP server URL will be shown above"
echo "   Use it with your AI agents and MCP clients!"

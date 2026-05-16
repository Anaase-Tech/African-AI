#!/bin/bash
# African AI - Quick Deploy Script

echo "🌍 Deploying African AI to Vercel..."

# Check if git is initialized
if [ ! -d .git ]; then
    echo "Initializing Git..."
    git init
    git add .
    git commit -m "Initial commit - African AI v2.0"
    git branch -M main
fi

# Check if remote exists
if ! git remote | grep -q origin; then
    echo "Adding GitHub remote..."
    git remote add origin https://github.com/Anaase-Tech/African-AI.git
fi

# Push to GitHub
echo "Pushing to GitHub..."
git add .
git commit -m "Update: $(date)"
git push -u origin main

echo "✅ Pushed to GitHub!"
echo "🚀 Now deploy on Vercel:"
echo "   1. Go to vercel.com"
echo "   2. Import from GitHub: Anaase-Tech/African-AI"
echo "   3. Add environment variable: GROQ_API_KEY"
echo "   4. Deploy!"

echo ""
echo "🌍 Africa rising! 🚀"

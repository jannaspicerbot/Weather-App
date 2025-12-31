#!/bin/bash
# GitHub Setup Helper Script
# This script helps you create and push your Weather App to GitHub

echo "=================================================="
echo "Weather App - GitHub Setup Helper"
echo "=================================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ ERROR: Git is not installed"
    echo "Please install Git first: https://git-scm.com/downloads"
    exit 1
fi

echo "✅ Git is installed"
echo ""

# Initialize git repository
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already initialized"
fi

echo ""
echo "=================================================="
echo "Next Steps:"
echo "=================================================="
echo ""
echo "1. Go to https://github.com/new"
echo "2. Repository name: Weather-App"
echo "3. Description: Ambient Weather data collection and visualization"
echo "4. Choose Public or Private"
echo "5. DO NOT initialize with README, .gitignore, or license"
echo "6. Click 'Create repository'"
echo ""
echo "7. Then run these commands:"
echo ""
echo "   git add ."
echo "   git commit -m 'Initial commit: Weather App with data fetching and visualization'"
echo "   git branch -M main"
echo "   git remote add origin https://github.com/YOUR_USERNAME/Weather-App.git"
echo "   git push -u origin main"
echo ""
echo "=================================================="
echo ""
echo "⚠️  IMPORTANT: Replace YOUR_USERNAME with your GitHub username"
echo ""
echo "📝 Example:"
echo "   git remote add origin https://github.com/johndoe/Weather-App.git"
echo ""
echo "=================================================="

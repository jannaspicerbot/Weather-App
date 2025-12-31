# How to Push This Project to GitHub

Follow these steps to create your "Weather App" repository on GitHub and push your code.

## Prerequisites

- A GitHub account (create one at https://github.com/signup if needed)
- Git installed on your computer
- Command line/terminal access

## Step-by-Step Instructions

### Step 1: Create a New Repository on GitHub

1. Go to https://github.com/new
2. Fill in the repository details:
   - **Repository name**: `Weather-App`
   - **Description**: `Ambient Weather data collection and visualization with Python`
   - **Visibility**: Choose Public or Private
   - **⚠️ IMPORTANT**: Do NOT check any of these boxes:
     - ❌ Add a README file
     - ❌ Add .gitignore
     - ❌ Choose a license
3. Click **"Create repository"**

### Step 2: Navigate to Your Project Directory

Open a terminal/command prompt and navigate to your weather-app directory:

```bash
cd /path/to/weather-app
```

### Step 3: Initialize Git (if not already done)

```bash
git init
```

### Step 4: Add All Files to Git

```bash
git add .
```

This adds all your project files to Git's staging area.

### Step 5: Create Your First Commit

```bash
git commit -m "Initial commit: Weather App with data fetching and visualization"
```

### Step 6: Set the Main Branch

```bash
git branch -M main
```

### Step 7: Connect to GitHub

Replace `YOUR_USERNAME` with your actual GitHub username:

```bash
git remote add origin https://github.com/YOUR_USERNAME/Weather-App.git
```

**Example**: If your username is `johndoe`:
```bash
git remote add origin https://github.com/johndoe/Weather-App.git
```

### Step 8: Push to GitHub

```bash
git push -u origin main
```

You may be prompted to authenticate:
- Enter your GitHub username
- For password, use a **Personal Access Token** (not your GitHub password)

### Step 9: Verify

Go to `https://github.com/YOUR_USERNAME/Weather-App` in your browser to see your code!

## Creating a Personal Access Token (if needed)

If you don't have a Personal Access Token:

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: `Weather App`
4. Set expiration (recommend 90 days)
5. Check the **`repo`** scope
6. Click **"Generate token"**
7. **Copy the token immediately** (you won't see it again!)
8. Use this token as your password when pushing

## Future Updates

After the initial push, to update your repository:

```bash
git add .
git commit -m "Description of your changes"
git push
```

## Quick Reference

```bash
# Stage all changes
git add .

# Commit with message
git commit -m "Your message here"

# Push to GitHub
git push

# Check status
git status

# View commit history
git log --oneline
```

## Troubleshooting

### "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/Weather-App.git
```

### Authentication failed
- Make sure you're using a Personal Access Token, not your password
- Check that your username is correct

### Permission denied
- Verify you have access to the repository
- Check that the repository URL is correct

## Need Help?

- GitHub Documentation: https://docs.github.com
- Git Basics: https://git-scm.com/book/en/v2/Getting-Started-Git-Basics

---

**Note**: Remember to never commit your actual API keys! The `.gitignore` file is configured to protect your secrets, but always double-check before committing.

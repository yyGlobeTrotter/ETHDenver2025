#!/bin/bash

# Script to prepare files for Vercel deployment

echo "Preparing files for Vercel deployment..."

# Create directories if they don't exist
mkdir -p api/static

# Copy index.html to api directory
cp index.html api/

# Copy static files to api/static directory
cp -r static/* api/static/

echo "Files prepared for Vercel deployment!"
echo "You can now deploy to Vercel with 'vercel' or by pushing to GitHub." 
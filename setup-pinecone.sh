#!/bin/bash

# Setup script for Pinecone and MongoDB integration
# Run this after adding your API keys to .env

set -e  # Exit on error

echo "========================================="
echo "Reflection - Pinecone Setup Script"
echo "========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys:"
    echo "   - PINECONE_API_KEY"
    echo "   - GOOGLE_API_KEY"
    echo "   - MONGODB_URI (if not using default)"
    echo ""
    read -p "Press Enter after updating .env file..."
fi

echo ""
echo "Step 1: Installing File Parsing Service dependencies..."
echo "========================================="
cd services/file-parsing
pip install -r requirements.txt
cd ../..
echo "✅ File Parsing Service dependencies installed"
echo ""

echo "Step 2: Installing QA Generation Service dependencies..."
echo "========================================="
cd services/question-answer-generation
pip install -r requirements.txt
cd ../..
echo "✅ QA Generation Service dependencies installed"
echo ""

echo "Step 3: Verifying MongoDB connection..."
echo "========================================="
if command -v mongod &> /dev/null; then
    echo "✅ MongoDB is installed"
    
    # Check if MongoDB is running
    if pgrep -x "mongod" > /dev/null; then
        echo "✅ MongoDB is running"
    else
        echo "⚠️  MongoDB is not running"
        echo "Start MongoDB with: sudo systemctl start mongod"
    fi
else
    echo "⚠️  MongoDB not found. Please install MongoDB:"
    echo "   Ubuntu/Debian: sudo apt-get install mongodb"
    echo "   MacOS: brew install mongodb-community"
fi
echo ""

echo "Step 4: Testing Pinecone connection..."
echo "========================================="
python3 << EOF
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('PINECONE_API_KEY')
if api_key and api_key != 'your-pinecone-api-key-here':
    print("✅ PINECONE_API_KEY found in .env")
    
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=api_key)
        indexes = pc.list_indexes()
        print(f"✅ Connected to Pinecone successfully")
        print(f"   Existing indexes: {[idx['name'] for idx in indexes]}")
        
        # Check if our index exists
        index_name = os.getenv('PINECONE_INDEX', 'reflection-documents')
        if index_name not in [idx['name'] for idx in indexes]:
            print(f"⚠️  Index '{index_name}' not found")
            print(f"   It will be created automatically on first use")
        else:
            print(f"✅ Index '{index_name}' exists")
            
    except Exception as e:
        print(f"❌ Pinecone connection failed: {e}")
        print("   Please check your PINECONE_API_KEY")
else:
    print("⚠️  PINECONE_API_KEY not set in .env")
    print("   Add your Pinecone API key to .env file")
EOF
echo ""

echo "Step 5: Testing Google Gemini API..."
echo "========================================="
python3 << EOF
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
if api_key and api_key != 'your-google-gemini-api-key-here':
    print("✅ GOOGLE_API_KEY found in .env")
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.0-flash",
            google_api_key=api_key
        )
        print("✅ Google Gemini API initialized successfully")
    except Exception as e:
        print(f"❌ Gemini initialization failed: {e}")
        print("   Please check your GOOGLE_API_KEY")
else:
    print("⚠️  GOOGLE_API_KEY not set in .env")
    print("   Add your Google Gemini API key to .env file")
EOF
echo ""

echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Ensure MongoDB is running: sudo systemctl start mongod"
echo "2. Start services: ./start-services.sh"
echo "3. Login to the application"
echo "4. Upload resume and job description"
echo "5. Check practice page for user-specific questions"
echo ""
echo "For troubleshooting, see IMPLEMENTATION_SUMMARY.md"
echo ""

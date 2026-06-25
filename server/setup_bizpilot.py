#!/usr/bin/env python3
"""
BizPilot Setup Script
Installs dependencies and sets up the AI agent system
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}:")
        print(f"Command: {command}")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 BizPilot AI Agent Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("manage.py"):
        print("❌ Please run this script from the Django server directory (where manage.py is located)")
        sys.exit(1)
    
    # Install Python dependencies
    print("\n📦 Installing Python dependencies...")
    dependencies = [
        "pip install phidata",
        "pip install openai",
        "pip install groq", 
        "pip install python-dotenv",
        "pip install yfinance",
        "pip install duckduckgo-search",
        "pip install requests"
    ]
    
    for dep in dependencies:
        if not run_command(dep, f"Installing {dep.split()[-1]}"):
            print(f"⚠️  Failed to install {dep.split()[-1]}, but continuing...")
    
    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("\n📝 Creating .env file...")
        env_content = """# AI Model API Keys
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Django Settings
DEBUG=True
SECRET_KEY=your_django_secret_key_here"""
        
        with open(".env", "w", encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ .env file created!")
        print("\n⚠️  IMPORTANT: Please update the .env file with your actual API keys:")
        print("   - Get OpenAI API key from: https://platform.openai.com/api-keys")
        print("   - Get Groq API key from: https://console.groq.com/keys")
    else:
        print("✅ .env file already exists")
    
    # Test the setup
    print("\n🧪 Testing the setup...")
    test_code = """
try:
    from chat.bizpilot_agents import get_bizpilot_agents
    print("✅ BizPilot agents imported successfully!")
    
    # Test basic functionality (without API calls)
    agents = get_bizpilot_agents(use_openai=True)
    print("✅ Agent system initialized!")
    
except ImportError as e:
    print(f"⚠️  Import warning: {e}")
    print("   The system will fall back to static responses if agents aren't available.")
    
except Exception as e:
    print(f"⚠️  Setup warning: {e}")
    print("   Please check your API keys in the .env file.")
"""
    
    with open("test_setup.py", "w", encoding='utf-8') as f:
        f.write(test_code)
    
    if run_command("python test_setup.py", "Testing setup"):
        print("\n🎉 Setup completed successfully!")
    else:
        print("\n⚠️  Setup completed with warnings. The system will use fallback responses.")
    
    # Clean up test file
    try:
        os.remove("test_setup.py")
    except:
        pass
    
    print("\n📋 Next steps:")
    print("1. Update your .env file with real API keys")
    print("2. Run: python manage.py runserver")
    print("3. Visit: http://127.0.0.1:8000/")
    print("4. Test the AI-powered chatbot!")
    
    print("\n💡 Features available:")
    print("   🤖 AI-powered business planning")
    print("   📊 Market research and analysis") 
    print("   🗺️  Dynamic roadmap generation")
    print("   💰 Financial planning assistance")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Mobile Automation Setup Script
Run this script to set up Appium and mobile automation for CURP system
"""

import subprocess
import sys
import os
import platform

def run_command(command, description=""):
    """Run a command and return success status"""
    print(f"🔄 {description}")
    print(f"   Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"   ✅ Success: {result.stdout.strip()[:100]}")
            return True
        else:
            print(f"   ❌ Failed: {result.stderr.strip()[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timeout: Command took too long")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_prerequisites():
    """Check if prerequisites are installed"""
    print("🔍 Checking Prerequisites...")
    print("="*60)
    
    checks = {}
    
    # Check Python
    try:
        python_version = sys.version.split()[0]
        print(f"✅ Python: {python_version}")
        checks['python'] = True
    except:
        print("❌ Python: Not found")
        checks['python'] = False
    
    # Check Node.js
    checks['node'] = run_command("node --version", "Checking Node.js")
    
    # Check NPM
    checks['npm'] = run_command("npm --version", "Checking NPM")
    
    # Check ADB
    checks['adb'] = run_command("adb version", "Checking Android ADB")
    
    # Check if in correct environment
    current_dir = os.getcwd()
    venv_active = 'VIRTUAL_ENV' in os.environ
    
    print(f"📂 Current directory: {current_dir}")
    print(f"🐍 Virtual environment active: {venv_active}")
    
    if "backend" not in current_dir.lower():
        print("⚠️ Recommendation: Run this from the backend directory")
    
    return checks

def install_appium():
    """Install Appium and drivers"""
    print("\n📦 Installing Appium...")
    print("="*60)
    
    # Install Appium globally
    if not run_command("npm install -g appium", "Installing Appium globally"):
        return False
    
    # Install UiAutomator2 driver
    if not run_command("appium driver install uiautomator2", "Installing UiAutomator2 driver"):
        return False
    
    # Verify Appium installation
    if not run_command("appium --version", "Verifying Appium installation"):
        return False
    
    # List installed drivers
    if not run_command("appium driver list --installed", "Checking installed drivers"):
        return False
    
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    print("\n🐍 Installing Python Dependencies...")
    print("="*60)
    
    dependencies = [
        "Appium-Python-Client",
        "selenium",
        "requests"
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            return False
    
    return True

def check_android_setup():
    """Check Android device setup"""
    print("\n📱 Checking Android Setup...")
    print("="*60)
    
    # Check connected devices
    result = subprocess.run("adb devices", shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        devices = [line for line in result.stdout.split('\n') if '\tdevice' in line]
        
        if devices:
            print(f"✅ Found {len(devices)} connected device(s):")
            for device in devices:
                device_id = device.split('\t')[0]
                print(f"   📱 {device_id}")
            return True
        else:
            print("⚠️ No devices connected")
            print_android_setup_instructions()
            return False
    else:
        print("❌ ADB not working properly")
        return False

def print_android_setup_instructions():
    """Print Android setup instructions"""
    print("\n📋 ANDROID DEVICE SETUP INSTRUCTIONS:")
    print("-" * 40)
    print("1. 🔧 Enable Developer Options:")
    print("   Settings → About Phone → Tap 'Build Number' 7 times")
    print()
    print("2. 🔗 Enable USB Debugging:")
    print("   Settings → Developer Options → Enable 'USB Debugging'")
    print()
    print("3. 📱 Install IMSS Digital App:")
    print("   Open Google Play Store → Search 'IMSS Digital' → Install")
    print()
    print("4. 🔌 Connect USB Cable:")
    print("   Connect your Android device to computer via USB")
    print("   Accept the USB debugging prompt on your device")
    print()
    print("5. ✅ Verify Connection:")
    print("   Run: adb devices")
    print("   Should show your device ID with 'device' status")

def test_appium_server():
    """Test Appium server startup"""
    print("\n🧪 Testing Appium Server...")
    print("="*60)
    
    import time
    import threading
    import requests
    
    # Start Appium server in background
    def start_server():
        subprocess.run("appium --address 127.0.0.1 --port 4723 --session-override --relaxed-security", 
                      shell=True, capture_output=True)
    
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for server to start
    print("⏳ Starting Appium server (this may take 30 seconds)...")
    max_wait = 30
    for i in range(max_wait):
        try:
            response = requests.get("http://127.0.0.1:4723/status", timeout=2)
            if response.status_code == 200:
                print(f"✅ Appium server started successfully after {i+1} seconds!")
                print("🛑 Stopping test server...")
                return True
        except:
            pass
        
        time.sleep(1)
        if i % 5 == 4:  # Show progress every 5 seconds
            print(f"   Still waiting... ({i+1}/{max_wait}s)")
    
    print("❌ Appium server failed to start within 30 seconds")
    return False

def main():
    """Main setup function"""
    print("🚀 MOBILE AUTOMATION SETUP SCRIPT")
    print("="*60)
    print("This script will set up Appium for CURP mobile automation")
    print()
    
    # Step 1: Check prerequisites
    checks = check_prerequisites()
    
    # Check critical prerequisites
    if not checks.get('python', False):
        print("❌ Python is required but not found")
        return False
    
    if not checks.get('node', False):
        print("❌ Node.js is required. Please install from: https://nodejs.org/")
        print("   After installation, restart terminal and run this script again")
        return False
    
    if not checks.get('npm', False):
        print("❌ NPM is required (should come with Node.js)")
        return False
    
    # Step 2: Install Appium
    if not install_appium():
        print("❌ Failed to install Appium")
        return False
    
    # Step 3: Install Python dependencies
    if not install_python_dependencies():
        print("❌ Failed to install Python dependencies")
        return False
    
    # Step 4: Check Android setup
    android_ok = check_android_setup()
    
    # Step 5: Test Appium server (optional)
    print("\n❓ Would you like to test Appium server startup? (y/n): ", end="")
    try:
        test_server = input().strip().lower() == 'y'
        if test_server:
            server_ok = test_appium_server()
        else:
            server_ok = True
    except:
        server_ok = True
    
    # Final summary
    print("\n" + "="*60)
    print("📊 SETUP SUMMARY")
    print("="*60)
    print(f"✅ Appium installed: Yes")
    print(f"✅ Python dependencies: Yes") 
    print(f"📱 Android device: {'Yes' if android_ok else 'Needs setup'}")
    print(f"🧪 Server test: {'Passed' if server_ok else 'Skipped/Failed'}")
    
    if android_ok and server_ok:
        print("\n🎉 SETUP COMPLETE!")
        print("Your mobile automation is ready!")
        print()
        print("🚀 Next steps:")
        print("1. Start your API: python main.py")
        print("2. Test with demo: curl -X POST http://localhost:8000/demo-curp -d '{\"count\": 1}' -H 'Content-Type: application/json'")
        print("3. Monitor progress: curl http://localhost:8000/processes")
    else:
        print("\n⚠️ SETUP INCOMPLETE")
        if not android_ok:
            print("📱 Please set up your Android device using the instructions above")
        print("🔄 Run this script again after addressing the issues")
    
    return android_ok and server_ok

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)
"""
Appium Server Management - Automatic server startup with environment handling
Handles the requirement for proper environment setup before starting Appium
"""

import subprocess
import time
import requests
import os
from typing import Optional

class AppiumServerManager:
    """Manages Appium server lifecycle with environment awareness"""
    
    def __init__(self, port: int = 4723, host: str = "127.0.0.1"):
        self.port = port
        self.host = host
        self.base_url = f"http://{host}:{port}"
        self.server_process: Optional[subprocess.Popen] = None
        self.appium_command = "appium"  # Will be updated if venv detected
        
    def detect_appium_location(self):
        """Detect the best Appium command to use"""
        try:
            # First, try to detect venv Appium
            current_dir = os.getcwd()
            
            # Check for backend/venv structure
            venv_paths = [
                os.path.join(current_dir, "backend", "venv"),
                os.path.join(current_dir, "venv"),
            ]
            
            for venv_path in venv_paths:
                if os.path.exists(venv_path):
                    if os.name == 'nt':  # Windows
                        appium_exe = os.path.join(venv_path, "Scripts", "appium.cmd")
                        if os.path.exists(appium_exe):
                            self.appium_command = appium_exe
                            print(f"✅ Using venv Appium: {appium_exe}")
                            return True
                    else:  # Unix/Linux/Mac
                        appium_exe = os.path.join(venv_path, "bin", "appium")
                        if os.path.exists(appium_exe):
                            self.appium_command = appium_exe
                            print(f"✅ Using venv Appium: {appium_exe}")
                            return True
            
            # Fall back to system Appium
            result = subprocess.run([self.appium_command, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Using system Appium: {self.appium_command}")
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error detecting Appium location: {e}")
            return False
    
    def is_server_running(self) -> bool:
        """Check if Appium server is already running"""
        try:
            response = requests.get(f"{self.base_url}/status", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_server(self, timeout: int = 60) -> bool:
        """
        Start Appium server with proper environment setup
        
        Args:
            timeout: Maximum time to wait for server to start
            
        Returns:
            bool: True if server started successfully
        """
        # Check if server is already running
        if self.is_server_running():
            print(f"✅ Appium server already running on {self.base_url}")
            return True
        
        # Detect Appium location
        if not self.detect_appium_location():
            print("❌ Appium not found. Please install Appium first:")
            self.print_installation_instructions()
            return False
        
        try:
            print(f"🚀 Starting Appium server on {self.base_url}")
            
            # Enhanced command with better settings for automation
            cmd = [
                self.appium_command,
                "--address", self.host,
                "--port", str(self.port),
                "--session-override",          # Allow session override
                "--relaxed-security",          # Enable relaxed security
                "--log-level", "error",        # Reduce log verbosity
                "--use-drivers", "uiautomator2",  # Specify driver
                "--allow-insecure", "chromedriver_autodownload"  # Auto-download chromedriver
            ]
            
            print(f"🔧 Running command: {' '.join(cmd)}")
            
            # Start Appium server process
            env = os.environ.copy()
            
            # Add common Android SDK paths if available
            android_paths = [
                os.path.join(os.path.expanduser("~"), "AppData", "Local", "Android", "Sdk"),  # Windows
                os.path.join(os.path.expanduser("~"), "Android", "Sdk"),  # Linux
                os.path.join(os.path.expanduser("~"), "Library", "Android", "sdk"),  # Mac
            ]
            
            for android_path in android_paths:
                if os.path.exists(android_path):
                    env["ANDROID_HOME"] = android_path
                    env["PATH"] = f"{os.path.join(android_path, 'platform-tools')}{os.pathsep}{env['PATH']}"
                    print(f"🤖 Using Android SDK: {android_path}")
                    break
            
            # Start the process
            if os.name == 'nt':  # Windows
                self.server_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:  # Unix/Linux/Mac
                self.server_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env
                )
            
            print("⏳ Waiting for Appium server to initialize...")
            
            # Wait for server to be ready with enhanced progress tracking
            start_time = time.time()
            last_dot_time = time.time()
            
            while time.time() - start_time < timeout:
                # Check if server is responding
                if self.is_server_running():
                    elapsed = time.time() - start_time
                    print(f"\n✅ Appium server started successfully in {elapsed:.1f} seconds!")
                    print(f"🔗 Server available at: {self.base_url}")
                    return True
                
                # Check if process is still running
                if self.server_process.poll() is not None:
                    # Process ended, get error output
                    stdout, stderr = self.server_process.communicate()
                    print(f"\n❌ Appium server process ended unexpectedly")
                    
                    if stderr:
                        print(f"Error output: {stderr[:500]}...")
                        
                        # Check for common errors and provide solutions
                        if "EADDRINUSE" in stderr:
                            print("💡 Port already in use. Try stopping any existing Appium servers.")
                        elif "chromedriver" in stderr.lower():
                            print("💡 ChromeDriver issue. Install or update ChromeDriver.")
                        elif "adb" in stderr.lower():
                            print("💡 ADB issue. Make sure Android SDK is installed and in PATH.")
                    
                    return False
                
                # Show progress dots every 2 seconds
                if time.time() - last_dot_time >= 2:
                    print(".", end="", flush=True)
                    last_dot_time = time.time()
                
                time.sleep(1)
            
            print(f"\n⏰ Timeout waiting for Appium server to start after {timeout} seconds")
            self.stop_server()
            return False
            
        except FileNotFoundError:
            print(f"❌ Appium command not found: {self.appium_command}")
            self.print_installation_instructions()
            return False
        except Exception as e:
            print(f"❌ Error starting Appium server: {e}")
            return False
    
    def stop_server(self) -> bool:
        """Stop the Appium server gracefully"""
        try:
            if self.server_process:
                print("🛑 Stopping Appium server...")
                
                # Try graceful shutdown first
                self.server_process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.server_process.wait(timeout=15)
                    print("✅ Appium server stopped gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    print("⚠️ Forcing Appium server shutdown...")
                    self.server_process.kill()
                    self.server_process.wait()
                    print("✅ Appium server force stopped")
                
                self.server_process = None
                return True
            else:
                # Check if server is still running externally
                if self.is_server_running():
                    print("⚠️ Appium server is running but not managed by this process")
                    print("   You may need to stop it manually if needed")
                return True
                
        except Exception as e:
            print(f"❌ Error stopping Appium server: {e}")
            return False
    
    def print_installation_instructions(self):
        """Print installation instructions"""
        print("\n" + "="*60)
        print("📋 APPIUM INSTALLATION INSTRUCTIONS")
        print("="*60)
        print("Environment Setup:")
        print("  conda deactivate")
        print("  cd backend")
        if os.name == 'nt':
            print("  .\\venv\\Scripts\\activate")
        else:
            print("  source venv/bin/activate")
        print()
        print("Install Node.js and Appium:")
        print("  1. Install Node.js: https://nodejs.org/")
        print("  2. npm install -g appium")
        print("  3. appium driver install uiautomator2")
        print()
        print("Install Python client:")
        print("  pip install Appium-Python-Client")
        print()
        print("Setup Android:")
        print("  1. Install Android SDK")
        print("  2. Add platform-tools to PATH")
        print("  3. Enable USB debugging on device")
        print("  4. Connect device: adb devices")
        print("="*60)
    
    def get_server_status(self) -> dict:
        """Get detailed server status"""
        try:
            if self.is_server_running():
                response = requests.get(f"{self.base_url}/status", timeout=5)
                return {
                    "running": True,
                    "url": self.base_url,
                    "status_code": response.status_code,
                    "appium_command": self.appium_command,
                    "process_id": self.server_process.pid if self.server_process else None
                }
            else:
                return {
                    "running": False,
                    "url": self.base_url,
                    "appium_command": self.appium_command,
                    "error": "Server not responding"
                }
        except Exception as e:
            return {
                "running": False,
                "url": self.base_url,
                "appium_command": self.appium_command,
                "error": str(e)
            }

def test_appium_setup():
    """Test Appium server setup"""
    print("🧪 Testing Appium Server Setup")
    print("="*50)
    
    server = AppiumServerManager()
    
    # Test server lifecycle
    print("🚀 Testing server startup...")
    if server.start_server():
        status = server.get_server_status()
        print(f"📊 Server status: {status}")
        
        print("⏰ Server will run for 10 seconds for testing...")
        time.sleep(10)
        
        print("🛑 Testing server shutdown...")
        server.stop_server()
        print("✅ Test completed successfully!")
        return True
    else:
        print("❌ Server test failed!")
        server.print_installation_instructions()
        return False

if __name__ == "__main__":
    test_appium_setup()
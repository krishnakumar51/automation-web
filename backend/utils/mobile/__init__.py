"""
Simplified Mobile Automation - Connects to manually started Appium server
No automatic server management - expects server to be running on localhost:4723
"""

import time
import sqlite3

def start_mobile_automation(process_id: str, curp_id: str, email: str, first_name: str, last_name: str) -> bool:
    """
    SIMPLIFIED: Connect to manually started Appium server and run IMSS automation
    
    Prerequisites:
    1. Start Appium server manually in separate terminal:
       conda deactivate
       cd backend
       .\venv\Scripts\activate
       appium
    
    2. Connect Android device with USB debugging enabled
    3. Install IMSS Digital app on device
    
    Args:
        process_id: Process UUID from database
        curp_id: CURP ID to process  
        email: Email address from Outlook account
        first_name: User's first name
        last_name: User's last name
    
    Returns:
        bool: Success status
    """
    
    try:
        print(f"📱 Starting mobile automation for process {process_id}")
        print(f"🆔 CURP: {curp_id}")
        print(f"📧 Email: {email}")
        print(f"👤 Name: {first_name} {last_name}")
        
        # Update IMSS processing status to 'in_progress'
        update_imss_status(process_id, "in_progress", "Connecting to Appium server")
        
        # Check if Appium server is running
        import requests
        try:
            response = requests.get("http://localhost:4723/status", timeout=5)
            if response.status_code == 200:
                print("✅ Found running Appium server on http://localhost:4723")
            else:
                raise Exception("Appium server not responding properly")
        except:
            raise Exception("No Appium server found on http://localhost:4723")
        
        # Import and run IMSS automation 
        try:
            from .imss_automation import run_imss_automation
            print("✅ IMSS automation module imported")
        except ImportError:
            raise Exception("IMSS automation module not found - check utils/mobile/imss_automation.py")
        
        # Run IMSS automation (connects to existing server)
        print(f"🏥 Starting IMSS automation for CURP: {curp_id}")
        
        result = run_imss_automation(curp_id=curp_id, email=email, debug=False)
        
        if result:
            print("✅ IMSS automation completed successfully!")
            update_imss_status(process_id, "completed", "IMSS automation finished successfully")
            return True
        else:
            raise Exception("IMSS automation workflow failed")
            
    except Exception as e:
        error_msg = f"Mobile automation failed: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Provide helpful error messages
        if "No Appium server found" in str(e):
            print("\n" + "="*60)
            print("🚨 APPIUM SERVER NOT RUNNING")
            print("="*60)
            print("Please start Appium server manually in a separate terminal:")
            print()
            print("1. Open new terminal")
            print("2. conda deactivate")
            print("3. cd backend")
            print("4. .\\venv\\Scripts\\activate")
            print("5. appium")
            print()
            print("Then retry the CURP automation.")
            print("="*60)
        
        update_imss_status(process_id, "failed", error_msg)
        return False

def update_imss_status(process_id: str, status: str, message: str = ""):
    """Update IMSS processing status in database"""
    try:
        conn = sqlite3.connect('curp_automation.db')
        cursor = conn.cursor()
        
        if status == "completed":
            cursor.execute('''
            UPDATE imss_processing 
            SET status = ?, completed_at = CURRENT_TIMESTAMP
            WHERE process_id = ?
            ''', (status, process_id))
        elif status == "failed":
            cursor.execute('''
            UPDATE imss_processing 
            SET status = ?, error_message = ?
            WHERE process_id = ?
            ''', (status, message, process_id))
        else:
            cursor.execute('''
            UPDATE imss_processing 
            SET status = ?
            WHERE process_id = ?
            ''', (status, process_id))
        
        conn.commit()
        conn.close()
        print(f"📊 Updated IMSS status to: {status}")
        
    except Exception as e:
        print(f"⚠️ Failed to update IMSS status: {e}")

def check_appium_server() -> dict:
    """Check if Appium server is running and return status"""
    try:
        import requests
        response = requests.get("http://localhost:4723/status", timeout=5)
        if response.status_code == 200:
            return {
                "running": True,
                "message": "Appium server is running on http://localhost:4723"
            }
        else:
            return {
                "running": False,
                "message": f"Appium server responded with status {response.status_code}"
            }
    except Exception as e:
        return {
            "running": False,
            "message": f"Cannot connect to Appium server: {str(e)}"
        }

def test_mobile_setup():
    """Test if mobile automation is ready"""
    print("🧪 Testing Mobile Automation Setup")
    print("="*50)
    
    # Check Appium server
    server_status = check_appium_server()
    if server_status["running"]:
        print("✅ Appium server is running")
    else:
        print(f"❌ Appium server issue: {server_status['message']}")
        print("\n📋 TO START APPIUM SERVER:")
        print("1. Open new terminal")
        print("2. conda deactivate")
        print("3. cd backend") 
        print("4. .\\venv\\Scripts\\activate")
        print("5. appium")
        return False
    
    # Check IMSS automation module
    try:
        from .imss_automation import run_imss_automation
        print("✅ IMSS automation module available")
    except ImportError as e:
        print(f"❌ IMSS automation module not found: {e}")
        return False
    
    # Check Android device
    try:
        import subprocess
        result = subprocess.run("adb devices", shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            devices = [line for line in result.stdout.split('\n') if '\tdevice' in line]
            if devices:
                print(f"✅ Found {len(devices)} connected Android device(s)")
            else:
                print("⚠️ No Android devices connected")
                print("   Connect device with USB debugging enabled")
        else:
            print("⚠️ ADB not available - Android SDK needed")
    except:
        print("⚠️ Cannot check Android devices")
    
    return server_status["running"]

if __name__ == "__main__":
    test_mobile_setup()
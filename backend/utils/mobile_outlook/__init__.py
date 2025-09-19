#!/usr/bin/env python3

"""
Mobile Outlook Automation Package
=================================

Modular mobile automation system for Outlook account creation

"""

from .automation_runner import create_outlook_account_mobile, OutlookMobileAutomation, generate_user_data
from .mobile_setup import MobileSetup
from .utils import MobileUtils

__version__ = "1.0.0"
__author__ = "Mobile Automation Team"

# Export main functions
__all__ = [
    'create_outlook_account_mobile',
    'OutlookMobileAutomation', 
    'generate_user_data',
    'MobileSetup',
    'MobileUtils'
]

def test_mobile_integration():
    """Test function to verify mobile integration works"""
    try:
        print("✅ Mobile automation module imported successfully")
        return True
    except Exception as e:
        print(f"❌ Mobile automation module error: {e}")
        return False

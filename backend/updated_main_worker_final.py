

# def curp_automation_worker(curp_data: dict, process_id: str):
#     """
#     CORRECTED CURP-to-PDF automation worker with proper database progress handling
    
#     WORKFLOW:
#     1. Create Outlook account (your working code)
#     2. Trigger mobile IMSS automation (with proper error handling)
#     3. Set correct progress based on actual completion status
#     4. Only proceed to email monitoring if mobile succeeds OR is not available
    
#     PROGRESS LOGIC:
#     - Outlook only: 50% (if mobile not available)
#     - Outlook + Mobile: 100% (if both succeed)
#     - Failed: 0% (if anything critical fails)
#     """
#     try:
#         add_log(f"🚀 Starting CURP automation for {curp_data['curp_id']}", process_id)
        
#         # ==========================================
#         # PHASE 1: CREATE OUTLOOK ACCOUNT  
#         # ==========================================
#         add_log("📧 Phase 1: Creating Outlook account", process_id)
#         update_master_process_status(process_id, "in_progress", "outlook_creation", 10, 
#                                    logs=f"Starting Outlook account creation for {curp_data['first_name']} {curp_data['last_name']}")
        
#         # Generate Outlook account data based on personal info
#         outlook_data = generate_outlook_data(
#             curp_data['first_name'], 
#             curp_data['last_name'], 
#             curp_data['date_of_birth']
#         )
        
#         # Store outlook account entry in database
#         store_outlook_account(process_id, outlook_data, "pending")
#         add_log(f"Generated Outlook credentials - Email: {outlook_data['email']}", process_id)
        
#         # Execute Outlook automation using your working code
#         outlook_success = False
#         try:
#             with pw.sync_playwright() as playwright:
#                 add_log("Playwright context initialized for Outlook creation", process_id)
                
#                 # Use your exact working Outlook creation function
#                 result = create_outlook_account(
#                     playwright,
#                     outlook_data['username'],
#                     outlook_data['password'],
#                     outlook_data['birth_month'],
#                     outlook_data['birth_day'],
#                     outlook_data['birth_year'],
#                     curp_data['first_name'],
#                     curp_data['last_name']
#                 )
                
#                 if result:
#                     outlook_success = True
#                     add_log(f"✅ Outlook account created successfully: {outlook_data['email']}", process_id)
                    
#                     # Update database status
#                     update_outlook_account_status(process_id, "completed")
#                     update_master_process_status(process_id, "in_progress", "outlook_completed", 35, 
#                                                email=outlook_data['email'],
#                                                logs="Outlook account created - Checking mobile automation availability")
#                 else:
#                     raise Exception("Outlook account creation returned False")
                    
#         except Exception as outlook_error:
#             add_log(f"❌ Outlook creation failed: {str(outlook_error)}", process_id)
#             update_outlook_account_status(process_id, "failed", str(outlook_error))
#             raise outlook_error
        
#         # ==========================================
#         # PHASE 2: MOBILE IMSS AUTOMATION (CORRECTED)
#         # ==========================================
#         if outlook_success:
#             add_log("📱 Phase 2: Checking mobile IMSS automation", process_id)
#             update_master_process_status(process_id, "in_progress", "checking_mobile", 40,
#                                        logs="Outlook completed - Checking mobile automation availability")
            
#             # Store IMSS processing entry
#             store_imss_processing(process_id, curp_data['curp_id'], outlook_data['email'])
            
#             # CORRECTED: Use the fixed trigger function with proper error handling
#             mobile_result = None
#             try:
#                 # Import the CORRECTED trigger function
#                 from utils.outlook import trigger_mobile_automation_if_available
                
#                 add_log("Mobile automation trigger imported successfully", process_id)
                
#                 # Call the corrected trigger function
#                 mobile_result = trigger_mobile_automation_if_available(
#                     process_id=process_id,
#                     curp_id=curp_data['curp_id'],
#                     email=outlook_data['email'],
#                     first_name=curp_data['first_name'],
#                     last_name=curp_data['last_name']
#                 )
                
#                 # Handle result based on status
#                 if mobile_result["success"]:
#                     # Mobile automation succeeded
#                     add_log("✅ Mobile IMSS automation completed successfully", process_id)
#                     update_imss_status(process_id, "completed", "Mobile automation completed")
                    
#                     # CORRECTED: Set to completed with 100% progress
#                     update_master_process_status(process_id, "completed", "imss_completed", 100,
#                                                logs="Mobile IMSS automation completed successfully - Process complete")
                    
#                     add_log(f"🎉 CURP automation FULLY completed for {curp_data['curp_id']}", process_id)
                    
#                 else:
#                     # Mobile automation failed or not available
#                     add_log(f"⚠️ Mobile automation issue: {mobile_result['message']}", process_id)
                    
#                     # Handle different failure types
#                     if mobile_result["status"] == "module_not_available":
#                         # Mobile module not available - this is OK for development
#                         add_log("Mobile automation not set up - completing with Outlook only", process_id)
#                         update_imss_status(process_id, "skipped", "Mobile automation module not available")
                        
#                         # CORRECTED: Set to completed but only 50% (Outlook only)
#                         update_master_process_status(process_id, "completed", "outlook_only", 50,
#                                                    logs="Process completed with Outlook only - Mobile automation not available")
                        
#                     elif mobile_result["status"] == "appium_not_installed":
#                         # Appium not installed - this needs setup
#                         add_log("❌ Appium not installed - mobile automation failed", process_id)
#                         update_imss_status(process_id, "failed", mobile_result["message"])
                        
#                         # CORRECTED: Set to partial completion (Outlook works, mobile needs setup)
#                         update_master_process_status(process_id, "partial", "appium_setup_needed", 35,
#                                                    logs="Outlook completed but Appium setup needed for mobile automation")
                        
#                     else:
#                         # Other mobile automation errors
#                         add_log(f"❌ Mobile automation failed: {mobile_result['status']}", process_id)
#                         update_imss_status(process_id, "failed", mobile_result["message"])
                        
#                         # CORRECTED: Set to partial completion
#                         update_master_process_status(process_id, "partial", "mobile_failed", 35,
#                                                    logs=f"Outlook completed but mobile automation failed: {mobile_result['message']}")
                    
#                     add_log(f"📊 CURP automation PARTIALLY completed for {curp_data['curp_id']}", process_id)
                    
#             except ImportError as ie:
#                 # Trigger function not available
#                 error_msg = f"Mobile automation trigger not available: {str(ie)}"
#                 add_log(f"⚠️ {error_msg}", process_id)
#                 update_imss_status(process_id, "skipped", "Mobile automation trigger not available")
                
#                 # CORRECTED: Set to completed but only 50% (Outlook only)
#                 update_master_process_status(process_id, "completed", "outlook_only", 50,
#                                            logs="Process completed with Outlook only - Mobile automation not available")
                
#                 add_log(f"📊 CURP automation PARTIALLY completed for {curp_data['curp_id']}", process_id)
                
#             except Exception as me:
#                 # Unexpected error with mobile automation trigger
#                 error_msg = f"Mobile automation trigger error: {str(me)}"
#                 add_log(f"❌ {error_msg}", process_id)
#                 update_imss_status(process_id, "failed", error_msg)
                
#                 # CORRECTED: Set to partial completion
#                 update_master_process_status(process_id, "partial", "mobile_error", 35,
#                                            logs=f"Outlook completed but mobile automation error: {error_msg}")
                
#                 add_log(f"📊 CURP automation PARTIALLY completed for {curp_data['curp_id']}", process_id)
        
#         # NOTE: Removed the email monitoring simulation that was causing incorrect 100% completion
#         # Email monitoring should only run if mobile automation actually succeeds
        
#     except Exception as e:
#         import traceback
#         error_details = traceback.format_exc()
#         error_msg = f"CURP automation failed for {curp_data['curp_id']}: {str(e)}"
        
#         add_log(f"❌ {error_msg}", process_id)
#         add_log(f"Error details: {error_details}", process_id)
        
#         # Update all relevant database tables with error status
#         try:
#             update_outlook_account_status(process_id, "failed", str(e))
#         except:
#             pass
        
#         try:
#             update_imss_status(process_id, "failed", str(e))
#         except:
#             pass
        
#         try:
#             update_email_pdf_status(process_id, "failed", str(e))
#         except:
#             pass
        
#         # CORRECTED: Set to failed with 0% progress
#         update_master_process_status(process_id, "failed", "error", 0, 
#                                    logs=f"Process failed: {error_msg}")
        
#     finally:
#         # Final cooldown before next process
#         try:
#             add_log("Process completed - Cooldown for 3 seconds...", process_id)
#         except Exception:
#             pass
#         time.sleep(3)

def curp_automation_worker(curp_data: dict, process_id: str):
    """
    COMPLETE CURP-to-PDF automation worker with FULL EMAIL POLLING INTEGRATION
    
    WORKFLOW:
    1. Create Outlook account (web browser automation)
    2. Submit IMSS form (mobile app automation) 
    3. Monitor email and download PDF (web browser automation)
    4. Update database with complete progress tracking
    
    PROGRESS LOGIC:
    - Outlook created: 35%
    - IMSS submitted: 75% 
    - PDF link found: 90%
    - PDF downloaded: 100%
    """
    try:
        add_log(f"🚀 Starting COMPLETE CURP automation for {curp_data['curp_id']}", process_id)
        
        # ==========================================
        # PHASE 1: CREATE OUTLOOK ACCOUNT  
        # ==========================================
        add_log("📧 Phase 1: Creating Outlook account", process_id)
        update_master_process_status(process_id, "in_progress", "outlook_creation", 10, 
                                   logs=f"Starting Outlook account creation for {curp_data['first_name']} {curp_data['last_name']}")
        
        # Generate Outlook account data based on personal info
        outlook_data = generate_outlook_data(
            curp_data['first_name'], 
            curp_data['last_name'], 
            curp_data['date_of_birth']
        )
        
        # Store outlook account entry in database
        store_outlook_account(process_id, outlook_data, "pending")
        add_log(f"Generated Outlook credentials - Email: {outlook_data['email']}", process_id)
        
        # Execute Outlook automation using your working code
        outlook_success = False
        try:
            with pw.sync_playwright() as playwright:
                add_log("Playwright context initialized for Outlook creation", process_id)
                
                # Use your exact working Outlook creation function
                result = create_outlook_account(
                    playwright,
                    outlook_data['username'],
                    outlook_data['password'],
                    outlook_data['birth_month'],
                    outlook_data['birth_day'],
                    outlook_data['birth_year'],
                    curp_data['first_name'],
                    curp_data['last_name']
                )
                
                if result:
                    outlook_success = True
                    add_log(f"✅ Outlook account created successfully: {outlook_data['email']}", process_id)
                    
                    # Update database status
                    update_outlook_account_status(process_id, "completed")
                    update_master_process_status(process_id, "in_progress", "outlook_completed", 35, 
                                               email=outlook_data['email'],
                                               logs="Outlook account created - Starting IMSS mobile automation")
                else:
                    raise Exception("Outlook account creation returned False")
                    
        except Exception as outlook_error:
            add_log(f"❌ Outlook creation failed: {str(outlook_error)}", process_id)
            update_outlook_account_status(process_id, "failed", str(outlook_error))
            raise outlook_error
        
        # ==========================================
        # PHASE 2: MOBILE IMSS AUTOMATION
        # ==========================================
        mobile_success = False
        if outlook_success:
            add_log("📱 Phase 2: Starting mobile IMSS automation", process_id)
            update_master_process_status(process_id, "in_progress", "imss_processing", 45,
                                       logs="Outlook completed - Starting mobile IMSS automation")
            
            # Store IMSS processing entry
            store_imss_processing(process_id, curp_data['curp_id'], outlook_data['email'])
            
            try:
                # Import the trigger function from outlook module
                from utils.outlook import trigger_mobile_automation_if_available
                
                add_log("Mobile automation trigger imported successfully", process_id)
                
                # Call mobile automation
                mobile_result = trigger_mobile_automation_if_available(
                    process_id=process_id,
                    curp_id=curp_data['curp_id'],
                    email=outlook_data['email'],
                    first_name=curp_data['first_name'],
                    last_name=curp_data['last_name']
                )
                
                # Handle result based on status
                if mobile_result["success"]:
                    # Mobile automation succeeded
                    mobile_success = True
                    add_log("✅ Mobile IMSS automation completed successfully", process_id)
                    update_imss_status(process_id, "completed", "Mobile automation completed")
                    
                    # Update to 75% - ready for email monitoring
                    update_master_process_status(process_id, "in_progress", "imss_completed", 75,
                                               logs="IMSS form submitted successfully - Starting email monitoring")
                    
                else:
                    # Mobile automation failed - still try email monitoring as fallback
                    add_log(f"⚠️ Mobile automation issue: {mobile_result['message']}", process_id)
                    add_log("Proceeding to email monitoring despite mobile automation issue", process_id)
                    
                    # Mark as partial but continue to email monitoring
                    update_imss_status(process_id, "failed", mobile_result["message"])
                    update_master_process_status(process_id, "in_progress", "mobile_failed_fallback", 50,
                                               logs=f"Mobile automation failed: {mobile_result['message']} - Trying email monitoring as fallback")
                    mobile_success = False  # Will try email monitoring anyway
                    
            except ImportError as ie:
                # Mobile module not available - continue with email monitoring
                error_msg = f"Mobile automation not available: {str(ie)}"
                add_log(f"⚠️ {error_msg}", process_id)
                add_log("Mobile automation not available - proceeding to email monitoring", process_id)
                
                update_imss_status(process_id, "skipped", "Mobile automation module not available")
                update_master_process_status(process_id, "in_progress", "mobile_skipped", 50,
                                           logs="Mobile automation not available - Proceeding to email monitoring")
                mobile_success = False  # Will try email monitoring
                
            except Exception as me:
                # Mobile automation error - continue with email monitoring as fallback
                error_msg = f"Mobile automation error: {str(me)}"
                add_log(f"❌ {error_msg}", process_id)
                add_log("Mobile automation failed - trying email monitoring as fallback", process_id)
                
                update_imss_status(process_id, "failed", error_msg)
                update_master_process_status(process_id, "in_progress", "mobile_error_fallback", 50,
                                           logs=f"Mobile automation error: {error_msg} - Trying email monitoring as fallback")
                mobile_success = False  # Will try email monitoring anyway
        
        # ==========================================
        # PHASE 3: EMAIL MONITORING AND PDF DOWNLOAD (NEW!)
        # ==========================================
        if outlook_success:  # Continue if at least Outlook succeeded
            add_log("📧 Phase 3: Starting email monitoring and PDF download", process_id)
            
            # Store email processing entry
            store_email_pdf_processing(process_id, curp_data['curp_id'], outlook_data['email'])
            
            # Determine timeout based on mobile success
            if mobile_success:
                timeout_minutes = 10  # Shorter timeout if IMSS was submitted successfully
                update_master_process_status(process_id, "in_progress", "email_monitoring", 80,
                                           logs="IMSS submitted successfully - Monitoring email for PDF (10 min timeout)")
            else:
                timeout_minutes = 30  # Longer timeout if mobile failed (user might submit manually)
                update_master_process_status(process_id, "in_progress", "email_monitoring_fallback", 60,
                                           logs="Mobile automation failed - Monitoring email for manual IMSS submission (30 min timeout)")
            
            try:
                # Import email polling module
                from utils.outlook.email_polling import poll_and_download_pdf
                
                add_log(f"Starting email polling (timeout: {timeout_minutes} minutes)", process_id)
                
                # Run email polling and PDF download
                email_result = poll_and_download_pdf(
                    process_id=process_id,
                    email=outlook_data['email'],
                    password=outlook_data['password'],
                    timeout_minutes=timeout_minutes
                )
                
                if email_result["success"]:
                    # PDF downloaded successfully!
                    add_log(f"✅ PDF downloaded successfully: {email_result['file_name']}", process_id)
                    
                    # Update to 100% completion
                    update_master_process_status(process_id, "completed", "pdf_downloaded", 100,
                                               logs=f"Process completed successfully - PDF downloaded: {email_result['file_name']} ({email_result['file_size']} bytes)")
                    
                    add_log(f"🎉 COMPLETE CURP automation finished for {curp_data['curp_id']}", process_id)
                    add_log(f"📄 PDF file: {email_result['file_name']} ({email_result['file_size']} bytes)", process_id)
                    
                elif email_result["link_found"]:
                    # Link found but download failed
                    add_log(f"⚠️ PDF link found but download failed: {email_result['error']}", process_id)
                    
                    update_master_process_status(process_id, "partial", "pdf_link_found_download_failed", 90,
                                               logs=f"PDF link found but download failed: {email_result['error']}")
                    
                else:
                    # No email received within timeout
                    add_log(f"⚠️ No IMSS email received within {timeout_minutes} minutes", process_id)
                    
                    if mobile_success:
                        # Mobile succeeded but no email - this is unusual
                        update_master_process_status(process_id, "partial", "imss_submitted_no_email", 85,
                                                   logs=f"IMSS form submitted but no email received within {timeout_minutes} minutes")
                    else:
                        # Mobile failed and no email - likely IMSS was never submitted
                        update_master_process_status(process_id, "partial", "no_imss_submission", 50,
                                                   logs=f"No IMSS submission detected and no email received within {timeout_minutes} minutes")
                    
            except ImportError as email_import_error:
                # Email polling module not available
                error_msg = f"Email polling module not available: {str(email_import_error)}"
                add_log(f"❌ {error_msg}", process_id)
                
                update_email_pdf_status(process_id, "failed", error_msg)
                
                if mobile_success:
                    # Mobile succeeded but can't check email
                    update_master_process_status(process_id, "partial", "imss_submitted_no_email_module", 75,
                                               logs=f"IMSS submitted successfully but email polling not available: {error_msg}")
                else:
                    # Nothing worked
                    update_master_process_status(process_id, "partial", "outlook_only", 35,
                                               logs=f"Only Outlook creation succeeded - Mobile and email modules not available")
                
            except Exception as email_error:
                # Email polling failed
                error_msg = f"Email polling failed: {str(email_error)}"
                add_log(f"❌ {error_msg}", process_id)
                
                update_email_pdf_status(process_id, "failed", error_msg)
                
                if mobile_success:
                    # Mobile succeeded but email polling failed
                    update_master_process_status(process_id, "partial", "imss_submitted_email_failed", 75,
                                               logs=f"IMSS submitted successfully but email polling failed: {error_msg}")
                else:
                    # Both mobile and email failed
                    update_master_process_status(process_id, "partial", "mobile_and_email_failed", 35,
                                               logs=f"Mobile automation and email polling both failed")
        
        else:
            raise Exception("Cannot proceed without successful Outlook account creation")
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        error_msg = f"CURP automation failed for {curp_data['curp_id']}: {str(e)}"
        
        add_log(f"❌ {error_msg}", process_id)
        add_log(f"Error details: {error_details}", process_id)
        
        # Update all relevant database tables with error status
        try:
            update_outlook_account_status(process_id, "failed", str(e))
        except:
            pass
        
        try:
            update_imss_status(process_id, "failed", str(e))
        except:
            pass
        
        try:
            update_email_pdf_status(process_id, "failed", str(e))
        except:
            pass
        
        # Set to failed with 0% progress
        update_master_process_status(process_id, "failed", "error", 0, 
                                   logs=f"Process failed: {error_msg}")
        
    finally:
        # Final cooldown before next process
        try:
            add_log("Process completed - Cooldown for 3 seconds...", process_id)
        except Exception:
            pass
        time.sleep(3)








# def curp_automation_worker(curp_data: dict, process_id: str):
#     """
#     Complete CURP-to-PDF automation worker with integrated mobile automation
    
#     WORKFLOW:
#     1. Create Outlook account (your working code)
#     2. Trigger mobile IMSS automation (integrated)
#     3. Email monitoring (placeholder for future)
#     4. Complete database updates throughout
    
#     This function handles the complete flow from CURP input to PDF delivery
#     """
#     try:
#         add_log(f"🚀 Starting CURP automation for {curp_data['curp_id']}", process_id)
        
#         # ==========================================
#         # PHASE 1: CREATE OUTLOOK ACCOUNT  
#         # ==========================================
#         add_log("📧 Phase 1: Creating Outlook account", process_id)
#         update_master_process_status(process_id, "in_progress", "outlook_creation", 10, 
#                                    logs=f"Starting Outlook account creation for {curp_data['first_name']} {curp_data['last_name']}")
        
#         # Generate Outlook account data based on personal info
#         outlook_data = generate_outlook_data(
#             curp_data['first_name'], 
#             curp_data['last_name'], 
#             curp_data['date_of_birth']
#         )
        
#         # Store outlook account entry in database
#         store_outlook_account(process_id, outlook_data, "pending")
#         add_log(f"Generated Outlook credentials - Email: {outlook_data['email']}", process_id)
        
#         # Execute Outlook automation using your working code
#         outlook_success = False
#         try:
#             with pw.sync_playwright() as playwright:
#                 add_log("Playwright context initialized for Outlook creation", process_id)
                
#                 # Use your exact working Outlook creation function
#                 result = create_outlook_account(
#                     playwright,
#                     outlook_data['username'],
#                     outlook_data['password'],
#                     outlook_data['birth_month'],
#                     outlook_data['birth_day'],
#                     outlook_data['birth_year'],
#                     curp_data['first_name'],
#                     curp_data['last_name']
#                 )
                
#                 if result:
#                     outlook_success = True
#                     add_log(f"✅ Outlook account created successfully: {outlook_data['email']}", process_id)
                    
#                     # Update database status
#                     update_outlook_account_status(process_id, "completed")
#                     update_master_process_status(process_id, "in_progress", "outlook_completed", 35, 
#                                                email=outlook_data['email'],
#                                                logs="Outlook account created - Preparing mobile automation")
#                 else:
#                     raise Exception("Outlook account creation returned False")
                    
#         except Exception as outlook_error:
#             add_log(f"❌ Outlook creation failed: {str(outlook_error)}", process_id)
#             update_outlook_account_status(process_id, "failed", str(outlook_error))
#             raise outlook_error
        
#         # ==========================================
#         # PHASE 2: MOBILE IMSS AUTOMATION
#         # ==========================================
#         if outlook_success:
#             add_log("📱 Phase 2: Starting mobile IMSS automation", process_id)
#             update_master_process_status(process_id, "in_progress", "imss_processing", 45,
#                                        logs="Outlook completed - Starting mobile IMSS automation")
            
#             # Store IMSS processing entry
#             store_imss_processing(process_id, curp_data['curp_id'], outlook_data['email'])
            
#             # Attempt mobile automation integration
#             mobile_success = False
#             try:
#                 # Import and run mobile automation
#                 from utils.mobile import start_mobile_automation
                
#                 add_log("Mobile automation module imported successfully", process_id)
                
#                 # Run mobile IMSS automation with your working code
#                 mobile_result = start_mobile_automation(
#                     process_id=process_id,
#                     curp_id=curp_data['curp_id'],
#                     email=outlook_data['email'],
#                     first_name=curp_data['first_name'],
#                     last_name=curp_data['last_name']
#                 )
                
#                 if mobile_result:
#                     mobile_success = True
#                     add_log("✅ Mobile IMSS automation completed successfully", process_id)
#                     update_master_process_status(process_id, "in_progress", "email_monitoring", 75,
#                                                logs="IMSS automation completed - Email monitoring started")
#                 else:
#                     raise Exception("Mobile IMSS automation returned False")
                    
#             except ImportError as ie:
#                 # Mobile module not available - continue with email monitoring
#                 error_msg = f"Mobile automation not available: {str(ie)}"
#                 add_log(f"⚠️ {error_msg}", process_id)
#                 add_log("Continuing without mobile automation (development mode)", process_id)
                
#                 # Mark IMSS as skipped and continue
#                 update_imss_status(process_id, "skipped", "Mobile automation module not available")
#                 update_master_process_status(process_id, "in_progress", "email_monitoring", 60,
#                                            logs="Skipping mobile automation - Proceeding to email monitoring")
#                 mobile_success = True  # Continue the flow
                
#             except Exception as me:
#                 # Mobile automation failed
#                 error_msg = f"Mobile automation failed: {str(me)}"
#                 add_log(f"❌ {error_msg}", process_id)
#                 update_imss_status(process_id, "failed", error_msg)
                
#                 # Continue to email monitoring as fallback
#                 add_log("Continuing to email monitoring despite mobile failure", process_id)
#                 update_master_process_status(process_id, "in_progress", "email_monitoring", 60,
#                                            logs="Mobile automation failed - Fallback to email monitoring")
#                 mobile_success = True  # Continue despite mobile failure
        
#         # ==========================================
#         # PHASE 3: EMAIL MONITORING (PLACEHOLDER)
#         # ==========================================
#         if outlook_success:  # Continue if at least Outlook succeeded
#             add_log("📧 Phase 3: Email monitoring for CURP PDF", process_id)
            
#             # Store email processing entry
#             store_email_pdf_processing(process_id, curp_data['curp_id'], outlook_data['email'])
            
#             # Email monitoring simulation (replace with real implementation later)
#             add_log("Email monitoring started (simulated for now)", process_id)
#             update_master_process_status(process_id, "in_progress", "email_monitoring", 85,
#                                        logs="Monitoring email for CURP PDF arrival")
            
#             # Simulate email monitoring delay
#             time.sleep(15)  # Simulate monitoring time
            
#             # Simulate successful PDF receipt
#             add_log("Simulated: CURP PDF received via email", process_id)
#             update_master_process_status(process_id, "completed", "pdf_ready", 100,
#                                        logs="Process completed successfully - CURP PDF available")
            
#             add_log(f"🎉 CURP automation completed successfully for {curp_data['curp_id']}", process_id)
            
#         else:
#             raise Exception("Cannot proceed without successful Outlook account")
            
#     except Exception as e:
#         import traceback
#         error_details = traceback.format_exc()
#         error_msg = f"CURP automation failed for {curp_data['curp_id']}: {str(e)}"
        
#         add_log(f"❌ {error_msg}", process_id)
#         add_log(f"Error details: {error_details}", process_id)
        
#         # Update all relevant database tables with error status
#         try:
#             update_outlook_account_status(process_id, "failed", str(e))
#         except:
#             pass
        
#         try:
#             update_imss_status(process_id, "failed", str(e))
#         except:
#             pass
        
#         try:
#             update_email_pdf_status(process_id, "failed", str(e))
#         except:
#             pass
        
#         # Update master status
#         update_master_process_status(process_id, "failed", "error", 0, 
#                                    logs=f"Process failed: {error_msg}")
        
#     finally:
#         # Final cooldown before next process
#         try:
#             add_log("Process completed - Cooldown for 3 seconds...", process_id)
#         except Exception:
#             pass
#         time.sleep(3)

# def curp_automation_worker(curp_data: dict, process_id: str):
#     """
#     Complete CURP-to-PDF automation worker with FIXED mobile automation integration
    
#     WORKFLOW:
#     1. Create Outlook account (your working code)
#     2. Trigger mobile IMSS automation (FIXED to use proper trigger function)
#     3. Email monitoring (placeholder for future)
#     4. Complete database updates throughout
    
#     This function handles the complete flow from CURP input to PDF delivery
#     """
#     try:
#         add_log(f"🚀 Starting CURP automation for {curp_data['curp_id']}", process_id)
        
#         # ==========================================
#         # PHASE 1: CREATE OUTLOOK ACCOUNT  
#         # ==========================================
#         add_log("📧 Phase 1: Creating Outlook account", process_id)
#         update_master_process_status(process_id, "in_progress", "outlook_creation", 10, 
#                                    logs=f"Starting Outlook account creation for {curp_data['first_name']} {curp_data['last_name']}")
        
#         # Generate Outlook account data based on personal info
#         outlook_data = generate_outlook_data(
#             curp_data['first_name'], 
#             curp_data['last_name'], 
#             curp_data['date_of_birth']
#         )
        
#         # Store outlook account entry in database
#         store_outlook_account(process_id, outlook_data, "pending")
#         add_log(f"Generated Outlook credentials - Email: {outlook_data['email']}", process_id)
        
#         # Execute Outlook automation using your working code
#         outlook_success = False
#         try:
#             with pw.sync_playwright() as playwright:
#                 add_log("Playwright context initialized for Outlook creation", process_id)
                
#                 # Use your exact working Outlook creation function
#                 result = create_outlook_account(
#                     playwright,
#                     outlook_data['username'],
#                     outlook_data['password'],
#                     outlook_data['birth_month'],
#                     outlook_data['birth_day'],
#                     outlook_data['birth_year'],
#                     curp_data['first_name'],
#                     curp_data['last_name']
#                 )
                
#                 if result:
#                     outlook_success = True
#                     add_log(f"✅ Outlook account created successfully: {outlook_data['email']}", process_id)
                    
#                     # Update database status
#                     update_outlook_account_status(process_id, "completed")
#                     update_master_process_status(process_id, "in_progress", "outlook_completed", 35, 
#                                                email=outlook_data['email'],
#                                                logs="Outlook account created - Triggering mobile automation")
#                 else:
#                     raise Exception("Outlook account creation returned False")
                    
#         except Exception as outlook_error:
#             add_log(f"❌ Outlook creation failed: {str(outlook_error)}", process_id)
#             update_outlook_account_status(process_id, "failed", str(outlook_error))
#             raise outlook_error
        
#         # ==========================================
#         # PHASE 2: MOBILE IMSS AUTOMATION (FIXED)
#         # ==========================================
#         if outlook_success:
#             add_log("📱 Phase 2: Triggering mobile IMSS automation", process_id)
#             update_master_process_status(process_id, "in_progress", "imss_processing", 45,
#                                        logs="Outlook completed - Triggering mobile IMSS automation")
            
#             # Store IMSS processing entry
#             store_imss_processing(process_id, curp_data['curp_id'], outlook_data['email'])
            
#             # FIXED: Use the trigger function from outlook module
#             mobile_success = False
#             try:
#                 # Import the trigger function from outlook module (not direct mobile import)
#                 from utils.outlook import trigger_mobile_automation_if_available
                
#                 add_log("Mobile automation trigger function imported successfully", process_id)
                
#                 # Trigger mobile IMSS automation using the proper trigger function
#                 mobile_result = trigger_mobile_automation_if_available(
#                     process_id=process_id,
#                     curp_id=curp_data['curp_id'],
#                     email=outlook_data['email'],
#                     first_name=curp_data['first_name'],
#                     last_name=curp_data['last_name']
#                 )
                
#                 if mobile_result:
#                     mobile_success = True
#                     add_log("✅ Mobile IMSS automation completed successfully", process_id)
#                     update_master_process_status(process_id, "in_progress", "email_monitoring", 75,
#                                                logs="IMSS automation completed - Email monitoring started")
#                 else:
#                     add_log("⚠️ Mobile automation returned False, but continuing", process_id)
#                     # Continue even if mobile automation fails
#                     mobile_success = True
                    
#             except ImportError as ie:
#                 # Mobile module not available - continue with email monitoring
#                 error_msg = f"Mobile automation trigger not available: {str(ie)}"
#                 add_log(f"⚠️ {error_msg}", process_id)
#                 add_log("Continuing without mobile automation (development mode)", process_id)
                
#                 # Mark IMSS as skipped and continue
#                 update_imss_status(process_id, "skipped", "Mobile automation module not available")
#                 update_master_process_status(process_id, "in_progress", "email_monitoring", 60,
#                                            logs="Skipping mobile automation - Proceeding to email monitoring")
#                 mobile_success = True  # Continue the flow
                
#             except Exception as me:
#                 # Mobile automation failed
#                 error_msg = f"Mobile automation trigger failed: {str(me)}"
#                 add_log(f"❌ {error_msg}", process_id)
#                 update_imss_status(process_id, "failed", error_msg)
                
#                 # Continue to email monitoring as fallback
#                 add_log("Continuing to email monitoring despite mobile failure", process_id)
#                 update_master_process_status(process_id, "in_progress", "email_monitoring", 60,
#                                            logs="Mobile automation failed - Fallback to email monitoring")
#                 mobile_success = True  # Continue despite mobile failure
        
#         # ==========================================
#         # PHASE 3: EMAIL MONITORING (PLACEHOLDER)
#         # ==========================================
#         if outlook_success:  # Continue if at least Outlook succeeded
#             add_log("📧 Phase 3: Email monitoring for CURP PDF", process_id)
            
#             # Store email processing entry
#             store_email_pdf_processing(process_id, curp_data['curp_id'], outlook_data['email'])
            
#             # Email monitoring simulation (replace with real implementation later)
#             add_log("Email monitoring started (simulated for now)", process_id)
#             update_master_process_status(process_id, "in_progress", "email_monitoring", 85,
#                                        logs="Monitoring email for CURP PDF arrival")
            
#             # Simulate email monitoring delay
#             time.sleep(15)  # Simulate monitoring time
            
#             # Simulate successful PDF receipt
#             add_log("Simulated: CURP PDF received via email", process_id)
#             update_master_process_status(process_id, "completed", "pdf_ready", 100,
#                                        logs="Process completed successfully - CURP PDF available")
            
#             add_log(f"🎉 CURP automation completed successfully for {curp_data['curp_id']}", process_id)
            
#         else:
#             raise Exception("Cannot proceed without successful Outlook account")
            
#     except Exception as e:
#         import traceback
#         error_details = traceback.format_exc()
#         error_msg = f"CURP automation failed for {curp_data['curp_id']}: {str(e)}"
        
#         add_log(f"❌ {error_msg}", process_id)
#         add_log(f"Error details: {error_details}", process_id)
        
#         # Update all relevant database tables with error status
#         try:
#             update_outlook_account_status(process_id, "failed", str(e))
#         except:
#             pass
        
#         try:
#             update_imss_status(process_id, "failed", str(e))
#         except:
#             pass
        
#         try:
#             update_email_pdf_status(process_id, "failed", str(e))
#         except:
#             pass
        
#         # Update master status
#         update_master_process_status(process_id, "failed", "error", 0, 
#                                    logs=f"Process failed: {error_msg}")
        
#     finally:
#         # Final cooldown before next process
#         try:
#             add_log("Process completed - Cooldown for 3 seconds...", process_id)
#         except Exception:
#             pass
#         time.sleep(3)

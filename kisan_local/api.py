import frappe
from frappe.auth import LoginManager

@frappe.whitelist(allow_guest=True)
def create_user(email=None, mobile=None, language=None):
    """
    Create or login user with email or mobile number
    """
    try:
        user_language = language or "en"
        
        # Generate email based on input
        if mobile:
            email = f"user_{mobile}@noemail.com"
            first_name = ""
        elif not email:
            random_hash = frappe.generate_hash(length=12)
            email = f"user_{random_hash}@noemail.com"
            first_name = ""
        else:
            # Use email as first name for email-based registrations
            first_name = email.split("@")[0]
        
        # Check if user exists
        user_exists = frappe.db.exists("User", email)
        
        if not user_exists:
            # Create new user
            user = frappe.get_doc({
                "doctype": "User",
                "email": email,
                "first_name": first_name,
                "enabled": 1,
                "send_welcome_email": 0,
                "user_type": "Website User",
                "mobile_no": mobile if mobile else None,
                "language": user_language,
            })
            user.flags.ignore_permissions = True
            user.flags.ignore_password_policy = True
            user.insert()
            frappe.db.commit()
        else:
            # Get existing user
            user = frappe.get_doc("User", email)
            
            # Update language if different
            if user.language != user_language:
                user.language = user_language
                user.save(ignore_permissions=True)
                frappe.db.commit()
        
        # Login user using the original simple method
        frappe.set_user(user.name)
        frappe.local.login_manager.login_as(user.name)
        
        # Clear any cached user data
        frappe.clear_cache(user=user.name)
        
        return {
            "status": "success",
            "email": email,
            "user": user.name,
            "message": "User logged in successfully"
        }
    
    except Exception as e:
        frappe.log_error(message=str(e), title="User Creation Error")
        return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=True)
def set_language(lang):
    """
    Set language preference for current user and session
    """
    try:
        frappe.local.lang = lang
        
        # Update user preference if logged in
        if frappe.session.user and frappe.session.user != "Guest":
            user = frappe.get_doc("User", frappe.session.user)
            if user.language != lang:
                user.language = lang
                user.save(ignore_permissions=True)
        
        frappe.db.commit()
        
        return {"status": "ok", "lang": lang}

    except Exception as e:
        frappe.log_error(str(e), "Set Language Error")
        return {"status": "error", "message": str(e)}


def get_context(context):
    """
    Set language from URL parameter when page loads
    """
    lang = frappe.form_dict.get('lang', 'en')
    frappe.local.lang = lang
    return context
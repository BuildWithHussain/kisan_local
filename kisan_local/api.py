import frappe
from frappe.auth import LoginManager


@frappe.whitelist(allow_guest=True)
def create_user(email=None, mobile=None, language=None):
    """
    Create or login user with email or mobile number
    """
    try:
        user_language = language or "en"

        if mobile:
            email = f"user_{mobile}@noemail.com"
        elif not email:
            random_hash = frappe.generate_hash(length=12)
            email = f"user_{random_hash}@noemail.com"

        first_name = ""


        user_exists = frappe.db.exists("User", email)

        if not user_exists:
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
            user = frappe.get_doc("User", user_exists)

            if user.language != user_language:
                user.language = user_language
                user.save(ignore_permissions=True)
                frappe.db.commit()

        frappe.local.session_obj = None
        frappe.clear_cache()

        # Create fresh login manager
        login_manager = LoginManager()
        login_manager.login_as(user.name)

        frappe.db.commit()

        return {
            "status": "success",
            "email": email,
            "message": "User logged in successfully"
        }

    except Exception as e:
        frappe.log_error(message=str(e), title="User Creation Error")
        return {"status": "error", "message": str(e)}


def get_context(context):
    """
    Call it when the page loads to set language from URL parameter
    """
    lang = frappe.form_dict.get('lang')
    if lang:
        frappe.local.lang = lang
    return context

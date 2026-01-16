import frappe

@frappe.whitelist(allow_guest=True)
def create_user(email=None, mobile=None, language=None):
    """
    Create or login user with email or mobile number.
    Returns a one-time login key that can be used to auto-login.
    """
    try:
        user_language = language or "en"

        if mobile:
            email = f"user_{mobile}@noemail.com"
        elif not email:
            random_hash = frappe.generate_hash(length=12)
            email = f"user_{random_hash}@noemail.com"

        first_name = "User"

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
            user = frappe.get_doc("User", email)

            needs_save = False
            if not user.enabled:
                user.enabled = 1
                needs_save = True
            if user.language != user_language:
                user.language = user_language
                needs_save = True
            if not user.first_name:
                user.first_name = first_name
                needs_save = True
            if needs_save:
                user.save(ignore_permissions=True)
                frappe.db.commit()

        frappe.clear_cache(user=user.name)

        login_key = frappe.generate_hash()
        frappe.cache.set_value(
            f"one_time_login_key:{login_key}",
            email,
            expires_in_sec=300  # 5 minutes
        )

        user_email = None
        if email and not email.endswith("@noemail.com"):
            user_email = email

        return {
            "status": "success",
            "email": user_email,
            "user": user.name,
            "login_key": login_key,
            "message": "User created successfully"
        }

    except Exception as e:
        frappe.log_error(message=str(e), title="User Creation Error")
        return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=True)
def set_language(lang):
    """
    Set language preference for current user with current session
    """
    try:
        frappe.local.lang = lang

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


@frappe.whitelist(allow_guest=True, methods=["GET"])
def auto_login(key=None, redirect_to=None):
    """
    Auto-login using a one-time key and redirect to the specified URL.
    Bypassing the Buzz login.
    """
    from frappe import _

    if not key:
        frappe.respond_as_web_page(
            _("Invalid Request"),
            _("Login key is required."),
            http_status_code=400
        )
        return

    cache_key = f"one_time_login_key:{key}"
    email = frappe.cache.get_value(cache_key)

    if not email:
        frappe.respond_as_web_page(
            _("Not Permitted"),
            _("The login link is invalid or has expired."),
            http_status_code=403,
            indicator_color="red"
        )
        return

    frappe.cache.delete_value(cache_key)

    frappe.local.login_manager.login_as(email)

    if not redirect_to:
        redirect_to = "/dashboard/book-tickets/KSS-2026-South-India"

    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = redirect_to


@frappe.whitelist(allow_guest=True)
def cleanup_corrupted_sessions():
    """
    Utility to clean up sessions with NULL or invalid users.
    Can call this if encountering 'User None is disabled' errors.
    """
    try:
        frappe.db.sql("DELETE FROM `tabSessions` WHERE user IS NULL OR user = '' OR user = 'None'")

        frappe.cache.delete_keys("session")

        frappe.db.commit()

        return {"status": "success", "message": "Corrupted sessions cleaned up"}
    except Exception as e:
        frappe.log_error(message=str(e), title="Session Cleanup Error")
        return {"status": "error", "message": str(e)}
import frappe

def get_context(context):
    """
    Set language from URL parameter when page loads
    """
    lang = frappe.form_dict.get('lang', 'en')
    frappe.local.lang = lang

    # Set language in session as well
    if hasattr(frappe.local, 'session_obj') and frappe.local.session_obj:
        frappe.local.session_obj.data.lang = lang

    # Check if user is already logged in
    context.is_logged_in = frappe.session.user and frappe.session.user != "Guest"
    context.dashboard_url = "/dashboard/book-tickets/KSS-2026-South-India"

    return context
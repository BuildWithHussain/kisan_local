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
    
    return context
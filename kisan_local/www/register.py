import frappe


def get_context(context):
    """
    Set language from URL parameter before page renders
    This ensures translations work on page load
    """
    lang = frappe.form_dict.get('lang', 'en')

    frappe.local.lang = lang

    if frappe.session.user and frappe.session.user != "Guest":
        if hasattr(frappe.local, 'session_obj') and frappe.local.session_obj:
            frappe.local.session_obj.data.lang = lang

    return context

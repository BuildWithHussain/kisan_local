import frappe

@frappe.whitelist(allow_guest=True)
def create_user(email=None, mobile=None):
	try:
		if frappe.session.user and frappe.session.user != "Guest":
			return {
				"status": "already_logged_in",
				"email": frappe.session.user,
				"message": "User already logged in",
			}

		if mobile:
			email = f"user_{mobile}@noemail.com"
			first_name = " "
		elif not email:
			random_hash = frappe.generate_hash(length=12)
			email = f"user_{random_hash}@noemail.com"
			first_name = " "
		else:
			first_name = " "

		user_exists = frappe.db.exists("User", email)
		if not user_exists:
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": email,
					"first_name": first_name,
					"enabled": 1,
					"send_welcome_email": 0,
					"user_type": "Website User",
					"mobile_no": mobile if mobile else None,
				}
			)
			user.flags.ignore_permissions = True
			user.flags.ignore_password_policy = True
			user.insert()
			frappe.db.commit()
		else:
			user = frappe.get_cached_doc("User", email)

		frappe.local.login_manager.login_as(user.name)
		frappe.db.commit()

		frappe.local.cookie_manager.set_cookie("user_id", user.name)
		frappe.local.cookie_manager.set_cookie("sid", frappe.session.sid)

		return {
			"status": "success",
			"email": email,
			"mobile": mobile,
			"message": "User created successfully",
		}

	except Exception as e:
		frappe.log_error(message=str(e), title="User Creation Error")
		return {"status": "error", "message": str(e)}

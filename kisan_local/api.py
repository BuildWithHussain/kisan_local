import frappe

@frappe.whitelist(allow_guest=True)
def create_user(email=None):
	try:
		if not email:
			random_hash = frappe.generate_hash(length=12)
			email = f"user_{random_hash}@noemail.com"
			first_name = f"Guest-{random_hash}"
		else:
			first_name = email.split("@")[0]

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
				}
			)
			user.flags.ignore_permissions = True
			user.flags.ignore_password_policy = True
			user.insert()
			frappe.db.commit()
		else:
			user = frappe.get_cached_doc("User", user_exists)

		frappe.local.login_manager.login_as(user.name)

		return {
			"status": "success",
			"email": email,
			"message": "User created successfully",
		}

	except Exception as e:
		frappe.log_error(message=str(e), title="User Creation Error")
		return {"status": "error", "message": str(e)}

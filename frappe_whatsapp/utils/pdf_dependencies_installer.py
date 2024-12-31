import os
import frappe


def setup_dependencies():
    try:
        os.system("pip install playwright")
        os.system("playwright install")
        os.system("sudo playwright install-deps")
        os.system("sudo apt-get install libnss3 libnspr4 libasound2 -y")
    except Exception as e:
        frappe.log_error(title="setup_dependencies error on whatsapp", message=str(e))


@frappe.whitelist()
def trigger_action():
    setup_dependencies()
from playwright.sync_api import sync_playwright
import frappe
from io import BytesIO


def get_buffer(html_content):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_content)
        pdf_buffer = BytesIO(
            page.pdf(format="A4", margin={"top": "0", "bottom": "20mm", "left": "20mm", "right": "20mm"}))
        browser.close()
        return pdf_buffer


def get_context_with_letter_head(letterhead: str, context: dict):
    letter_head_doc = frappe.get_doc("Letter Head", letterhead)
    if letter_head_doc:
        if letter_head_doc.content:
            context["letter_head"] = letter_head_doc.content
        if letter_head_doc.footer:
            context["footer"] = letter_head_doc.footer
    return context


def get_custom_render_template(docname: str, doctype: str, print_format: str):
    try:
        doc = frappe.get_doc(doctype, docname)
        print_format_doc = frappe.get_doc("Print Format", print_format)
        if not print_format_doc.html:
            frappe.throw("The selected print format does not contain an HTML template.")
        letter_head = None
        if doc.letter_head:
            letter_head = doc.letter_head
        elif doc.custom_letter_head:
            letter_head = doc.custom_letter_head
        try:
            context = {
                "doc": doc,
                "frappe": frappe,
            }
            if letter_head:
                context = get_context_with_letter_head(letter_head, context)
            html_template = print_format_doc.html
            html = frappe.render_template(html_template, context)
        except Exception as e:
            return str(e)
        return html
    except Exception as e:
        return str(e)


@frappe.whitelist(allow_guest=True)
def generate_pdf(doctype=None,
                 print_format=None,
                 docname=None):
    """
    Generate a PDF dynamically without storing it using WeasyPrint.
    """
    html_content = get_custom_render_template(docname, doctype, print_format)
    pdf_buffer = get_buffer(html_content)
    frappe.response['filename'] = 'dynamic_pdf.pdf'
    frappe.local.response.filecontent = pdf_buffer.getvalue()
    frappe.local.response.type = "pdf"

"""
Finance utilities — receipt PDF generation using WeasyPrint.
"""
from io import BytesIO
from django.utils import timezone


def generate_receipt_pdf(transaction, request=None):
    from apps.core.models import ChurchSettings
    church = ChurchSettings.load()
    try:
        from weasyprint import HTML
        from django.template.loader import render_to_string
        context = {
            "transaction": transaction,
            "church": church,
            "member": transaction.member,
            "generated_at": timezone.now(),
        }
        html_string = render_to_string("finance/receipt.html", context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri("/") if request else "/")
        buffer = BytesIO()
        html.write_pdf(buffer)
        buffer.seek(0)
        return buffer
    except Exception:
        return _minimal_receipt(transaction, church)


def _minimal_receipt(transaction, church):
    lines = [
        "OFFICIAL RECEIPT", "",
        church.church_name, church.address or "", "",
        f"Receipt No: {transaction.receipt_number}",
        f"Reference:  {transaction.reference}",
        f"Date:       {transaction.transaction_date}",
        f"Member:     {transaction.member.get_full_name() if transaction.member else 'Anonymous'}",
        f"Type:       {transaction.get_transaction_type_display()}",
        f"Amount:     {church.currency_symbol}{transaction.amount:,.2f}",
        f"Method:     {transaction.get_payment_method_display()}",
        "", "Thank you for your faithfulness.",
    ]
    buf = BytesIO("\n".join(lines).encode("utf-8"))
    buf.seek(0)
    return buf

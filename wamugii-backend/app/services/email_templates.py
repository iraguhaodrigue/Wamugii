"""
HTML email bodies for the events that warrant an email.

Deliberately plain: a centred table, inline CSS only, no images (they would
need hosting) and no external stylesheets, so these render the same in Gmail,
Outlook and a phone client. Each builder returns `(subject, html, text)` — the
plain-text part matters for deliverability and for clients that refuse HTML.

CTA links are built from settings.FRONTEND_URL. When it is unset the button is
simply omitted rather than pointing at a localhost URL the recipient cannot
open.
"""

from decimal import Decimal

from app.core.config import settings

BRAND_NAME = "WAMUGII TECH SOLUTIONS"
BRAND_SLOGAN = "We Build. We Innovate. We Empower."

# Matches the app's teal→purple identity, kept as literal hex because email
# clients do not support CSS variables.
TEAL = "#0e7490"
PURPLE = "#6d28d9"
INK = "#0f172a"
MUTED = "#64748b"
BORDER = "#e2e8f0"


def _cta_url(path: str) -> str | None:
    """Absolute frontend URL for `path`, or None when FRONTEND_URL is unset."""
    base = settings.FRONTEND_URL
    if not base:
        return None
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


def _button(url: str | None, label: str) -> str:
    if not url:
        return ""
    return (
        f'<tr><td style="padding:24px 0 8px 0;">'
        f'<a href="{url}" style="display:inline-block;background:{TEAL};color:#ffffff;'
        f'text-decoration:none;font-weight:600;font-size:14px;padding:12px 22px;'
        f'border-radius:8px;">{label}</a></td></tr>'
    )


def _rows(pairs: list[tuple[str, str]]) -> str:
    """Label/value rows for the little detail table in each email."""
    out = []
    for label, value in pairs:
        out.append(
            f'<tr>'
            f'<td style="padding:6px 16px 6px 0;color:{MUTED};font-size:14px;'
            f'white-space:nowrap;vertical-align:top;">{label}</td>'
            f'<td style="padding:6px 0;color:{INK};font-size:14px;font-weight:600;">{value}</td>'
            f'</tr>'
        )
    return "".join(out)


def _shell(heading: str, intro: str, detail_rows: str, cta: str, footer_note: str = "") -> str:
    """The shared frame: branded header, white card, muted footer."""
    return f"""\
<!doctype html>
<html>
<body style="margin:0;padding:0;background:#f5f7fb;font-family:'Segoe UI',Arial,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f5f7fb;padding:24px 12px;">
    <tr><td align="center">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#ffffff;border:1px solid {BORDER};border-radius:12px;overflow:hidden;">
        <tr><td style="background:{INK};padding:20px 24px;">
          <div style="color:#ffffff;font-size:16px;font-weight:700;letter-spacing:0.3px;">{BRAND_NAME}</div>
          <div style="color:#67e8f9;font-size:12px;margin-top:4px;">{BRAND_SLOGAN}</div>
        </td></tr>
        <tr><td style="padding:24px;">
          <h1 style="margin:0 0 12px 0;color:{INK};font-size:19px;font-weight:700;">{heading}</h1>
          <p style="margin:0 0 18px 0;color:{MUTED};font-size:14px;line-height:1.6;">{intro}</p>
          <table role="presentation" cellpadding="0" cellspacing="0">{detail_rows}</table>
          <table role="presentation" cellpadding="0" cellspacing="0">{cta}</table>
          {footer_note}
        </td></tr>
        <tr><td style="padding:16px 24px;border-top:1px solid {BORDER};color:{MUTED};font-size:12px;line-height:1.5;">
          This is an automated message from {BRAND_NAME}. Please don't reply to this email.
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def _money(value: Decimal | str | None) -> str:
    """Money arrives as a decimal string; show it with the currency."""
    if value is None:
        return "—"
    return f"RWF {value}"


def _plain(heading: str, lines: list[str], url: str | None, label: str) -> str:
    body = "\n".join(lines)
    tail = f"\n\n{label}: {url}" if url else ""
    return f"{BRAND_NAME}\n{BRAND_SLOGAN}\n\n{heading}\n\n{body}{tail}\n"


# --- status wording ---------------------------------------------------------

# Plain English for each project status, so a client doesn't have to decode an
# enum to understand what just happened to their project.
PROJECT_STATUS_MEANING: dict[str, str] = {
    "PENDING": "Your project is logged and waiting to be scheduled.",
    "PLANNING": "We're planning the work and scoping out the details.",
    "IN_PROGRESS": "We've started working on your project.",
    "ON_HOLD": "Work is paused for now — we'll be in touch about next steps.",
    "TESTING": "We're testing the work before handing it over.",
    "CLIENT_REVIEW": "It's ready for your review — we'd love your feedback.",
    "COMPLETED": "Your project is complete. Thank you for working with us.",
    "CANCELLED": "This project has been cancelled.",
}


# --- templates --------------------------------------------------------------


def quote_submitted_admin(quote) -> tuple[str, str, str]:
    """To staff/admin: a new public quote request landed."""
    subject = f"New Quote Request — {quote.project_title}"
    url = _cta_url("/admin/quotes")

    pairs = [
        ("Name", quote.full_name),
        ("Email", quote.email),
        ("Phone", quote.phone or "—"),
    ]
    if getattr(quote, "company_name", None):
        pairs.append(("Company", quote.company_name))
    if getattr(quote, "budget_range", None):
        pairs.append(("Budget", quote.budget_range))
    if getattr(quote, "preferred_deadline", None):
        pairs.append(("Deadline", quote.preferred_deadline))
    pairs.append(("Project", quote.project_title))
    pairs.append(("Details", quote.project_description))

    html = _shell(
        heading="New quote request",
        intro="Someone has submitted a quote request through the website.",
        detail_rows=_rows(pairs),
        cta=_button(url, "View Quote Request"),
    )
    text = _plain(
        "New quote request",
        [f"{label}: {value}" for label, value in pairs],
        url,
        "View Quote Request",
    )
    return subject, html, text


def project_status_changed_client(project, client) -> tuple[str, str, str]:
    subject = f"Your Project '{project.title}' has been updated"
    url = _cta_url(f"/client/projects/{project.id}")
    status = project.status.value if hasattr(project.status, "value") else str(project.status)
    meaning = PROJECT_STATUS_MEANING.get(status, "Your project status has been updated.")

    pairs = [("Project", project.title), ("Status", status.replace("_", " ").title())]
    html = _shell(
        heading="Project status updated",
        intro=f"Hi {client.full_name.split(' ')[0]}, {meaning}",
        detail_rows=_rows(pairs),
        cta=_button(url, "View Your Project"),
    )
    text = _plain(
        "Project status updated",
        [meaning, ""] + [f"{label}: {value}" for label, value in pairs],
        url,
        "View Your Project",
    )
    return subject, html, text


def milestone_completed_client(milestone, project, client) -> tuple[str, str, str]:
    subject = f"Milestone Completed: {milestone.title}"
    url = _cta_url(f"/client/projects/{project.id}")

    pairs = [("Milestone", milestone.title), ("Project", project.title)]
    html = _shell(
        heading="Milestone completed",
        intro=(
            f"Hi {client.full_name.split(' ')[0]}, another step of your project is done — "
            "thanks for your patience as we keep things moving."
        ),
        detail_rows=_rows(pairs),
        cta=_button(url, "View Project Progress"),
    )
    text = _plain(
        "Milestone completed",
        [f"{label}: {value}" for label, value in pairs],
        url,
        "View Project Progress",
    )
    return subject, html, text


def invoice_created_client(invoice, client) -> tuple[str, str, str]:
    subject = f"Invoice {invoice.invoice_number} from {BRAND_NAME}"
    url = _cta_url(f"/client/invoices/{invoice.id}")

    pairs = [("Invoice", invoice.invoice_number), ("Total", _money(invoice.total))]
    if invoice.tax_rate is not None:
        pairs.append((f"Includes VAT ({invoice.tax_rate}%)", _money(invoice.tax)))
    if invoice.due_date is not None:
        pairs.append(("Due", invoice.due_date.strftime("%d %b %Y")))

    # Deliberately no "pay online" wording — payment is arranged offline and
    # recorded by staff.
    note = (
        f'<p style="margin:18px 0 0 0;color:{MUTED};font-size:13px;line-height:1.6;">'
        "To arrange payment or ask anything about this invoice, just get in touch and "
        "we'll confirm the details with you.</p>"
    )

    html = _shell(
        heading="You have a new invoice",
        intro=f"Hi {client.full_name.split(' ')[0]}, here are the details of your invoice.",
        detail_rows=_rows(pairs),
        cta=_button(url, "View Invoice"),
        footer_note=note,
    )
    text = _plain(
        "You have a new invoice",
        [f"{label}: {value}" for label, value in pairs]
        + ["", "To arrange payment, get in touch and we'll confirm the details."],
        url,
        "View Invoice",
    )
    return subject, html, text


def payment_recorded_client(payment, invoice, client) -> tuple[str, str, str]:
    subject = f"Payment Received — {invoice.invoice_number}"
    url = _cta_url(f"/client/invoices/{invoice.id}")

    method = payment.method.value if hasattr(payment.method, "value") else str(payment.method)
    status = invoice.status.value if hasattr(invoice.status, "value") else str(invoice.status)

    pairs = [
        ("Invoice", invoice.invoice_number),
        ("Amount received", _money(payment.amount)),
        ("Method", method.replace("_", " ").title()),
        ("Balance due", _money(invoice.balance_due)),
        ("Status", status.replace("_", " ").title()),
    ]

    settled = invoice.balance_due is not None and Decimal(invoice.balance_due) <= 0
    intro = (
        f"Hi {client.full_name.split(' ')[0]}, thank you — we've recorded your payment"
        + (" and this invoice is now settled in full." if settled else ".")
    )

    html = _shell(
        heading="Payment received",
        intro=intro,
        detail_rows=_rows(pairs),
        cta=_button(url, "View Invoice"),
    )
    text = _plain(
        "Payment received",
        [f"{label}: {value}" for label, value in pairs],
        url,
        "View Invoice",
    )
    return subject, html, text

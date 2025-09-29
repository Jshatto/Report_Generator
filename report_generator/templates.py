"""Rendering helpers for human-friendly report outputs."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from .models import ReportSummary


def build_markdown_report(summary: ReportSummary) -> str:
    """Render the report as Markdown."""

    lines = ["# Financial Summary", ""]

    if not summary.transactions:
        lines.append("No transactions supplied.")
        return "\n".join(lines)

    lines.extend(_render_overview(summary))
    lines.append("")
    lines.extend(_render_category_table(summary))
    lines.append("")
    lines.extend(_render_daily_totals(summary))
    lines.append("")
    lines.append("## Transactions")
    lines.append("")
    lines.append("| Date | Category | Description | Amount |")
    lines.append("| --- | --- | --- | ---: |")
    for txn in summary.transactions:
        lines.append(
            f"| {txn.occurred_on.isoformat()} | {txn.category} | "
            f"{txn.description} | ${txn.amount:.2f} |"
        )

    return "\n".join(lines)


def build_html_report(summary: ReportSummary) -> str:
    """Render the report as a standalone HTML string."""

    totals_by_category = summary.totals_by_category
    transactions = summary.transactions

    total_revenue = sum(
        (total for total in totals_by_category.values() if total > 0),
        start=Decimal("0"),
    )
    total_expenses_signed = sum(
        (total for total in totals_by_category.values() if total < 0),
        start=Decimal("0"),
    )
    total_expenses = -total_expenses_signed
    gross_profit = total_revenue - total_expenses
    net_income = summary.total_amount

    category_count = len(totals_by_category)
    revenue_category_count = sum(
        1 for total in totals_by_category.values() if total > 0
    )
    expense_category_count = sum(
        1 for total in totals_by_category.values() if total < 0
    )
    neutral_category_count = category_count - revenue_category_count - expense_category_count
    transaction_count = len(transactions)
    totals_by_day = summary.totals_by_day
    day_count = len(totals_by_day)
    average_daily_total = (
        summary.total_amount / day_count if day_count else Decimal("0")
    )
    average_transaction = (
        sum((txn.amount for txn in transactions), start=Decimal("0")) / transaction_count
        if transaction_count
        else Decimal("0")
    )

    report_start: str | None
    report_end: str | None
    if transactions:
        report_start = min(txn.occurred_on for txn in transactions).strftime("%b %d, %Y")
        report_end = max(txn.occurred_on for txn in transactions).strftime("%b %d, %Y")
    else:
        report_start = None
        report_end = None

    generated_on = date.today().strftime("%b %d, %Y")

    def format_currency(value: Decimal) -> str:
        quantised = value.quantize(Decimal("0.01"))
        return f"${quantised:,.2f}"

    def build_category_section() -> str:
        if not totals_by_category:
            return (
                "<section class=\"section data-section\">\n"
                "  <div class=\"card card--bordered\">\n"
                "    <div class=\"card__header\">\n"
                "      <div><h2>Category Performance</h2><p>Totals grouped by account classification.</p></div>\n"
                "    </div>\n"
                "    <div class=\"card__body\">\n"
                "      <p class=\"empty-state\">No category totals available.</p>\n"
                "    </div>\n"
                "  </div>\n"
                "</section>"
            )

        rows = "\n".join(
            (
                "        <tr>\n"
                f"          <td>{category}</td>\n"
                f"          <td class=\"numeric\">{format_currency(total)}</td>\n"
                f"          <td><span class=\"pill {('pill--positive' if total > 0 else 'pill--negative' if total < 0 else 'pill--neutral')}\">{('Revenue' if total > 0 else 'Expense' if total < 0 else 'Neutral')}</span></td>\n"
                "        </tr>"
            )
            for category, total in totals_by_category.items()
        )

        return (
            "<section class=\"section data-section\">\n"
            "  <div class=\"card card--bordered\">\n"
            "    <div class=\"card__header\">\n"
            "      <div>\n"
            "        <h2>Category Performance</h2>\n"
            "        <p>How each category contributed to the reporting period.</p>\n"
            "      </div>\n"
            "      <span class=\"chart-badge\" aria-hidden=\"true\">table</span>\n"
            "    </div>\n"
            "    <div class=\"card__body\">\n"
            "      <table class=\"data-table\">\n"
            "        <thead><tr><th>Category</th><th class=\"numeric\">Total</th><th>Type</th></tr></thead>\n"
            "        <tbody>\n"
            f"{rows}\n"
            "        </tbody>\n"
            "      </table>\n"
            "    </div>\n"
            "  </div>\n"
            "</section>"
        )

    def build_daily_section() -> str:
        if not totals_by_day:
            return (
                "<section class=\"section data-section\">\n"
                "  <div class=\"card card--bordered\">\n"
                "    <div class=\"card__header\">\n"
                "      <div><h2>Daily Totals</h2><p>Trend of overall movement across the period.</p></div>\n"
                "    </div>\n"
                "    <div class=\"card__body\">\n"
                "      <p class=\"empty-state\">No daily totals available.</p>\n"
                "    </div>\n"
                "  </div>\n"
                "</section>"
            )

        rows = "\n".join(
            (
                "        <tr>\n"
                f"          <td>{day.strftime('%b %d, %Y')}</td>\n"
                f"          <td class=\"numeric\">{format_currency(total)}</td>\n"
                "        </tr>"
            )
            for day, total in sorted(totals_by_day.items())
        )

        return (
            "<section class=\"section data-section\">\n"
            "  <div class=\"card card--bordered\">\n"
            "    <div class=\"card__header\">\n"
            "      <div>\n"
            "        <h2>Daily Totals</h2>\n"
            "        <p>Momentum of the business day by day.</p>\n"
            "      </div>\n"
            "      <span class=\"chart-badge\" aria-hidden=\"true\">trend</span>\n"
            "    </div>\n"
            "    <div class=\"card__body\">\n"
            "      <table class=\"data-table\">\n"
            "        <thead><tr><th>Date</th><th class=\"numeric\">Total</th></tr></thead>\n"
            "        <tbody>\n"
            f"{rows}\n"
            "        </tbody>\n"
            "      </table>\n"
            "    </div>\n"
            "  </div>\n"
            "</section>"
        )

    def build_transaction_section() -> str:
        if not transactions:
            return (
                "<section class=\"section data-section\">\n"
                "  <div class=\"card card--bordered\">\n"
                "    <div class=\"card__header\">\n"
                "      <div><h2>Transactions</h2><p>Itemised view of the activity powering this report.</p></div>\n"
                "    </div>\n"
                "    <div class=\"card__body\">\n"
                "      <p class=\"empty-state\">No transactions supplied.</p>\n"
                "    </div>\n"
                "  </div>\n"
                "</section>"
            )

        rows = "\n".join(
            (
                "        <tr>\n"
                f"          <td>{txn.occurred_on.strftime('%b %d, %Y')}</td>\n"
                f"          <td>{txn.category}</td>\n"
                f"          <td>{txn.description}</td>\n"
                f"          <td class=\"numeric\">{format_currency(txn.amount)}</td>\n"
                "        </tr>"
            )
            for txn in transactions
        )

        return (
            "<section class=\"section data-section\">\n"
            "  <div class=\"card card--bordered\">\n"
            "    <div class=\"card__header\">\n"
            "      <div>\n"
            "        <h2>Transactions</h2>\n"
            "        <p>Itemised view of the activity powering this report.</p>\n"
            "      </div>\n"
            "      <span class=\"chart-badge\" aria-hidden=\"true\">ledger</span>\n"
            "    </div>\n"
            "    <div class=\"card__body\">\n"
            "      <table class=\"data-table\">\n"
            "        <thead><tr><th>Date</th><th>Category</th><th>Description</th><th class=\"numeric\">Amount</th></tr></thead>\n"
            "        <tbody>\n"
            f"{rows}\n"
            "        </tbody>\n"
            "      </table>\n"
            "    </div>\n"
            "  </div>\n"
            "</section>"
        )

    kpi_cards = "\n".join(
        (
            "        <article class=\"kpi-card\">\n"
            f"          <h3>Total Revenue</h3>\n"
            f"          <p class=\"kpi-card__value\">{format_currency(total_revenue)}</p>\n"
            "          <p class=\"kpi-card__meta\">Income across positive categories.</p>\n"
            "        </article>",
            "        <article class=\"kpi-card\">\n"
            f"          <h3>Total Expenses</h3>\n"
            f"          <p class=\"kpi-card__value\">{format_currency(total_expenses)}</p>\n"
            "          <p class=\"kpi-card__meta\">Combined outflow from expense accounts.</p>\n"
            "        </article>",
            "        <article class=\"kpi-card\">\n"
            f"          <h3>Gross Profit</h3>\n"
            f"          <p class=\"kpi-card__value\">{format_currency(gross_profit)}</p>\n"
            "          <p class=\"kpi-card__meta\">Revenue minus expense allocations.</p>\n"
            "        </article>",
            "        <article class=\"kpi-card\">\n"
            f"          <h3>Net Income</h3>\n"
            f"          <p class=\"kpi-card__value\">{format_currency(net_income)}</p>\n"
            "          <p class=\"kpi-card__meta\">Overall movement for the reporting window.</p>\n"
            "        </article>",
        )
    )

    analysis_cards = "\n".join(
        (
            "          <article class=\"insight-card\">\n"
            "            <h3>Category Coverage</h3>\n"
            f"            <p class=\"insight-card__value\">{category_count}</p>\n"
            "            <p class=\"insight-card__meta\">Total categories monitored across the report.</p>\n"
            "          </article>",
            "          <article class=\"insight-card\">\n"
            "            <h3>Revenue vs Expense Mix</h3>\n"
            f"            <p class=\"insight-card__value\">{revenue_category_count}:{expense_category_count}</p>\n"
            "            <p class=\"insight-card__meta\">Distribution of income and expense groupings.</p>\n"
            "          </article>",
            "          <article class=\"insight-card\">\n"
            "            <h3>Neutral Categories</h3>\n"
            f"            <p class=\"insight-card__value\">{neutral_category_count}</p>\n"
            "            <p class=\"insight-card__meta\">Accounts that net to zero within the period.</p>\n"
            "          </article>",
            "          <article class=\"insight-card\">\n"
            "            <h3>Average Daily Movement</h3>\n"
            f"            <p class=\"insight-card__value\">{format_currency(average_daily_total)}</p>\n"
            "            <p class=\"insight-card__meta\">Total impact divided by the number of active days.</p>\n"
            "          </article>",
            "          <article class=\"insight-card\">\n"
            "            <h3>Average Transaction</h3>\n"
            f"            <p class=\"insight-card__value\">{format_currency(average_transaction)}</p>\n"
            "            <p class=\"insight-card__meta\">Mean amount across {transaction_count} transactions.</p>\n"
            "          </article>",
        )
    )

    hero_period = (
        f"<p class=\"hero__meta\">Reporting period: {report_start} – {report_end}</p>"
        if report_start and report_end
        else "<p class=\"hero__meta\">Reporting period unavailable.</p>"
    )

    hero_transactions = (
        f"<p class=\"hero__meta\">{transaction_count} transactions across {category_count} categories.</p>"
    )

    body_sections = "\n".join(
        (
            build_category_section(),
            build_daily_section(),
            build_transaction_section(),
        )
    )

    return (
        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        "  <meta charset=\"utf-8\">\n"
        "  <title>Financial Summary</title>\n"
        "  <style>\n"
        "    :root {\n"
        "      --brand-bg: #0f172a;\n"
        "      --brand-surface: #0b1220;\n"
        "      --brand-primary: #1e3a8a;\n"
        "      --brand-accent: #38bdf8;\n"
        "      --brand-surface-2: #f8fafc;\n"
        "      --text-strong: #111827;\n"
        "      --text: #1f2937;\n"
        "      --text-subtle: #64748b;\n"
        "      --line: #e2e8f0;\n"
        "      --surface: #ffffff;\n"
        "      --shadow-lg: 0 18px 40px rgba(15, 23, 42, .18);\n"
        "      --shadow-md: 0 12px 24px rgba(15, 23, 42, .12);\n"
        "      --radius-xl: 18px;\n"
        "    }\n"
        "    * { box-sizing: border-box; }\n"
        "    body {\n"
        "      margin: 0;\n"
        "      font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;\n"
        "      background:\n"
        "        radial-gradient(1200px 600px at -10% -10%, rgba(30, 58, 138, .20), transparent 60%),\n"
        "        radial-gradient(900px 600px at 110% -20%, rgba(14, 116, 144, .18), transparent 55%),\n"
        "        linear-gradient(180deg, var(--brand-surface), #0b1022 65%);\n"
        "      color: var(--text);\n"
        "      -webkit-font-smoothing: antialiased;\n"
        "    }\n"
        "    .wrap { max-width: 1100px; margin: 40px auto; padding: 0 24px; }\n"
        "    .shell {\n"
        "      background: var(--surface);\n"
        "      border: 1px solid rgba(226, 232, 240, .9);\n"
        "      border-radius: 26px;\n"
        "      box-shadow: var(--shadow-lg);\n"
        "      overflow: hidden;\n"
        "    }\n"
        "    .hero {\n"
        "      background: linear-gradient(160deg, rgba(255,255,255,.98), rgba(241,245,249,.92));\n"
        "      padding: 48px 40px;\n"
        "      display: grid;\n"
        "      gap: 18px;\n"
        "      text-align: center;\n"
        "      border-bottom: 1px solid var(--line);\n"
        "    }\n"
        "    .hero__title {\n"
        "      margin: 0;\n"
        "      font-size: 32px;\n"
        "      font-weight: 800;\n"
        "      color: var(--text-strong);\n"
        "      letter-spacing: -0.02em;\n"
        "    }\n"
        "    .hero__meta {\n"
        "      margin: 4px 0;\n"
        "      color: var(--text-subtle);\n"
        "      font-size: 14px;\n"
        "    }\n"
        "    .hero__footer {\n"
        "      display: flex;\n"
        "      justify-content: center;\n"
        "      gap: 12px;\n"
        "      flex-wrap: wrap;\n"
        "      font-size: 12px;\n"
        "      color: var(--text-subtle);\n"
        "    }\n"
        "    .hero__badge {\n"
        "      background: rgba(30, 64, 175, .08);\n"
        "      color: var(--brand-primary);\n"
        "      border-radius: 999px;\n"
        "      padding: 6px 14px;\n"
        "      font-weight: 600;\n"
        "      letter-spacing: .02em;\n"
        "    }\n"
        "    .section { padding: 32px 40px; }\n"
        "    .kpi-section { background: rgba(248, 250, 252, .75); }\n"
        "    .kpi-grid {\n"
        "      display: grid;\n"
        "      gap: 18px;\n"
        "      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));\n"
        "    }\n"
        "    .kpi-card {\n"
        "      background: var(--surface);\n"
        "      border: 1px solid rgba(226, 232, 240, .9);\n"
        "      border-radius: 20px;\n"
        "      padding: 20px;\n"
        "      box-shadow: var(--shadow-md);\n"
        "      text-align: left;\n"
        "    }\n"
        "    .kpi-card h3 {\n"
        "      margin: 0 0 12px 0;\n"
        "      font-size: 15px;\n"
        "      letter-spacing: .02em;\n"
        "      text-transform: uppercase;\n"
        "      color: var(--text-subtle);\n"
        "    }\n"
        "    .kpi-card__value {\n"
        "      margin: 0;\n"
        "      font-size: 26px;\n"
        "      font-weight: 800;\n"
        "      color: var(--brand-primary);\n"
        "    }\n"
        "    .kpi-card__meta {\n"
        "      margin: 10px 0 0 0;\n"
        "      color: var(--text-subtle);\n"
        "      font-size: 13px;\n"
        "      line-height: 1.4;\n"
        "    }\n"
        "    .analysis-card {\n"
        "      margin-bottom: 32px;\n"
        "    }\n"
        "    .analysis-card h2 {\n"
        "      margin: 0;\n"
        "      font-size: 20px;\n"
        "      color: var(--text-strong);\n"
        "    }\n"
        "    .analysis-card p {\n"
        "      margin: 6px 0 0 0;\n"
        "      color: var(--text-subtle);\n"
        "    }\n"
        "    .analysis-grid {\n"
        "      margin-top: 24px;\n"
        "      display: grid;\n"
        "      gap: 16px;\n"
        "      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));\n"
        "    }\n"
        "    .insight-card {\n"
        "      background: var(--brand-surface-2);\n"
        "      border: 1px solid rgba(226, 232, 240, .9);\n"
        "      border-left: 4px solid var(--brand-primary);\n"
        "      border-radius: 16px;\n"
        "      padding: 18px 20px;\n"
        "      box-shadow: var(--shadow-md);\n"
        "    }\n"
        "    .insight-card h3 {\n"
        "      margin: 0;\n"
        "      font-size: 15px;\n"
        "      color: var(--text-subtle);\n"
        "      text-transform: uppercase;\n"
        "      letter-spacing: .08em;\n"
        "    }\n"
        "    .insight-card__value {\n"
        "      margin: 12px 0 0 0;\n"
        "      font-size: 24px;\n"
        "      font-weight: 800;\n"
        "      color: var(--text-strong);\n"
        "    }\n"
        "    .insight-card__meta {\n"
        "      margin: 6px 0 0 0;\n"
        "      color: var(--text-subtle);\n"
        "      font-size: 13px;\n"
        "      line-height: 1.5;\n"
        "    }\n"
        "    .data-section {\n"
        "      background: rgba(248, 250, 252, .6);\n"
        "    }\n"
        "    .card {\n"
        "      background: var(--surface);\n"
        "      border: 1px solid rgba(226, 232, 240, .95);\n"
        "      border-radius: 20px;\n"
        "      box-shadow: var(--shadow-md);\n"
        "      padding: 0;\n"
        "      overflow: hidden;\n"
        "    }\n"
        "    .card--bordered {\n"
        "      border-left: 5px solid var(--brand-primary);\n"
        "    }\n"
        "    .card__header {\n"
        "      display: flex;\n"
        "      justify-content: space-between;\n"
        "      align-items: flex-start;\n"
        "      gap: 20px;\n"
        "      padding: 22px 26px 0 26px;\n"
        "    }\n"
        "    .card__header h2 {\n"
        "      margin: 0;\n"
        "      font-size: 20px;\n"
        "      color: var(--text-strong);\n"
        "    }\n"
        "    .card__header p {\n"
        "      margin: 6px 0 0 0;\n"
        "      color: var(--text-subtle);\n"
        "      font-size: 14px;\n"
        "    }\n"
        "    .card__body { padding: 22px 26px 28px 26px; }\n"
        "    .chart-badge {\n"
        "      display: inline-flex;\n"
        "      align-items: center;\n"
        "      justify-content: center;\n"
        "      background: rgba(30, 64, 175, .1);\n"
        "      color: var(--brand-primary);\n"
        "      border-radius: 999px;\n"
        "      padding: 6px 14px;\n"
        "      font-size: 12px;\n"
        "      font-weight: 700;\n"
        "      letter-spacing: .08em;\n"
        "      text-transform: uppercase;\n"
        "    }\n"
        "    .data-table {\n"
        "      width: 100%;\n"
        "      border-collapse: collapse;\n"
        "      margin-top: 12px;\n"
        "      font-size: 14px;\n"
        "    }\n"
        "    .data-table thead th {\n"
        "      text-align: left;\n"
        "      padding: 12px 16px;\n"
        "      background: rgba(15, 23, 42, .04);\n"
        "      color: var(--text-subtle);\n"
        "      font-weight: 700;\n"
        "      letter-spacing: .03em;\n"
        "      text-transform: uppercase;\n"
        "    }\n"
        "    .data-table tbody td {\n"
        "      padding: 12px 16px;\n"
        "      border-bottom: 1px solid rgba(226, 232, 240, .8);\n"
        "    }\n"
        "    .data-table tbody tr:last-child td { border-bottom: none; }\n"
        "    .data-table .numeric { text-align: right; font-variant-numeric: tabular-nums; }\n"
        "    .pill {\n"
        "      display: inline-block;\n"
        "      padding: 6px 12px;\n"
        "      border-radius: 999px;\n"
        "      font-size: 12px;\n"
        "      font-weight: 700;\n"
        "      letter-spacing: .04em;\n"
        "      text-transform: uppercase;\n"
        "    }\n"
        "    .pill--positive { background: rgba(34, 197, 94, .14); color: #047857; }\n"
        "    .pill--negative { background: rgba(239, 68, 68, .12); color: #b91c1c; }\n"
        "    .pill--neutral { background: rgba(148, 163, 184, .18); color: #475569; }\n"
        "    .empty-state {\n"
        "      margin: 0;\n"
        "      padding: 18px;\n"
        "      background: rgba(226, 232, 240, .35);\n"
        "      border-radius: 16px;\n"
        "      color: var(--text-subtle);\n"
        "      text-align: center;\n"
        "    }\n"
        "    @media (max-width: 720px) {\n"
        "      .section { padding: 28px 20px; }\n"
        "      .hero { padding: 40px 24px; }\n"
        "      .card__header { flex-direction: column; align-items: flex-start; }\n"
        "    }\n"
        "  </style>\n"
        "</head>\n"
        "<body>\n"
        "  <div class=\"wrap\">\n"
        "    <div class=\"shell\">\n"
        "      <header class=\"hero\" role=\"banner\">\n"
        "        <div>\n"
        "          <p class=\"hero__meta\">Generated {generated_on}</p>\n"
        "          <h1 class=\"hero__title\">Financial Performance Report</h1>\n"
        f"          {hero_period}\n"
        f"          {hero_transactions}\n"
        "        </div>\n"
        "        <div class=\"hero__footer\">\n"
        "          <span class=\"hero__badge\">Automated insights</span>\n"
        "          <span class=\"hero__badge\">Ready for clients</span>\n"
        "        </div>\n"
        "      </header>\n"
        "      <section class=\"section kpi-section\" aria-label=\"Key financial metrics\">\n"
        "        <div class=\"kpi-grid\">\n"
        f"{kpi_cards}\n"
        "        </div>\n"
        "      </section>\n"
        "      <section class=\"section\" aria-labelledby=\"analysis-summary-heading\">\n"
        "        <div class=\"analysis-card\">\n"
        "          <h2 id=\"analysis-summary-heading\">Enhanced Analysis Summary</h2>\n"
        "          <p>A quick scan of structural health, activity mix and pacing.</p>\n"
        "        </div>\n"
        "        <div class=\"analysis-grid\">\n"
        f"{analysis_cards}\n"
        "        </div>\n"
        "      </section>\n"
        f"{body_sections}\n"
        "    </div>\n"
        "  </div>\n"
        "</body>\n"
        "</html>\n"
    )


def _render_overview(summary: ReportSummary, *, html: bool = False) -> list[str]:
    lines = ["## Overview" if not html else "<h2>Overview</h2>"]

    total = f"${summary.total_amount:.2f}"
    if html:
        lines.append(f"<p>Total amount: <strong>{total}</strong></p>")
    else:
        lines.append(f"Total amount: **{total}**")

    return lines


def _render_category_table(summary: ReportSummary, *, html: bool = False) -> list[str] | str:
    if html:
        rows = "\n".join(
            f"    <tr><td>{category}</td><td>${total:.2f}</td></tr>"
            for category, total in summary.totals_by_category.items()
        )
        return (
            "<h2>Totals by category</h2>\n"
            "<table>\n"
            "  <thead><tr><th>Category</th><th>Total</th></tr></thead>\n"
            "  <tbody>\n"
            f"{rows}\n"
            "  </tbody>\n"
            "</table>"
        )

    lines = ["## Totals by category", "", "| Category | Total |", "| --- | ---: |"]
    for category, total in summary.totals_by_category.items():
        lines.append(f"| {category} | ${total:.2f} |")
    return lines


def _render_daily_totals(summary: ReportSummary, *, html: bool = False) -> list[str] | str:
    if html:
        rows = "\n".join(
            f"    <tr><td>{day.isoformat()}</td><td>${total:.2f}</td></tr>"
            for day, total in summary.totals_by_day.items()
        )
        return (
            "<h2>Totals by day</h2>\n"
            "<table>\n"
            "  <thead><tr><th>Date</th><th>Total</th></tr></thead>\n"
            "  <tbody>\n"
            f"{rows}\n"
            "  </tbody>\n"
            "</table>"
        )

    lines = ["## Totals by day", "", "| Date | Total |", "| --- | ---: |"]
    for day, total in summary.totals_by_day.items():
        lines.append(f"| {day.isoformat()} | ${total:.2f} |")
    return lines


def _render_transaction_table(summary: ReportSummary) -> str:
    rows = "\n".join(
        "    <tr>"
        f"<td>{txn.occurred_on.isoformat()}</td>"
        f"<td>{txn.category}</td>"
        f"<td>{txn.description}</td>"
        f"<td>${txn.amount:.2f}</td>"
        "</tr>"
        for txn in summary.transactions
    )

    return (
        "<h2>Transactions</h2>\n"
        "<table>\n"
        "  <thead><tr><th>Date</th><th>Category</th><th>Description</th><th>Amount</th></tr></thead>\n"
        "  <tbody>\n"
        f"{rows}\n"
        "  </tbody>\n"
        "</table>"
    )

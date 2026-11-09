"""Shared bits for the banking curriculum lesson files."""

SRC = {
    "bpi_fy25": "[BPI 4Q & FY2025 earnings press release (2 Feb 2026)](https://www.bpi.com.ph/content/dam/regulatory-pdfs/investor-relations/presentations/2025/Press%20Release%20-%20BPI%204Q%20and%20FY25%20Earnings%20Announcement.pdf)",
    "bpi_deck": "[BPI 4Q & FY2025 investor presentation](https://www.bpi.com.ph/content/dam/regulatory-pdfs/investor-relations/presentations/2025/external%204Q%20and%20FY25%20BPI%20Presentation%20Deck.pdf)",
    "bpi_ir": "[BPI Investor Relations – financial highlights](https://www.bpi.com.ph/content/bpi/ph/en/about-bpi/investor-relations/financial-highlights.html)",
    "bpi_9m26": "[InsiderPH (22 Oct 2026): BPI 9-month profit dips 3% as provisions surge](https://insiderph.com/bpi-9-mo-profit-dips-3-despite-strong-lending-as-provisions-surge)",
    "rrr": "[Interaksyon/Philstar (24 Feb 2025): BSP cuts banks' reserve requirements from late March](https://interaksyon.philstar.com/business/2025/02/24/292298/bsp-cuts-banks-reserve-requirements-effective-from-late-march/)",
    "pdic": "[GMA News (2025): PDIC maximum deposit insurance coverage raised to ₱1M](https://www.gmanetwork.com/news/money/personalfinance/937698/maximum-deposit-insurance-coverage-by-pdic-raised-to-p1m/story)",
    "digital": "[PNA (24 Aug 2022): BSP – PH now has 6 digital banks](https://alpha.pna.gov.ph/articles/1182068)",
    "bsp": "[Bangko Sentral ng Pilipinas (bsp.gov.ph)](https://www.bsp.gov.ph)",
    "bcbs239": "[BCBS 239 – Principles for effective risk data aggregation and risk reporting (BIS, 2013)](https://www.bis.org/publ/bcbs239.htm)",
}

def verified(text):
    return f'<callout icon="✅" color="green_bg">\n<b>Publicly verified</b>\n\n{text.strip()}\n</callout>'

def illustrative(text):
    return f'<callout icon="🧪" color="gray_bg">\n<b>Illustrative example (made-up numbers)</b>\n\n{text.strip()}\n</callout>'

def tip(text):
    return f'<callout icon="🧭" color="blue_bg">\n{text.strip()}\n</callout>'

def answers(text):
    return f'<toggle heading="h3">\nAnswers (open after you try)\n\n{text.strip()}\n</toggle>'

def terms(rows):
    out = ["| Term | What it means |", "|---|---|"]
    out += [f"| **{a}** | {b} |" for a, b in rows]
    return "\n".join(out)

def sql(q):
    return "```sql\n" + q.strip() + "\n```"

def py(q):
    return "```python\n" + q.strip() + "\n```"

def lesson(n, module, title, level, focus, body):
    return dict(n=n, module=module, title=title, level=level, focus=focus, body=body.strip())

def code(q):
    return "```\n" + q.strip() + "\n```"

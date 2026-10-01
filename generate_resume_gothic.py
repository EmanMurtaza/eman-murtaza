from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    KeepTogether, PageBreak, Flowable, Image, FrameBreak,
)

OUTPUT = "Eman_Murtaza_Resume_Gothic.pdf"
PHOTO = "eman_gothic_portrait.png"

# ── Fonts (Palatino ships with Windows; serif suits the gothic tone) ─────────
F = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("Pal", f"{F}\\pala.ttf"))
pdfmetrics.registerFont(TTFont("Pal-B", f"{F}\\palab.ttf"))
pdfmetrics.registerFont(TTFont("Pal-I", f"{F}\\palai.ttf"))
pdfmetrics.registerFont(TTFont("Pal-BI", f"{F}\\palabi.ttf"))
pdfmetrics.registerFontFamily("Pal", normal="Pal", bold="Pal-B", italic="Pal-I", boldItalic="Pal-BI")

# ── Palette ──────────────────────────────────────────────────────────────────
BG      = colors.HexColor("#0a0709")
PANEL   = colors.HexColor("#150d12")
BLOOD   = colors.HexColor("#a3132b")
BLOOD_L = colors.HexColor("#d23a52")
BONE    = colors.HexColor("#e6dccf")
SILVER  = colors.HexColor("#b9b1b8")
DIM     = colors.HexColor("#857a82")
LINE    = colors.HexColor("#3a1620")

W, H = A4
LM = RM = 17 * mm
TM = 15 * mm
BM = 15 * mm
CW = W - LM - RM


# ── Page decoration ──────────────────────────────────────────────────────────
def diamond(c, x, y, r, fill=BLOOD):
    c.setFillColor(fill)
    p = c.beginPath()
    p.moveTo(x, y + r); p.lineTo(x + r * 0.62, y); p.lineTo(x, y - r); p.lineTo(x - r * 0.62, y)
    p.close()
    c.drawPath(p, fill=1, stroke=0)


def cross(c, x, y, s):
    c.setStrokeColor(BLOOD); c.setLineWidth(0.9)
    c.line(x, y - s, x, y + s * 1.5)
    c.line(x - s * 0.8, y + s * 0.6, x + s * 0.8, y + s * 0.6)


def corner(c, x, y, sx, sy):
    """Gothic corner bracket with a small diamond finial."""
    c.setStrokeColor(BLOOD); c.setLineWidth(1.1)
    L = 16 * mm
    c.line(x, y, x + sx * L, y)
    c.line(x, y, x, y + sy * L)
    c.setLineWidth(0.4)
    c.line(x + sx * 2.2 * mm, y + sy * 2.2 * mm, x + sx * (L - 4 * mm), y + sy * 2.2 * mm)
    c.line(x + sx * 2.2 * mm, y + sy * 2.2 * mm, x + sx * 2.2 * mm, y + sy * (L - 4 * mm))
    diamond(c, x + sx * L, y, 1.5 * mm)
    diamond(c, x, y + sy * L, 1.5 * mm)


def on_page(c, doc):
    c.saveState()
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    # faint crimson glow at the top
    for i in range(14):
        c.setFillColor(colors.Color(0.42, 0.04, 0.12, alpha=0.018))
        c.circle(W * 0.5, H + 20 * mm, 150 * mm - i * 7 * mm, fill=1, stroke=0)
    m = 7 * mm
    c.setStrokeColor(LINE); c.setLineWidth(0.5)
    c.rect(m, m, W - 2 * m, H - 2 * m, fill=0, stroke=1)
    corner(c, m, m, 1, 1)
    corner(c, W - m, m, -1, 1)
    corner(c, m, H - m, 1, -1)
    corner(c, W - m, H - m, -1, -1)
    cross(c, W / 2, m - 0.5 * mm, 1.6 * mm)
    c.setFont("Pal-I", 7)
    c.setFillColor(DIM)
    c.drawCentredString(W / 2, m + 2.2 * mm, f"\u2020  Eman Murtaza  \u00b7  {doc.page}  \u2020")
    c.restoreState()


class Rule(Flowable):
    """Thin crimson rule with a centred diamond."""
    def __init__(self, width, before=4, after=4):
        super().__init__()
        self.width, self.height, self._b, self._a = width, before + after + 4, before, after

    def draw(self):
        c = self.canv
        y = self._a + 2
        c.setStrokeColor(LINE); c.setLineWidth(0.6)
        c.line(0, y, self.width / 2 - 4 * mm, y)
        c.line(self.width / 2 + 4 * mm, y, self.width, y)
        diamond(c, self.width / 2, y, 1.4 * mm)
        diamond(c, self.width / 2 - 3 * mm, y, 0.8 * mm, SILVER)
        diamond(c, self.width / 2 + 3 * mm, y, 0.8 * mm, SILVER)


class Arch(Flowable):
    """Photo in a pointed arch with a double crimson border."""
    def __init__(self, path, w, h):
        super().__init__()
        self.path, self.width, self.height = path, w, h

    def draw(self):
        import math
        c = self.canv
        w, h = self.width, self.height
        def outline(inset):
            p = c.beginPath()
            ww, hh = w - 2 * inset, h - 2 * inset
            rr = ww * 0.75
            sp = math.sqrt(rr * rr - (ww / 2 - rr) ** 2)
            base = inset + hh - sp
            p.moveTo(inset, inset)
            p.lineTo(inset, base)
            n = 40
            for i in range(1, n + 1):
                x = i / n * ww / 2
                p.lineTo(inset + x, base + math.sqrt(max(rr * rr - (rr - x) ** 2, 0)))
            for i in range(n - 1, -1, -1):
                x = i / n * ww / 2
                p.lineTo(inset + ww - x, base + math.sqrt(max(rr * rr - (rr - x) ** 2, 0)))
            p.lineTo(inset + ww, inset)
            p.close()
            return p

        c.saveState()
        c.setFillColor(PANEL)
        c.drawPath(outline(0), fill=1, stroke=0)
        c.restoreState()
        c.drawImage(self.path, 0, 0, w, h, mask="auto")
        c.setStrokeColor(BLOOD); c.setLineWidth(1.3)
        c.drawPath(outline(0.6), fill=0, stroke=1)
        c.setStrokeColor(SILVER); c.setLineWidth(0.35)
        c.drawPath(outline(2.2), fill=0, stroke=1)


# ── Styles ───────────────────────────────────────────────────────────────────
def S(name, **kw):
    return ParagraphStyle(name, **kw)


sName    = S("Name", fontName="Pal-B", fontSize=31, leading=34, textColor=BONE, charSpace=2.2)
sTitle   = S("Title", fontName="Pal-I", fontSize=10.2, leading=14, textColor=BLOOD_L, charSpace=0.8)
sContact = S("Contact", fontName="Pal", fontSize=8.6, leading=13, textColor=SILVER)
sSec     = S("Sec", fontName="Pal-B", fontSize=10.5, leading=13, textColor=BLOOD_L, charSpace=3.2,
             spaceBefore=3, spaceAfter=3, alignment=TA_CENTER)
sBody    = S("Body", fontName="Pal", fontSize=9, leading=13.2, textColor=SILVER)
sRole    = S("Role", fontName="Pal-B", fontSize=10.6, leading=13, textColor=BONE)
sCo      = S("Co", fontName="Pal-I", fontSize=9, leading=12, textColor=BLOOD_L)
sDate    = S("Date", fontName="Pal-I", fontSize=8.5, leading=12, textColor=DIM, alignment=TA_RIGHT)
sBullet  = S("Bullet", fontName="Pal", fontSize=8.8, leading=12.4, textColor=SILVER, leftIndent=11, bulletIndent=1)
sProjT   = S("ProjT", fontName="Pal-B", fontSize=9.4, leading=12, textColor=BONE)
sProjD   = S("ProjD", fontName="Pal", fontSize=8.3, leading=11.6, textColor=SILVER)
sTech    = S("Tech", fontName="Pal-I", fontSize=7.6, leading=10, textColor=DIM)
sDeg     = S("Deg", fontName="Pal-B", fontSize=9.6, leading=12, textColor=BONE)
sSub     = S("Sub", fontName="Pal-I", fontSize=8.6, leading=11.5, textColor=BLOOD_L)
sSmall   = S("Small", fontName="Pal", fontSize=8.2, leading=11.4, textColor=SILVER)
sLbl     = S("Lbl", fontName="Pal-B", fontSize=8.4, leading=11, textColor=BLOOD_L, charSpace=1.8)
sFoot    = S("Foot", fontName="Pal-I", fontSize=8, leading=11, textColor=DIM, alignment=TA_CENTER)


def section(title):
    return [Spacer(1, 5), Paragraph(title.upper(), sSec), Rule(CW, 0, 3)]


def bullet(t):
    return Paragraph(t, sBullet, bulletText="\u2020")


def pad0(extra=()):
    return TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        *extra,
    ])


# ── Content ──────────────────────────────────────────────────────────────────
story = []

# Header: arch portrait | name + title + contact
PH_W, PH_H = 34 * mm, 45.3 * mm
contact = [
    "emanmurtaza2003@gmail.com", "+92 342 5194397  (WhatsApp)",
    "linkedin.com/in/emanmurtaza-1a9800255", "github.com/EmanMurtaza",
    "eman-murtaza.vercel.app", "Bahria Town, Rawalpindi, Pakistan",
]
right = [
    Paragraph("Eman Murtaza", sName),
    Spacer(1, 2),
    Paragraph("Software Engineer  \u2020  Project Manager  \u2020  Applied AI Researcher", sTitle),
    Spacer(1, 7),
    Paragraph("<br/>".join(contact), sContact),
]
hdr = Table([[Arch(PHOTO, PH_W, PH_H), right]], colWidths=[PH_W + 8 * mm, CW - PH_W - 8 * mm])
hdr.setStyle(pad0())
story += [hdr, Spacer(1, 4)]

story += section("Profile")
story.append(Paragraph(
    "Software Engineering graduate (BSSE, FUSST) and applied-AI practitioner with four-plus years across "
    "full-stack engineering (.NET / ASP.NET MVC, React, Flutter, React Native), software QA and technical "
    "project management. Leads delivery as <b>Software Project Manager</b> at Friendsware Solutions and "
    "co-founded <b>Autom8X Systems</b>, an AI-automation and web agency with 20+ repositories shipped across "
    "healthcare, real estate, e-commerce, hospitality, legal and construction-tech. Author of a DOI-registered "
    "study comparing zero-shot, few-shot and chain-of-thought prompting; currently extending into machine "
    "learning and formal verification. Seeking a Master\u2019s in Software Engineering with a focus on applied AI.",
    sBody))
story.append(Spacer(1, 3))
hl = Table([[
    Paragraph("<b>20+</b> repos shipped", sSmall),
    Paragraph("<b>DOI</b> published research", sSmall),
    Paragraph("<b>IELTS 8.0</b> (C1)", sSmall),
    Paragraph("<b>IBM</b> PM &amp; ML certified", sSmall),
]], colWidths=[CW / 4] * 4)
hl.setStyle(pad0([
    ("BACKGROUND", (0, 0), (-1, -1), PANEL),
    ("BOX", (0, 0), (-1, -1), 0.5, LINE),
    ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
    ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
]))
for i in range(4):
    hl._cellvalues[0][i].style = ParagraphStyle("hl", parent=sSmall, alignment=TA_CENTER, textColor=BONE)
story.append(hl)

# Experience
story += section("Work Experience")
jobs = [
    ("Software Project Manager", "Friendsware Solutions \u2014 Islamabad", "03/2026 \u2013 Present", [
        "Lead delivery of client and internal products across <b>.NET/ASP.NET, Flutter, React Native, Azure</b> and Plesk hosting.",
        "Primary bridge between engineering and clients: documentation, QA oversight, stakeholder communication.",
    ]),
    ("Co-Founder &amp; AI Automation Engineer", "Autom8X Systems \u2014 Remote", "09/2025 \u2013 Present", [
        "Co-founded and scaled an AI-automation and web agency; shipped sites and products for healthcare, real estate, "
        "e-commerce, hospitality, legal and construction-tech clients.",
        "Built LLM-integrated features such as <b>Aria</b>, a voice AI receptionist, applying and evaluating zero-shot, "
        "few-shot and chain-of-thought prompting in production.",
        "Recent work: NumidAI building-performance simulator, DrawToEstimate supplier marketplace prototype, "
        "MedcureRS landing template, and the agency\u2019s React/TypeScript portfolio site.",
    ]),
    ("Project Manager Intern", "Friendsware Solutions", "02/2026 \u2013 03/2026", [
        "Supported end-to-end project management across active client engagements; promoted to Software Project Manager.",
    ]),
    (".NET Developer Intern", "Friendsware Solutions \u2014 Gulberg Greens, Islamabad", "07/2025 \u2013 09/2025", [
        "Shipped features in <b>ASP.NET MVC, C# and Tailwind CSS</b>; owned database design, debugging and authorisation logic.",
    ]),
    ("Software QA Engineer Intern", "Quest \u2014 Islamabad", "07/2023 \u2013 09/2023", [
        "Executed unit, coverage and black-box testing across the software QA lifecycle.",
    ]),
]
for role, co, date, bl in jobs:
    head = Table([[Paragraph(role, sRole), Paragraph(date, sDate)]], colWidths=[CW * 0.68, CW * 0.32])
    head.setStyle(pad0())
    story.append(KeepTogether([head, Paragraph(co, sCo), Spacer(1, 1.5)] + [bullet(b) for b in bl] + [Spacer(1, 5)]))

# Projects start page 2
story.append(PageBreak())
story += section("Selected Projects")
projects = [
    ("SignLingo", "Final-year project: AI-powered sign-language recognition system.", "AI \u00b7 Computer Vision"),
    ("Aria \u2014 Remote Desk Assistant", "Voice-enabled AI receptionist with real-time voice I/O.", "Groq \u00b7 Gemini \u00b7 JS"),
    ("NumidAI Platform", "Interactive building-climate simulator: rules-based engine, results dashboard, ranked passive-design recommendations.", "TypeScript \u00b7 React"),
    ("C# to UPPAAL Translator", "Converts C# code into UPPAAL timed-automata models; GUI with xUnit coverage of requirements and domain generation.", "C# \u00b7 xUnit \u00b7 Formal verification"),
    ("Iris Classification", "scikit-learn logistic regression on the Iris dataset; 80/20 split, 100% test accuracy.", "Python \u00b7 pandas \u00b7 Jupyter"),
    ("PharmAudit", "Pharmacy audit management MVP with full-stack CRUD and reporting.", "React \u00b7 Express \u00b7 SQLite"),
    ("DrawToEstimate Marketplace", "Clickable supplier marketplace prototype: slab listings, compare and quote flow, supplier dashboard.", "HTML \u00b7 CSS \u00b7 JS"),
    ("MedcureRS \u00b7 Murtaza Medical \u00b7 DGC Rx", "Healthcare web platforms: branded landing template, WhatsApp-API booking and digital prescriptions.", "HTML \u00b7 JS \u00b7 WhatsApp API"),
    ("VESSEL \u00b7 VACUO \u00b7 Realtor Site", "Commerce and lead-gen storefronts, one with an integrated AI assistant.", "TypeScript"),
    ("Autom8X Portfolio \u00b7 Admin Dashboard", "Agency marketing site and a custom analytics admin panel.", "React \u00b7 TypeScript \u00b7 Vite"),
]
cells = []
for t, d, tech in projects:
    cells.append([Paragraph(t, sProjT), Spacer(1, 1.5), Paragraph(d, sProjD), Spacer(1, 2), Paragraph(tech, sTech)])
rows = [cells[i:i + 2] for i in range(0, len(cells), 2)]
pt = Table(rows, colWidths=[CW / 2] * 2)
pt.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("BACKGROUND", (0, 0), (-1, -1), PANEL),
    ("BOX", (0, 0), (-1, -1), 0.5, LINE),
    ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
    ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(pt)

# Education | Publication & certifications
story += section("Education &amp; Credentials")
left = [
    Paragraph("EDUCATION", sLbl), Spacer(1, 3),
    Paragraph("BSc Software Engineering", sDeg),
    Paragraph("Foundation University School of Science &amp; Technology, Rawalpindi", sSub),
    Paragraph("09/2021 \u2013 09/2025 \u00b7 CGPA 3.12 / 4.0", sSmall),
    Paragraph("FYP: SignLingo \u2014 AI sign-language recognition", sSmall),
    Spacer(1, 5),
    Paragraph("SSC Technology", sDeg),
    Paragraph("Dr. AQ Khan College of Science, Bahria Town", sSub),
    Paragraph("Completed 2020", sSmall),
]
right = [
    Paragraph("CERTIFICATIONS", sLbl), Spacer(1, 3),
    Paragraph("Introduction to Project Management \u2014 IBM / Coursera (09/2026)", sSmall),
    Paragraph("Exploratory Data Analysis for Machine Learning \u2014 IBM / Coursera (09/2026)", sSmall),
    Spacer(1, 5),
    Paragraph("PUBLICATION", sLbl), Spacer(1, 3),
    Paragraph("<i>Prompt Engineering: Techniques, Empirical Study, and Future Directions.</i> Zenodo preprint, 2026. "
              "DOI 10.5281/zenodo.22340142", sSmall),
]
ed = Table([[left, right]], colWidths=[CW * 0.5, CW * 0.5])
ed.setStyle(pad0([("RIGHTPADDING", (0, 0), (0, 0), 10), ("LEFTPADDING", (1, 0), (1, 0), 10),
                  ("LINEAFTER", (0, 0), (0, 0), 0.5, LINE)]))
story.append(ed)

# Skills
story += section("Arsenal")
skills = [
    ("AI &amp; Research", "Prompt engineering, LLM evaluation, Groq / Gemini / OpenAI-class APIs, scikit-learn, pandas"),
    ("Engineering", "C# / .NET / ASP.NET MVC, React, TypeScript, JavaScript, Node / Express, Python, Flutter, React Native, Tailwind, GSAP"),
    ("Data &amp; Cloud", "SQL Server, SQLite, Azure, Vercel, Netlify, Plesk, WhatsApp Business API"),
    ("Delivery", "Agile / Scrum, Kanban, ClickUp, Jira, Git / GitHub, Figma, QA (unit, black-box, coverage)"),
    ("Languages", "Urdu (native) \u00b7 English C1 (IELTS 8.0)"),
]
st = Table([[Paragraph(k.upper(), sLbl), Paragraph(v, sSmall)] for k, v in skills], colWidths=[28 * mm, CW - 28 * mm])
st.setStyle(pad0([("BOTTOMPADDING", (0, 0), (-1, -1), 3.5)]))
story.append(st)
story += [Spacer(1, 4), Rule(CW, 0, 2),
          Paragraph("\u201cPer aspera ad astra\u201d  \u00b7  github.com/EmanMurtaza  \u00b7  eman-murtaza.vercel.app", sFoot)]


# ── Build ────────────────────────────────────────────────────────────────────
doc = BaseDocTemplate(OUTPUT, pagesize=A4, leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
                      title="Eman Murtaza \u2014 Resume", author="Eman Murtaza")
frame = Frame(LM, BM, CW, H - TM - BM, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=on_page)])
doc.build(story)
print("saved", OUTPUT)

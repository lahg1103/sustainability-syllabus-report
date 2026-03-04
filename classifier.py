import re
from pathlib import Path
import fitz
from docx import Document

SUSTAINABILITY_TERMS = [
    r"\benvironmental\b", r"\becosystem(?:s)?\b",
    r"\bsustain(?:able|ability|)\b",
    r"\bgreen\s+engineering\b", r"\bgreen\s+chemistry\b",
    r"\breuse\b", r"\breduce\b", r"\brecycle\b",
    r"\breduce\s+(?:cost|waste|hazard)\b",
    r"\bpollutants?\b", r"\bpollution\b",
    r"\bcontaminants?\b", r"\bemissions?\b",
    r"\bgas\s+emissions\b", r"\bgreenhouse\b",
    r"\benvironmental\s+impact\b",
    r"\bcleanup\b", r"\bair\s+quality\b", r"\bwater\s+quality\b",
    r"\becosystem\s+services\b",
    r"\bclimate\b",
    r"\bcarbon\b",
    r"\brenewable\b",
    r"\bconservation\b",
    r"\bbiodiversity\b",
    r"\benergy\s+efficiency\b",
    r"\benvironmental\s+justice\b",
    r"\bsustainable\s+development\b",

    r"\bsustainable\s+communities\b",
    r"\bbenefit(?:\s+communities|\s+environment)?\b",
    r"\bcollaborative\b", r"\bcollaboration\b",
    r"\bprotect\s+health\b", r"\bimprove\s+health\b",
    r"\bresource\s+security\b",
    r"\bfuture\s+generations\b",
    r"\bsustainable\s+living\b",

    r"\bcost\s+benefit\s+analysis\b",
    r"\blifecycle\b",
    r"\brisk\s+reduction\b", r"\breduce\s+risk\b",
    r"\bresilien(?:t|ce)\b",
]
SUSTAIN_RX = re.compile("|".join(SUSTAINABILITY_TERMS), re.I)

ASSIGNMENT_TERMS = [
    r"\bassignment(?:s)?\b",
    r"\bproject(?:s)?\b",
    r"\bpaper(?:s)?\b",
    r"\bessay(?:s)?\b",
    r"\bgraded\b",
    r"\brubric\b",
    r"\bdeliverable(?:s)?\b",
    r"\bcapstone\b",
    r"\bpresentation(?:s)?\b"
]

ASSIGN_RX = re.compile("|".join(ASSIGNMENT_TERMS), re.I)

def extract_text_docx(file):
    doc = Document(file)
    full_text = []
    
    for para in doc.paragraphs:
        full_text.append(para.text)
    
    return "\n".join(full_text)

def extract_text_pdf_from_path(file_path):
    doc = fitz.open(file_path)
    text = "".join(page.get_text() or "" for page in doc)
    doc.close()
    return text

def classify_text(text: str):

    text_lower = text.lower()

    sustain_matches = list(SUSTAIN_RX.finditer(text_lower))

    # no match/weak match
    if len(sustain_matches) < 2:
        return 0, ""

    assign_matches = list(ASSIGN_RX.finditer(text_lower))

    sustain_hits = [m.start() for m in sustain_matches]
    assign_hits = [m.start() for m in assign_matches]

    window = 300

    for s in sustain_hits:
        for a in assign_hits:
            if abs(s - a) <= window:
                match = sustain_matches[0]
                evidence = text[max(0, match.start()-200):match.end()+200]
                return 2, evidence

    # mentions
    match = sustain_matches[0]
    evidence = text[max(0, match.start()-200):match.end()+200]
    return 1, evidence

def analyze_folder(folder_path: Path):
    rows = []

    for file_path in folder_path.rglob("*"):
        if not file_path.is_file():
            continue

        ext = file_path.suffix.lower()

        text = ""

        try:
            if ext == ".pdf":
                text = extract_text_pdf_from_path(file_path)

            elif ext == ".docx":
                text = extract_text_docx(file_path)

            elif ext == ".txt":
                text = file_path.read_text(errors="ignore")

            else:
                continue  # skip other file types (for now)

            tier, evidence = classify_text(text)

            rows.append({
                "filename": file_path.name,
                "tier": tier,
                "evidence": evidence[:500]
            })

        except Exception as e:
            rows.append({
                "filename": file_path.name,
                "tier": "ERROR",
                "evidence": str(e)
            })

    return rows
import os
import yaml
import subprocess
from pathlib import Path
from docx import Document
from google import genai
import re

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
TEMPLATES_DIR = ROOT / "templates"
CUSTOMERS_DIR = ROOT / "customers"
OUTPUTS_DIR = ROOT / "outputs"


def read_universal_docs():
    content = []

    supported_ext = [".md", ".txt", ".docx"]

    for file_path in DOCS_DIR.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in supported_ext:
            #Load file with .md and .txt suffix 
            if file_path.suffix.lower() in [".md", ".txt"]:
                text = file_path.read_text(encoding="utf-8", errors="ignore")
            #Load file with .docx suffix
            elif file_path.suffix.lower() == ".docx":
                doc = Document(file_path)
                text = "\n".join([p.text for p in doc.paragraphs])
# Append file content with a header indicating the source file
            content.append(f"\n\n--- SOURCE FILE: {file_path.name} ---\n{text}")
    print(f"Loaded {len(content)} universal documentation files.")
    # Combine all content into a single string
    return "\n".join(content)

# Load customer configuration from YAML file
def load_customer(customer_file):
    with open(customer_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def generate_custom_doc(universal_docs, customer):
    prompt = f"""
You are a technical documentation agent.

You must customize product documentation using ONLY the universal documentation below.

Universal documentation:
{universal_docs}

Customer configuration:
{customer}


Task:
Create a customized customer-use product document.

Rules:
- Use clear headings.
- Be professional.
- Do not invent unsupported features.
- Adapt language to the customer's industry.
- Mention the customer name where appropriate.
- Be simple and straightforward, with customer perspective.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text

def add_bold_text(doc, text):
    parts = re.split(r"(\*\*.*?\*\*)", text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            run = doc.add_run(part[2:-2])
            run.bold = True
        else:
            doc.add_run(part)

def save_docx(content, output_path, customer_name):
    doc = Document()
    doc.add_heading(f"{customer_name} - Customized Product Documentation", level=0).bold = True
    #Generated content one line at a time.
    for line in content.split("\n"):
        #remove extra whitespace from the line
        line = line.strip()

        if not line:
            continue
        elif line.startswith("# "):
            doc.add_heading(line.replace("# ", ""), level=1)
        elif line.startswith("## "):
            doc.add_heading(line.replace("## ", ""), level=2)
        elif line.startswith("### "):
            doc.add_heading(line.replace("### ", ""), level=3)
        elif line.startswith("* "):
            bullet_text = line[2:].strip()
            paragraph = doc.add_paragraph( style="List Bullet")
            add_bold_text(paragraph, bullet_text)
        else:
            p = doc.add_paragraph()
            add_bold_text(p, line)

    doc.save(output_path)


def convert_to_pdf(docx_path, output_dir):
    try:
        subprocess.run([
            "soffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_dir),
            str(docx_path)
        ], check=True)
    except FileNotFoundError:
        print("PDF conversion skipped: LibreOffice is not installed or 'soffice' is not in PATH.")


def generate_for_customer(customer_file):
    customer = load_customer(customer_file)
    universal_docs = read_universal_docs()

    customer_name = customer["customer_name"]
    #replace spaces with underscores for output file naming, and convert to lowercase
    output_name = customer.get("output_name", customer_name.lower().replace(" ", "_"))

    output_folder = OUTPUTS_DIR / output_name
    output_folder.mkdir(parents=True, exist_ok=True)

    content = generate_custom_doc(universal_docs, customer)

    docx_path = output_folder / f"{output_name}.docx"
    save_docx(content, docx_path, customer_name)

    convert_to_pdf(docx_path, output_folder)

    print(f"Generated files for {customer_name}")
    print(f"DOCX: {docx_path}")


def main():
    customer_files = list(CUSTOMERS_DIR.glob("*.yaml"))

    if not customer_files:
        print("No customer YAML files found.")
        return

    for customer_file in customer_files:
        generate_for_customer(customer_file)

if __name__ == "__main__":
    main()
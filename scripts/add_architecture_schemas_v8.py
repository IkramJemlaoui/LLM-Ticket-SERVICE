"""Add the six reference schemas to the approved v7 architecture report."""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_ROW_HEIGHT_RULE, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "deliverables" / "AegisDesk_AI_Architecture_5_Pages_v7.docx"
OUTPUT = ROOT / "deliverables" / "AegisDesk_AI_Architecture_5_Pages_v9_Ollama.docx"

NAVY = "14324F"
WHITE = "FFFFFF"
COLORS = {
    "business": ("2452A4", "EAF1FD"),
    "agentic": ("7137A6", "F2EAFB"),
    "llm": ("078F91", "E7F7F6"),
    "data": ("238BC1", "EAF6FC"),
    "governance": ("E78A12", "FFF4E5"),
    "operations": ("4B941E", "EEF7E9"),
}


def shade(cell, color: str) -> None:
    properties = cell._tc.get_or_add_tcPr()
    element = properties.find(qn("w:shd"))
    if element is None:
        element = OxmlElement("w:shd")
        properties.append(element)
    element.set(qn("w:fill"), color)


def margins(cell, top=60, start=70, bottom=60, end=70) -> None:
    properties = cell._tc.get_or_add_tcPr()
    tc_mar = properties.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        properties.append(tc_mar)
    for name, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{name}"))
        if node is None:
            node = OxmlElement(f"w:{name}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def borders(cell, color: str, size="7") -> None:
    properties = cell._tc.get_or_add_tcPr()
    tc_borders = properties.first_child_found_in("w:tcBorders")
    if tc_borders is None:
        tc_borders = OxmlElement("w:tcBorders")
        properties.append(tc_borders)
    for edge in ("top", "left", "bottom", "right"):
        node = tc_borders.find(qn(f"w:{edge}"))
        if node is None:
            node = OxmlElement(f"w:{edge}")
            tc_borders.append(node)
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), size)
        node.set(qn("w:color"), color)


def text(cell, heading: str, detail: str = "", *, color=NAVY, size=6.7,
         center=True, white=False) -> None:
    cell.text = ""
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    margins(cell)
    paragraph = cell.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.LEFT
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.line_spacing = 0.9
    run = paragraph.add_run(heading)
    run.bold = True
    run.font.name = "Aptos"
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(WHITE if white else color)
    if detail:
        paragraph.add_run("\n")
        run = paragraph.add_run(detail)
        run.font.name = "Aptos"
        run.font.size = Pt(size - 0.5)
        run.font.color.rgb = RGBColor.from_string(WHITE if white else NAVY)


def move_after(table, anchor) -> None:
    element = anchor._tbl if hasattr(anchor, "_tbl") else anchor._p
    element.addnext(table._tbl)


def remove_paragraph(paragraph) -> None:
    element = paragraph._element
    element.getparent().remove(element)


def update_local_llm_text(document) -> None:
    paragraphs = list(document.paragraphs)
    paragraphs.extend(
        paragraph
        for table in document.tables
        for row in table.rows
        for cell in row.cells
        for paragraph in cell.paragraphs
    )
    for paragraph in paragraphs:
        for run in paragraph.runs:
            value = run.text
            if value.startswith("The application now defaults to a real OpenAI-compatible deployment"):
                run.text = (
                    "The application now defaults to Qwen 2.5 running locally through Ollama. "
                    "The Triage and Resolution agents use strict JSON Schema outputs, a bounded output budget "
                    "and a local request timeout. Safety, retrieval, routing and validation remain controlled. "
                    "If Ollama or the model is unavailable, the failure is visible; the application never "
                    "presents a simulated result as live model output."
                )
            elif value.startswith("OpenAI Responses API"):
                run.text = "Ollama documentation — https://docs.ollama.com/"
            elif "LLM_PROVIDER=openai" in value:
                run.text = (
                    "LLM_PROVIDER=ollama · OLLAMA_BASE_URL=http://localhost:11434/v1 · "
                    "OLLAMA_MODEL=qwen2.5:latest · no API key or per-request fee"
                )
            elif "cloud inference" in value:
                run.text = value.replace("cloud inference", "model inference")


def schema(document, anchor, title: str, steps: list[tuple[str, str]], accent: str,
           pale: str, footer: str | None = None, arrows=True):
    column_count = len(steps) * 2 - 1 if arrows else len(steps)
    row_count = 3 if footer else 2
    table = document.add_table(rows=row_count, cols=column_count)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.style = "Table Grid"

    header = table.cell(0, 0).merge(table.cell(0, column_count - 1))
    shade(header, accent)
    borders(header, accent)
    text(header, title.upper(), color=accent, size=7.2, white=True)
    table.rows[0].height = Cm(0.48)
    table.rows[0].height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST

    available = 17.9
    arrow_width = 0.38 if arrows else 0
    step_width = (available - arrow_width * (len(steps) - 1)) / len(steps)
    for index, (heading, detail) in enumerate(steps):
        column = index * 2 if arrows else index
        cell = table.cell(1, column)
        cell.width = Cm(step_width)
        shade(cell, pale)
        borders(cell, accent)
        text(cell, heading, detail, color=accent, size=6.4)
        if arrows and index < len(steps) - 1:
            arrow_cell = table.cell(1, column + 1)
            arrow_cell.width = Cm(arrow_width)
            shade(arrow_cell, WHITE)
            borders(arrow_cell, WHITE, size="0")
            text(arrow_cell, "→", color=accent, size=10)
    table.rows[1].height = Cm(0.9)
    table.rows[1].height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST

    if footer:
        footer_cell = table.cell(2, 0).merge(table.cell(2, column_count - 1))
        shade(footer_cell, pale)
        borders(footer_cell, accent)
        text(footer_cell, footer, color=accent, size=6.1)
        table.rows[2].height = Cm(0.42)
        table.rows[2].height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST

    move_after(table, anchor)
    return table


def enhance_agent_table(table) -> None:
    accent, pale = COLORS["agentic"]
    steps = [
        ("SAFETY", "Agent"),
        ("TRIAGE", "Agent"),
        ("KNOWLEDGE", "Agent"),
        ("RESOLUTION", "Agent"),
        ("QUALITY", "Agent"),
        ("HUMAN", "Review"),
    ]
    step_row = table.rows[0]
    for cell, (heading, detail) in zip(step_row.cells, steps):
        shade(cell, pale); borders(cell, accent)
        text(cell, heading, detail, color=accent, size=6.4)
    step_row.height = Cm(0.92); step_row.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST


def style_orchestrator_paragraph(paragraph) -> None:
    accent, pale = COLORS["agentic"]
    paragraph.text = "ORCHESTRATOR — controls handoffs, applies rules and stops or escalates when required"
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(1)
    paragraph.paragraph_format.space_after = Pt(1)
    run = paragraph.runs[0]
    run.bold = True
    run.font.name = "Aptos"
    run.font.size = Pt(6.2)
    run.font.color.rgb = RGBColor.from_string(accent)
    properties = paragraph._p.get_or_add_pPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), pale)
    properties.append(shading)


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    document = Document(SOURCE)
    if len(document.paragraphs) != 87 or len(document.tables) != 20:
        raise RuntimeError("Unexpected v7 structure; refusing to modify the report.")

    update_local_llm_text(document)
    original_paragraphs = [paragraph.text for paragraph in document.paragraphs]
    original_table_text = [table.cell(0, 0).text for table in document.tables]

    business, business_pale = COLORS["business"]
    schema(
        document, document.tables[1], "Business processes impacted",
        [
            ("EMPLOYEE REQUEST", "Need described"),
            ("TRIAGE & CLASSIFICATION", "Context completed"),
            ("ROUTING", "Right team"),
            ("RESOLUTION", "Answer & follow-up"),
            ("KNOWLEDGE REUSE", "Verified learning"),
        ], business, business_pale,
    )
    remove_paragraph(document.paragraphs[3])

    agent_table = next(table for table in document.tables if table.cell(0, 0).text == "SAFETY")
    enhance_agent_table(agent_table)
    # Reuse the original spacer as the orchestration-control line.
    empty_after_agent = next(p for p in document.paragraphs if not p.text and p._p.getprevious() is agent_table._tbl)
    style_orchestrator_paragraph(empty_after_agent)

    llm, llm_pale = COLORS["llm"]
    schema(
        document, document.tables[10], "LLM components",
        [
            ("MODEL", "Qwen 2.5 · Ollama"),
            ("ROLE PROMPTS", "Triage & Resolution"),
            ("CONSTRAINED FUNCTIONS", "Schema-bound outputs"),
            ("REQUEST CONTEXT", "Short-term only"),
        ], llm, llm_pale,
    )

    data, data_pale = COLORS["data"]
    data_anchor = next(p for p in document.paragraphs if p.text.startswith("In operation, authorised sources"))
    schema(
        document, data_anchor, "Data flow",
        [
            ("COMPANY SOURCES", "Documents, systems, verified cases"),
            ("INGESTION & APPROVAL", "Owner, date, permissions"),
            ("STORAGE & INDEX", "SQLite + knowledge index"),
            ("RETRIEVAL & ACCESS", "Permission-aware RAG"),
        ], data, data_pale,
    )

    governance, governance_pale = COLORS["governance"]
    governance_anchor = next(p for p in document.paragraphs if p.text == "Risk-to-control design")
    schema(
        document, governance_anchor, "Key controls",
        [
            ("SECURITY", "Data protection"),
            ("COMPLIANCE", "Policies & regulations"),
            ("RISK MANAGEMENT", "Unsafe content & bias"),
            ("GUARDRAILS & POLICIES", "Taxonomy, access, usage"),
        ], governance, governance_pale, arrows=False,
    )

    operations, operations_pale = COLORS["operations"]
    operations_anchor = next(p for p in document.paragraphs if p.text == "Business and service measures")
    schema(
        document, operations_anchor, "Observability & improvement loop",
        [
            ("COLLECT METRICS", "Value, quality, safety"),
            ("MONITOR & ANALYSE", "Trends and exceptions"),
            ("ALERT & RESPOND", "Owner-led action"),
            ("IMPROVE & OPTIMISE", "Test, approve, release"),
        ], operations, operations_pale,
        footer="CONTINUOUS FEEDBACK LOOP — measured outcomes inform the next controlled improvement",
    )

    document.core_properties.title = "AegisDesk AI Architecture — Five-Page Report with Local LLM"
    document.core_properties.subject = "Business, agentic, LLM, data, governance and operations schemas"
    document.save(OUTPUT)

    verification = Document(OUTPUT)
    remaining_paragraphs = [paragraph.text for paragraph in verification.paragraphs if paragraph.text]
    if not all(text in remaining_paragraphs for text in original_paragraphs if text):
        raise RuntimeError("Existing report text changed unexpectedly.")
    if not all(text in [table.cell(0, 0).text for table in verification.tables] for text in original_table_text if text and text != "SAFETY"):
        raise RuntimeError("An existing report table changed unexpectedly.")

    print(f"Generated: {OUTPUT}")
    print(f"Paragraphs: {len(verification.paragraphs)}; tables: {len(verification.tables)}")
    print("Added schemas: Business, Agentic, LLM, Data, Governance, Operations")


if __name__ == "__main__":
    main()

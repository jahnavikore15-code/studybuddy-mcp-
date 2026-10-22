"""Local fallback helpers. Bedrock can be added later without blocking the demo."""

import re
from datetime import date, timedelta

def make_quiz(notes: list[dict], num_questions: int = 5) -> str:
    if not notes:
        return "No notes found. Add notes for this topic first."
    facts = []
    for note in notes:
        text = note.get("text", "")
        # Split on periods, exclamation marks, question marks, or newlines
        parts = re.split(r'[\r\n.!?]+', text)
        for part in parts:
            part = part.strip()
            # Strip leading list markers such as -, *, •, 1., 1), (a)
            part = re.sub(r'^[\s*\-•\d+.)\]]+', '', part).strip()
            if len(part.split()) >= 3:
                facts.append(part)
    facts = list(dict.fromkeys(facts))
    if not facts:
        return "Add notes with complete sentences or clear points to generate practice questions."
    questions = []
    for i, fact in enumerate(facts[:num_questions], start=1):
        clean_fact = fact.rstrip(".")
        questions.append(f"{i}. Explain this statement in your own words: {clean_fact}.")
    return "Practice Quiz\n\n" + "\n\n".join(questions) + (
        "\n\nNote: These are practice prompts generated from your saved notes, "
        "not AI-generated questions."
    )

def make_plan(exam_date: str, topics: list[str]) -> str:
    try:
        exam_day = date.fromisoformat(str(exam_date).strip())
    except (ValueError, AttributeError):
        return "Invalid date. Use YYYY-MM-DD."
    today = date.today()
    if exam_day < today:
        return "The exam date is in the past. Please enter a future date."
    days = (exam_day - today).days + 1
    if days > 180:
        return "Exam date is more than 180 days away. Revision plans work best within 180 days."
    topics = list(dict.fromkeys(t.strip() for t in topics if t.strip()))
    if not topics:
        return "Please provide at least one topic."
    output = [f"Revision Plan - Exam date: {exam_day.isoformat()}", ""]
    for i in range(days):
        day = today + timedelta(days=i)
        topic = topics[i % len(topics)]
        task = "Quick revision and review key points." if day == exam_day else (
            f"Study {topic}, revise your notes, and practise questions."
        )
        output.append(f"{day.isoformat()} - {task}")
    return "\n".join(output)

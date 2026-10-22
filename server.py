from mcp.server.fastmcp import FastMCP
import db
import llm

mcp = FastMCP("StudyBuddy")

@mcp.tool()
def add_note(topic: str, text: str) -> str:
    """Save study notes under a subject or topic."""
    try:
        note_id = db.save_note(topic, text)
        return f"Successfully saved note #{note_id} under '{topic.strip()}'."
    except ValueError as exc:
        return f"Error: {exc}"

@mcp.tool()
def get_study_notes(topic: str) -> str:
    """Retrieve all saved notes for a specific topic."""
    notes = db.get_notes(topic)
    if not notes:
        return f"No notes found for '{topic}'. Add a note first."
    return "\n".join(
        [f"Study notes for {topic}:"] +
        [f"\nNote #{n['id']}: {n['text']}" for n in notes]
    )

@mcp.tool()
def list_study_topics() -> str:
    """List all subjects that have saved notes."""
    topics = db.list_topics()
    return "Available topics:\n" + "\n".join(f"- {t}" for t in topics) if topics else (
        "No study topics yet. Add your first note!"
    )

@mcp.tool()
def quiz_me(topic: str, num_questions: int = 5) -> str:
    """Create practice questions from saved notes for a topic."""
    if not 1 <= num_questions <= 10:
        return "Please request between 1 and 10 questions."
    return llm.make_quiz(db.get_notes(topic), num_questions)

@mcp.tool()
def revision_plan(exam_date: str, topics: list[str]) -> str:
    """Create a daily revision schedule through the exam date (YYYY-MM-DD)."""
    return llm.make_plan(exam_date, topics)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")

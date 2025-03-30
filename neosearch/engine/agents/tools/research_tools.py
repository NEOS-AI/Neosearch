from llama_index.core.workflow import Context


async def record_notes(ctx: Context, notes: str, notes_title: str) -> str:
    """Useful for recording notes on a given topic. Your input should be notes with a title to save the notes under."""
    current_state = await ctx.get("state")
    if "research_notes" not in current_state:
        current_state["research_notes"] = {}
    current_state["research_notes"][notes_title] = notes
    await ctx.set("state", current_state)
    return "Notes recorded."


async def write_report(ctx: Context, report_content: str) -> str:
    """Useful for writing a report on a given topic. Your input should be a markdown formatted report."""
    current_state = await ctx.get("state")
    current_state["report_content"] = report_content
    await ctx.set("state", current_state)
    return "Report written."


async def review_report(ctx: Context, review: str) -> str:
    """Useful for reviewing a report and providing feedback. Your input should be a review of the report."""
    current_state = await ctx.get("state")
    current_state["review"] = review
    await ctx.set("state", current_state)
    return "Report reviewed."


async def save_generate_questions(ctx: Context, questions: list[str]):
    """Useful for generating questions based on a given context. Your input should be a list of questions (comprehensive web search, broad coverage)."""
    current_state = await ctx.get("state")
    current_state["questions"] = questions
    num_of_questions = len(questions)
    await ctx.set("state", current_state)
    return f"Question generated (number of generated questions: {num_of_questions})."

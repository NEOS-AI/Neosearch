
DEEP_RESEARCH_GENERATE_QUESTIONS = """
Generate 5-6 specific questions about the topic to help guide the research agent to research about the topic: {topic} and this is the domain: {domain}, so don't ask too complex probing questions, keep them relatively simple. Focus on:
Mostly make these yes or no questions.
Do not ask the user for information, you are supposed to help him/her with the research, you can't ask questions about the topic itself, 
you can ask the user about what he wants to know about the topic and the domain.
Format your response as a numbered list, with exactly one question per line.
Example format:
1. [First question]
2. [Second question]
"""

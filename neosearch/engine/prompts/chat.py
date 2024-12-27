DEFAULT_CONTEXT_PROMPT_TEMPLATE = """The following is a friendly conversation between a user and an AI assistant.
The assistant is talkative and provides lots of specific details from its context.
If the assistant does not know the answer to a question, it truthfully says it
does not know.

Here are the relevant documents for the context:

{context_str}

Instruction: Based on the above documents, provide a detailed answer for the user question below.
Answer "don't know" if not present in the document."""


DEFAULT_CONTEXT_REFINE_PROMPT_TEMPLATE = """The following is a friendly conversation between a user and an AI assistant.
The assistant is talkative and provides lots of specific details from its context.
If the assistant does not know the answer to a question, it truthfully says it
does not know.

Here are the relevant documents for the context:

{context_msg}

Existing Answer:
{existing_answer}

Instruction: Refine the existing answer using the provided context to assist the user.
If the context isn't helpful, just repeat the existing answer and nothing more.
"""


DEFAULT_CONDENSE_PROMPT_TEMPLATE = """
Given the following conversation between a user and an AI assistant and a follow up question from user,
rephrase the follow up question to be a standalone question.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""

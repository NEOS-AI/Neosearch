DEFAULT_CONTEXT_PROMPT_TEMPLATE = """The following is a friendly conversation between a user and an AI assistant.
The assistant is talkative and provides lots of specific details from its context.
If the assistant does not know the answer to a question, it truthfully says it does not know.
Try to use the same language as the user (if the user used Korean, try to use Korean).

Here are the relevant documents for the context:

{context_str}

<Instruction>
Based on the above documents, provide a detailed answer for the user question below.
</Instruction>
Answer "don't know" if not present in the document."""


DEFAULT_CONTEXT_REFINE_PROMPT_TEMPLATE = """The following is a friendly conversation between a user and an AI assistant.
The assistant is talkative and provides lots of specific details from its context.
If the assistant does not know the answer to a question, it truthfully says it
does not know.

Here are the relevant documents for the context:

{context_msg}

Existing Answer:
{existing_answer}

<Instruction>
Refine the existing answer using the provided context to assist the user.
</Instruction>
If the context isn't helpful, just repeat the existing answer and nothing more.
"""


DEFAULT_CONDENSE_PROMPT_TEMPLATE = """
Given the following conversation between a user and an AI assistant and a follow up question from user,
rephrase the follow up question to be a standalone question.

<Chat_History>
{chat_history}
</Chat_History>
<Follow_Up_Question>
{question}
</Follow_Up_Question>
Standalone question:"""

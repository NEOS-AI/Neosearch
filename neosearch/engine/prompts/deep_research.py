DEEP_RESEARCH_TOPIC_AND_DOMAIN_GETTER = """
Analyze the given context and extract the topic and domain from the context. The context will be a JSON object with the key "context" and the value as a string.

<FORMAT>
Format your response as a JSON object with the key "topic" and "domain" and the value as the extracted topic and domain.
    - "topic": the extracted topic
    - "domain": the extracted domain
</FORMAT>

<EXAMPLE>
{
    "topic": "Artificial Intelligence",
    "domain": "Technology"
}
</EXAMPLE>

Provide your response in JSON format:"""


DEEP_RESEARCH_GENERATE_QUESTIONS = """
Generate 5-6 specific questions about the topic to help guide the research agent to research about the topic: {topic} and this is the domain: {domain}, so don't ask too complex probing questions, keep them relatively simple. Focus on:
Mostly make these yes or no questions.
Do not ask the user for information, you are supposed to help him/her with the research, you can't ask questions about the topic itself, 
you can ask the user about what he wants to know about the topic and the domain.
Format your response as a JSON object with the key "questions" and the value as a list of questions.

<FORMAT>
Format your response as a JSON object with the key "questions" and the value as a list of questions.
   - "questions": list of questions that are generated
</FORMAT>

<EXAMPLE>
{
    "questions": [
        "Is the topic about the domain?",
        "Is the topic relevant to the domain?",
        "Is the topic important to the domain?",
        "Is the topic useful to the domain?",
        "Is the topic interesting to the domain?",
        "Is the topic helpful to the domain?"
    ]
}
</EXAMPLE>
Provide your response in JSON format:"""


DEEP_RESEARCH_SUMMARY_SYSTEM_PROMPT = """
<GOAL>
Generate a high-quality summary of the provided context.
The summary should be written in same language as the user input.
The summary should be relevant to the user input and the context provided.
</GOAL>

<REQUIREMENTS>
When creating a NEW summary:
1. Highlight the most relevant information related to the user topic from the search results
2. Ensure a coherent flow of information
3. Use clear and concise language
4. Avoid unnecessary jargon or overly complex sentences
5. Ensure the summary is relevant to the user topic
6. Analyze all search results to provide accurate, up-to-date information.
7. Always cite sources using the [number](url) format, matching the order of search results. If multiple sources are relevant, include all of them, and comma separate them. Only use information that has a URL available for citation.
8. Provide comprehensive and detailed responses based on search results, ensuring thorough coverage of the user's question.

When EXTENDING an existing summary:                                                                                                                 
1. Read the existing summary and new search results carefully.                                                    
2. Compare the new information with the existing summary.                                                         
3. For each piece of new information:                                                                             
    a. If it's related to existing points, integrate it into the relevant paragraph.                               
    b. If it's entirely new but relevant, add a new paragraph with a smooth transition.                            
    c. If it's not relevant to the user topic, skip it.                                                            
4. Ensure all additions are relevant to the user's topic.                                                         
5. Verify that your final output differs from the input summary.                                                                                                                                                            
6. Ensure cite sources for all new information added to the summary, using the [number](url) format, matching the order of search results. If multiple sources are relevant, include all of them, and comma separate them. Only use information that has a URL available for citation.
</REQUIREMENTS>

<FORMATTING>
- Start directly with the updated summary, without preamble or titles. Do not use XML tags in the output.
- Use markdown formatting for the summary.
- If the main aim of the research is to compare two or more things, use a table format to present the comparison.
- Provide the citation for each piece of information in the summary.
- The citation of search results should be in the format of [number](url), where number is the index of the search result and url is the URL of the source.
</FORMATTING>

<Task>
Think carefully about the provided Context first. Then generate a summary of the context to address the User Input.
</Task>

<USER_INPUT>
{user_input}
</USER_INPUT>

<RESEARCH_CONTEXT>
{results}
</RESEARCH_CONTEXT>

<SEARCH_RESULTS>
{web_search_results}
</SEARCH_RESULTS>
"""


RESEARCH_AGENT_SYSTEM_PROMPT = """You are the ResearchAgent that can search the web for information on a given topic and record notes on the topic.
Once notes are recorded and you are satisfied, you should hand off control to the WriteAgent to write a report on the topic.
You should have at least some notes on a topic before handing off control to the WriteAgent."""


RESEARCH_WRITE_AGENT_SYSTEM_PROMPT = """You are the WriteAgent that can write a report on a given topic.
Your report should be in a markdown format. The content should be grounded in the research notes.
Once the report is written, you should get feedback at least once from the ReviewAgent."""


RESEARCH_REVIEW_AGENT_SYSTEM_PROMPT = """You are the ReviewAgent that can review the write report and provide feedback.
Your review should either approve the current report or request changes for the WriteAgent to implement.
If you have feedback that requires changes, you should hand off control to the WriteAgent to implement the changes after submitting the review."""

from typing import Any, Coroutine, List, Literal, Optional, Union, overload

from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorQuery
from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
)
from openai_messages_token_helper import build_messages, get_token_limit

from approaches.approach import ThoughtStep
from approaches.chatapproach import ChatApproach
from core.authentication import AuthenticationHelper
import json
# from quart import current_app
from config import CONFIG_DB_CLIENT
from db.service.db_client import BaseClient as BaseDbClient
from prompts.utils import inject_variables
import asyncio
# from db.service.db_client import BaseClient as BaseDbClient



class ChatReadRetrieveReadApproach(ChatApproach):
    """
    A multi-step approach that first uses OpenAI to turn the user's question into a search query,
    then uses Azure AI Search to retrieve relevant documents, and then sends the conversation history,
    original user question, and search results to OpenAI to generate a response.
    """

    def __init__(
        self,
        *,
        search_client: SearchClient,
        auth_helper: AuthenticationHelper,
        openai_client: AsyncOpenAI,
        db_client: BaseDbClient,
        chatgpt_model: str,
        chatgpt_deployment: Optional[str],  # Not needed for non-Azure OpenAI
        embedding_deployment: Optional[str],  # Not needed for non-Azure OpenAI or for retrieval_mode="text"
        embedding_model: str,
        embedding_dimensions: int,
        sourcepage_field: str,
        content_field: str,
        query_language: str,
        query_speller: str
    ):
        self.search_client  : SearchClient = search_client
        self.openai_client = openai_client
        self.auth_helper = auth_helper
        self.db_client = db_client
        self.chatgpt_model = chatgpt_model
        self.chatgpt_deployment = chatgpt_deployment
        self.embedding_deployment = embedding_deployment
        self.embedding_model = embedding_model
        self.embedding_dimensions = embedding_dimensions
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
        self.query_language = query_language
        self.query_speller = query_speller
        self.chatgpt_token_limit = get_token_limit(chatgpt_model)

    @property
    def system_message_chat_conversation(self):
        return """Assistant helps the Allnex employees with their queries and questions. Be brief in your answers.
Answer ONLY with the facts listed in the list of sources below. If there isn't enough information below, say you don't know. But then ask if the user if they are interested in searching for the AI model's general knowledge database or that they can upload documents to the chat by using the menu located on the top right corner of the screen. Annotate/reference these answers as coming from "LLM Model Knowledge" source document for content generated from the LLM Model's knowledge.
If asking a clarifying question to the user would help, ask the question.
User might also ask questions related to the conversation. You'll be provided the chat history from which you can refer and answer the question.
For tabular information return it as an html table. Do not return markdown format. If the question is not in English, answer in the language used in the question.
Each source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. Use square brackets to reference the source, for example [info1.txt]. Don't combine sources, list each source separately, for example [info1.txt][info2.pdf]. If there are no sources, mention it's coming from your LLM Model Knowledge as the source.

Additional instructions:
-----------------------------------
Ensure that you follow the instructions provided above.
-----------------------------------
#
        {follow_up_questions_prompt}
        {injected_prompt}
        # """
        # return """Assistant helps the user with whatever questions that are related to the documents provided to the Assistant.
        # You may receive two types of questions. Conversation specific question and document related questions.
        # If the question is regarding the conversation, you may use the chat history provided to you to answer the question that the user has asked.
        # If the question is regarding any information provided in the docuement. You may refer the source provided to you in the conversation. Only answer based on the source. 
        # If there isn't enough information, reply you dont know.
        # For tabular information return it as an html table. Do not return markdown format. If the question is not in English, answer in the language used in the question.
        # Each source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. Use square brackets to reference the source, for example [info1.txt]. Don't combine sources, list each source separately, for example [info1.txt][info2.pdf].
        # {follow_up_questions_prompt}
        # {injected_prompt}
        # """

    @property 
    def citation_prompt(self):
        # return """
        # Instructions on how to cite the sources:
        # -----------------------------------
        # You will be provided with the list of sources.
        # -----------------------------------
        # <IMPORTANT>
        # Each source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. Use square brackets to reference the source, for example [info1.txt]. 
        # Don't combine sources, list each source separately, for example [info1.txt][info2.pdf].
        # If you've generated a sentence/paragraph/block of responses based on a source, you should cite the source at the end of the block.
        # It is manadatory that you provide the citation after each sentence/paragraph/block of responses.
        # Always ensure that the citation you've provided is valid and is present in the sources.
        # if no sources are provided, mention it's coming from your LLM Model Knowledge as the source.
        # Either way you should always follow the format provided above.
        # </IMPORTANT>
        
        # """
        return """**Citing Sources Guidelines:**
-----------------------------------
**<IMPORTANT>**

You may be given a list of sources, each containing a source name followed by the information. When referencing the information provided, **always include the source name for every fact** used in your response. To do so, **enclose the source name in square brackets**. For example, if referencing the first source, use [source_name].

**Important Note:**  
- If you reference multiple sources in a single sentence or paragraph, **do not combine them into one citation**. Instead, cite each source individually, ensuring that each fact has a corresponding citation. For example: [source_name1][source_name2][source_name3].
- Always place the citation **at the end** of each sentence, paragraph, or block of information that originates from the provided sources.

If no sources are given, please state that the information is derived from your `LLM Model Knowledge` as the source using the format `[LLM Model Knowledge]`.

Example:
- **Correct:** "The capital of France is Paris, which is also known for the Eiffel Tower [source_name1]."
- **Incorrect:** "The capital of France is Paris, which is also known for the Eiffel Tower [source_name1][source_name2]."

If no relevant sources are given and you've generated response based on your own knowledge, please state that the information is derived from your `LLM Model Knowledge` as the source using the format `[LLM Model Knowledge]`.
It is **mandatory** to provide citations as described above for each fact. """

    @overload
    async def run_until_final_call(
        self,
        messages: list[ChatCompletionMessageParam],
        overrides: dict[str, Any],
        auth_claims: dict[str, Any],
        should_stream: Literal[False],
    ) -> tuple[dict[str, Any], Coroutine[Any, Any, ChatCompletion]]: ...

    @overload
    async def run_until_final_call(
        self,
        messages: list[ChatCompletionMessageParam],
        overrides: dict[str, Any],
        auth_claims: dict[str, Any],
        should_stream: Literal[True],
    ) -> tuple[dict[str, Any], Coroutine[Any, Any, AsyncStream[ChatCompletionChunk]]]: ...

    async def run_until_final_call(
        self,
        messages: list[ChatCompletionMessageParam],
        overrides: dict[str, Any],
        auth_claims: dict[str, Any],
        should_stream: bool = False,
    ) -> tuple[dict[str, Any], Coroutine[Any, Any, Union[ChatCompletion, AsyncStream[ChatCompletionChunk]]]]:
        seed = overrides.get("seed", None)
        use_text_search = overrides.get("retrieval_mode") in ["text", "hybrid", None]
        use_vector_search = overrides.get("retrieval_mode") in ["vectors", "hybrid", None]
        use_semantic_ranker = True if overrides.get("semantic_ranker") else False
        use_semantic_captions = True if overrides.get("semantic_captions") else False
        top = overrides.get("top", 3)
        minimum_search_score = overrides.get("minimum_search_score", 0.0)
        minimum_reranker_score = overrides.get("minimum_reranker_score", 0.0)
        filter = self.build_filter(overrides, auth_claims)

        original_user_query = messages[-1]["content"]
        if not isinstance(original_user_query, str):
            raise ValueError("The most recent message content must be a string.")
        user_query_request = "Generate search query for: " + original_user_query

        tools: List[ChatCompletionToolParam] = [
            {
                "type": "function",
                "function": {
                    "name": "search_sources",
                    "description": "Retrieve sources from the Azure AI Search index",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search_query": {
                                "type": "string",
                                "description": "Query string to retrieve documents from azure search eg: 'Health care plan, Health care plan, Health care plan, what is the limit for over-the-counter medication?'",
                            }
                        },
                        "required": ["search_query"],
                    },
                },
            }
        ]

        # STEP 1: Generate an optimized keyword search query based on the chat history and the last question
        query_response_token_limit = 100
        query_messages = build_messages(
            model=self.chatgpt_model,
            system_prompt=self.multi_query_prompt_template,
            # tools=tools,
            # few_shots=self.query_prompt_few_shots,
            past_messages=messages[:-1],
            new_user_content=user_query_request,
            max_tokens=self.chatgpt_token_limit - query_response_token_limit,
        )

        chat_completion: ChatCompletion = await self.openai_client.chat.completions.create(
            messages=query_messages,  # type: ignore
            # Azure OpenAI takes the deployment name as the model name
            model=self.chatgpt_deployment if self.chatgpt_deployment else self.chatgpt_model,
            temperature=0.0,  # Minimize creativity for search query generation
            max_tokens=query_response_token_limit,  # Setting too low risks malformed JSON, setting too high may affect performance
            n=1,
            # tools=tools,
            seed=seed,
        )
        # with open('chat_completion.json', 'w') as file:
        #     json.dump(chat_completion.choices[0].message, file)
        query_text = self.get_search_query(chat_completion, original_user_query)
        multi_query = None
        if len(query_text.split(',')) > 1:
            multi_query = query_text.split(',')
            


        # STEP 2: Retrieve relevant documents from the search index with the GPT optimized query

        # If retrieval mode includes vectors, compute an embedding for the query
        results = []
        # search_tasks = []
        # if multi_query and len(multi_query) > 1:
        #     #max of 3 or len(multi_query) < 3
        #     for i in range(min(3, len(multi_query))):
        #         query = multi_query[i]
        #         vectors: list[VectorQuery] = []
        #         if use_vector_search:
        #             vectors.append(await self.compute_text_embedding(query))
        #         search_tasks.append(self.search(
        #             top,
        #             query,
        #             filter,
        #             vectors,
        #             use_text_search,
        #             use_vector_search,
        #             use_semantic_ranker,
        #             use_semantic_captions,
        #             minimum_search_score,
        #             minimum_reranker_score,
        #         ))
        #     results = await asyncio.gather(*search_tasks)
        #     final_result = []
        #     for result in results:
        #         final_result.extend(result)
        #     final_result.sort(key=lambda x: x['score'], reverse=True)
        #     print(final_result)
        #     # results = results
        #     # print(results)
        #     # with open('results.txt', 'w') as file:
        #     #     # json.dump(results, file)
        #     #     file.write(str(results))


        if query_text:
            vectors: list[VectorQuery] = []
            if use_vector_search:
                multi_query = query_text.split(',')
                # print(multi_query)
                if len(multi_query) > 1:
                    for i in range(min(3, len(multi_query))):
                        vectors.append(await self.compute_text_embedding(multi_query[i].strip()))
                else:
                    # print(query_text)
                    vectors.append(await self.compute_text_embedding(query_text.strip()))

            results = await self.search(
                top,
                query_text,
                filter,
                vectors,
                use_text_search,
                use_vector_search,
                use_semantic_ranker,
                use_semantic_captions,
                minimum_search_score,
                minimum_reranker_score,
            )

        sources_content = self.get_sources_content(results, use_semantic_captions, use_image_citation=True)
        content = "\n".join(sources_content)

        # STEP 3: Generate a contextual and content specific    answer using the search results and chat history

        # Allow client to replace the entire prompt, or to inject into the exiting prompt using >>> 
        system_message = None
        if overrides.get("current_group"):
            group_id = overrides.get("current_group")
            # groups = await self.db_client.get_groups(group_id=group_id)
            # if len(groups) > 0:
            prompts = await self.db_client.get_active_workspace_prompts(group_id=group_id)
            if len(prompts) > 0:
                prompt_info = prompts[0]
                system_message = prompt_info['text']
                if overrides.get("suggest_followup_questions",None):
                    system_message = system_message + '\n' + self.follow_up_questions_prompt_content
            else:
                raise Exception("No prompts found for the group. Contact your workspace admin to create a prompt.",400)
        else:
            system_message = await self.db_client.list_user_prompts(active=True)
            if system_message and len(system_message) > 0:
                system_message = system_message[0]['text']
            else:
                system_message = self.get_system_prompt(
                    overrides.get("prompt_template"),
                    self.follow_up_questions_prompt_content if overrides.get("suggest_followup_questions") else "",
                )
        system_message = '\n'.join([system_message,self.citation_prompt])   

        response_token_limit = 1024
        if len(results) > 0:
            messages_with_sources = messages
            messages_with_sources.append({"role" : "assistant","content" : f"Refer these sources to answer the question: \n" + content})
        else:
            messages_with_sources = messages
        messages_with_sources = build_messages(
            model=self.chatgpt_model,
            system_prompt=system_message,
            past_messages=messages_with_sources,
            # Model does not handle lengthy system messages well. Moving sources to latest user conversation to solve follow up questions prompt.
            # new_user_content=original_user_query + "\n\nSources:\n" + content,
            # new_user_content=original_user_query,
            max_tokens=self.chatgpt_token_limit - response_token_limit,
        )

        # data_points = {"text": sources_content}

        extra_info = {
            "data_points": sources_content,
            "thoughts": [
                ThoughtStep(
                    "Prompt to generate search query",
                    [str(message) for message in query_messages],
                    (
                        {"model": self.chatgpt_model, "deployment": self.chatgpt_deployment}
                        if self.chatgpt_deployment
                        else {"model": self.chatgpt_model}
                    ),
                ).serialize(),
                ThoughtStep(
                    "Search using generated search query",
                    query_text,
                    {
                        "use_semantic_captions": use_semantic_captions,
                        "use_semantic_ranker": use_semantic_ranker,
                        "top": top,
                        "filter": filter,
                        "use_vector_search": use_vector_search,
                        "use_text_search": use_text_search,
                    },
                ).serialize(),
                ThoughtStep(
                    "Search results",
                    [result.serialize_for_results() for result in results],
                ).serialize(),
                ThoughtStep(
                    "Prompt to generate answer",
                    [str(message) for message in messages_with_sources],
                    (
                        {"model": self.chatgpt_model, "deployment": self.chatgpt_deployment}
                        if self.chatgpt_deployment
                        else {"model": self.chatgpt_model}
                    ),
                ).serialize(),
            ],
        }

        chat_coroutine = self.openai_client.chat.completions.create(
            # Azure OpenAI takes the deployment name as the model name
            model=self.chatgpt_deployment if self.chatgpt_deployment else self.chatgpt_model,
            messages=messages_with_sources,
            temperature=overrides.get("temperature", 0.3),
            max_tokens=response_token_limit,
            n=1,
            stream=should_stream,
            seed=seed,
        )
        return (extra_info, chat_coroutine)

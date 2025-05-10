from openai import AsyncAzureOpenAI, AsyncOpenAI

async def generate_title(model_client : AsyncOpenAI,model_name : str, conversation_messages : list):
    title_prompt = "Summarize the conversation so far into a 4-word or less title. Do not use any quotation marks or punctuation. Do not include any other commentary or description."

    messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in conversation_messages
    ]
    messages.append({"role": "user", "content": title_prompt})

    try:
        response = await model_client.chat.completions.create(
            model=model_name, messages=messages, temperature=1, max_tokens=64
        )

        title = response.choices[0].message.content
        return title
    except Exception as e:
        return messages[-2]["content"]
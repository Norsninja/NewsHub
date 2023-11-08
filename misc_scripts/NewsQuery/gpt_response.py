import openai
import os

class GPTResponse:
    def __init__(self):
        self.api_key = openai.api_key = os.getenv('OPENAI_API_KEY')
        self.model = "gpt-4"
        self.messages = [
            {
                "role": "system",
                "content": "You are a knowledgeable AI who has read several articles related to the user's query. Your task is to provide a unified response to the query, making sure to consolidate all relevant information, and explain the changes over time. Determine and use the relevant info to the query or topic given by the user, based on the following article summaries to generate your response. Please ensure you don't refer to the articles by numbers but incorporate the information smoothly and coherently in your answer. Cite sources that best reflect the query by referring to the corresponding URL."
            }
        ]

    def get_response(self, query, doc_info_and_summary):
        self.messages.append({
            "role": "user",
            "content": query
        })
        self.messages[-1]["content"] += f"\n\nSummarized Information::\n{doc_info_and_summary}"
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            temperature=.2,
            max_tokens=600,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        self.messages.append({
            "role": "assistant",
            "content": response.choices[0].message['content']
        })
        return self.messages[-1]["content"]

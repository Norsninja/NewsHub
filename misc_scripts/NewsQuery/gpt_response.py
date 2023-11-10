import openai
import os
import json
import tiktoken

class GPTResponse:
    def __init__(self):
        self.api_key = openai.api_key = os.getenv('OPENAI_API_KEY')
        self.model = "gpt-4"
        self.history_file = 'misc_scripts/NewsQuery/conversation_history.json'
        self.messages = self.load_messages()
        self.encoding = tiktoken.encoding_for_model(self.model)
        print("GptResponse Called...")
    def count_tokens(self):
        """
        Counts the total number of tokens for all messages in the history.
        """
        total_tokens = 0
        for message in self.messages:
            content = message.get('content', '')
            total_tokens += len(self.encoding.encode(content))
        return total_tokens
    def load_messages(self):
        print("GptResponse load_messages Called...")
        if not os.path.exists(self.history_file):
            # Return the initial system message if no CSV exists
            return [
                {
                    "role": "system",
                    "content": "You are an advanced news analysis AI. Your task is to provide a unified response to the query, making sure to consolidate all relevant information, and explain the changes over time. Engage in a reflective process to define the '5 Ws' (Who, What, Where, When, Why) for the topic, with a special focus on the 'When'. Adjust the date range as necessary based on significant events or developments identified in this phase. Determine and use the relevant info to the query or topic given by the user, based on the following article summaries to generate your response. Please ensure you don't refer to the articles by numbers but incorporate the information smoothly and coherently in your answer. Cite sources that best reflect the query by referring to the corresponding URL. Note the dates of all the articles returned and try to establish any patterns"
                }
            ]
        with open(self.history_file, mode='r', encoding='utf-8') as file:
            return json.load(file)

    def save_messages(self):
        print("GptResponse save_messages Called...")
        with open(self.history_file, 'w', encoding='utf-8') as file:
            json.dump(self.messages, file, ensure_ascii=False, indent=4)

    def get_response(self, query, doc_info_and_summary):
        print("GptResponse get_response Called...")
        # Append user query to messages
        self.messages.append({
            "role": "user",
            "content": query
        })
        
        # Append summarized information only if it's provided
        if doc_info_and_summary:
            self.messages[-1]["content"] += f"\n\nSummarized Information:\n{doc_info_and_summary}"

        # Make the API call to OpenAI to get the response
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            temperature=.2,
            max_tokens=600,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        # Append the assistant's response to messages
        self.messages.append({
            "role": "assistant",
            "content": response.choices[0].message['content']
        })
        
        # Save the updated messages list to the history file
        self.save_messages()
        
        # Return the content of the assistant's response
        return self.messages[-1]["content"]

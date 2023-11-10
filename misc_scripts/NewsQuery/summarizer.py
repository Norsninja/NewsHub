from langchain import OpenAI, PromptTemplate
from langchain.chains.summarize import load_summarize_chain

class Summarizer:
    def __init__(self):
        self.llm = OpenAI(temperature=0)
        self.summarization_chain = load_summarize_chain(llm=self.llm, chain_type="map_reduce")
        print("Summarizer Called...")

    def summarize_documents(self, documents):
        return self.summarization_chain.run(documents)

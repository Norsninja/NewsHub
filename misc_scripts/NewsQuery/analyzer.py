from config import load_config
from data_handler import load_data, parse_data
from text_processor import TextProcessor
from document_retriever import DocumentRetriever
from summarizer import Summarizer
from gpt_response import GPTResponse
from pydantic import BaseModel

class NewsAnalyzer:
    def __init__(self):
        self.config_settings = load_config('modules/suite_config.ini')
        self.raw_data = load_data('cache/test_weekly_cache.pkl')
        self.documents = parse_data(self.raw_data)
        
        self.text_processor = TextProcessor()
        self.chunked_docs = self.text_processor.chunk_documents(self.documents)
        self.vectorstore = self.text_processor.vectorize_chunks(self.chunked_docs)
        
        self.document_retriever = DocumentRetriever(self.vectorstore)
        self.summarizer = Summarizer()
        self.gpt_response = GPTResponse()

    def analyze(self, query):
        relevant_documents = self.document_retriever.retrieve_documents(query)
        
        # Display the retrieved articles first
        print("Retrieved Articles:\n")
        for i, doc in enumerate(relevant_documents):
            print(f"Document {i+1}:")
            print(f"Headline: {doc.metadata['headline']}")
            print(f"Date and Time: {doc.metadata['date_time']}")
            print(f"Link: {doc.metadata['link']}")
            print(f"Content: {doc.page_content}")  # Use 'page_content' instead of 'text'
            print("\n-----------------\n")
        
        # Then, generate summaries
        summaries = self.summarizer.summarize_documents(relevant_documents)

        doc_info_and_summary = ""
        for i, doc in enumerate(relevant_documents):
            doc_info_and_summary += f"\nDocument {i+1}:\n"
            doc_info_and_summary += f"Headline: {doc.metadata['headline']}\n"
            doc_info_and_summary += f"Date and Time: {doc.metadata['date_time']}\n"
            doc_info_and_summary += f"Link: {doc.metadata['link']}\n"
            doc_info_and_summary += f"Summary: {summaries[i]}\n"
            doc_info_and_summary += "\n-----------------\n"

        return self.gpt_response.get_response(query, doc_info_and_summary)
    
    def get_relevant_documents(self, query):
        return self.document_retriever.retrieve_documents(query)


# if __name__ == "__main__":
#     analyzer = NewsAnalyzer()
#     query = input("Enter your query: ")
#     response = analyzer.analyze(query)
#     print(response)

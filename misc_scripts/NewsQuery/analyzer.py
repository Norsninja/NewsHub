from config import load_config
from data_handler import load_data, parse_data
from text_processor import TextProcessor
from document_retriever import DocumentRetriever
from gpt_response import GPTResponse
from pydantic import BaseModel
import threading

class NewsAnalyzer:
    def __init__(self):
        self.config_settings = load_config('modules/suite_config.ini')
        self.raw_data = None
        self.documents = None
        self.text_processor = None
        self.chunked_docs = None
        self.vectorstore = None
        self.document_retriever = None
        self.summarizer = None
        self.gpt_response = GPTResponse()
        self.lock = threading.Lock()

        # Start a thread to load and parse the data
        threading.Thread(target=self.load_and_parse_data).start()

    def load_and_parse_data(self):
        with self.lock:
            if self.raw_data is None:
                self.raw_data = load_data('cache/test_weekly_cache.pkl')
                self.documents = parse_data(self.raw_data)

    def process_text(self):
        if self.text_processor is None:
            self.text_processor = TextProcessor()
            self.chunked_docs = self.text_processor.chunk_documents(self.documents)
            self.vectorstore = self.text_processor.vectorize_chunks(self.chunked_docs)

    def get_relevant_documents(self, query):
        with self.lock:
            self.process_text()
            if self.document_retriever is None:
                self.document_retriever = DocumentRetriever(self.vectorstore)
            return self.document_retriever.retrieve_documents(query)
    def format_documents(self, documents):
        formatted_documents = ""
        for i, doc in enumerate(documents):
            formatted_documents += f"\nDocument {i+1}:\n"
            formatted_documents += f"Headline: {doc.metadata['headline']}\n"
            formatted_documents += f"Date and Time: {doc.metadata['date_time']}\n"
            formatted_documents += f"Link: {doc.metadata['link']}\n"
            formatted_documents += f"Content: {doc.page_content}\n"
            formatted_documents += "\n-----------------\n"
        return formatted_documents       
    def create_doc_info_and_summary(self, relevant_documents, summaries):
        doc_info_and_summary = ""
        for i, doc in enumerate(relevant_documents):
            doc_info_and_summary += f"\nDocument {i+1}:\n"
            doc_info_and_summary += f"Headline: {doc.metadata['headline']}\n"
            doc_info_and_summary += f"Date and Time: {doc.metadata['date_time']}\n"
            doc_info_and_summary += f"Link: {doc.metadata['link']}\n"
            doc_info_and_summary += f"Summary: {summaries[i]}\n"
            doc_info_and_summary += "\n-----------------\n"
        return doc_info_and_summary
    def analyze(self, query):
        relevant_documents = self.document_retriever.retrieve_documents(query)
        
        # Display the retrieved articles first
        print("Retrieved Articles:\n")
        print(self.format_documents(relevant_documents))
        
        # Then, generate summaries
        summaries = self.summarizer.summarize_documents(relevant_documents)

        doc_info_and_summary = self.create_doc_info_and_summary(relevant_documents, summaries)

        return self.gpt_response.get_response(query, doc_info_and_summary)
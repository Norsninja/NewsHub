from config import load_config
from data_handler import load_data, parse_data
from text_processor import TextProcessor
from document_retriever import DocumentRetriever
from gpt_response import GPTResponse
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
        # This method might need updating depending on how you use the text processor
        if self.text_processor is None:
            self.text_processor = TextProcessor()
            self.chunked_docs = self.text_processor.chunk_documents(self.documents)
            self.vectorstore = self.text_processor.vectorize_chunks(self.chunked_docs)

    def get_relevant_documents(self, query, num_articles=None):
        with self.lock:
            self.process_text()
            if self.document_retriever is None:
                self.document_retriever = DocumentRetriever(self.vectorstore)
            return self.document_retriever.retrieve_documents(query, num_articles)

    def format_documents(self, documents):
        formatted_documents = ""
        for i, doc in enumerate(documents):
            formatted_documents += f"\nDocument {i+1}:\n"
            formatted_documents += f"Headline: {doc.metadata['headline']}\n"
            formatted_documents += f"Category: {doc.metadata['category']}\n"  # Added field
            formatted_documents += f"Date and Time: {doc.metadata['date_time']}\n"
            formatted_documents += f"Source: {doc.metadata['source']}\n"  # Added field
            formatted_documents += f"Location: {doc.metadata['location']}\n"  # Added field
            formatted_documents += f"Coordinates: {doc.metadata['coordinates']}\n"  # Added field
            formatted_documents += f"Link: {doc.metadata['link']}\n"
            formatted_documents += f"Summary: {doc.metadata['summary']}\n"
            formatted_documents += "\n-----------------\n"
        return formatted_documents



    def analyze(self, query, num_articles):
        relevant_documents = self.get_relevant_documents(query, num_articles)
        
        # Display the retrieved articles first
        print("Retrieved Articles:\n")
        print(self.format_documents(relevant_documents))

        # Since summaries are already included in the metadata, we no longer generate them
        # Instead, we create a string from metadata for the GPT response
        doc_info_and_summary = self.format_documents(relevant_documents)

        return self.gpt_response.get_response(query, doc_info_and_summary)


import tkinter as tk
from tkinter import scrolledtext
from analyzer import NewsAnalyzer
import threading

class NewsAnalyzerGUI(tk.Tk):
    def __init__(self, analyzer):
        super().__init__()

        self.analyzer = analyzer

        self.title("News Analyzer")
        self.geometry("1024x768")

        # Query label
        self.query_label = tk.Label(self, text="Enter your query:")
        self.query_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Query entry
        self.query_entry = tk.Entry(self, width=120)
        self.query_entry.grid(row=0, column=1, padx=20, pady=20, sticky="w")

        # Analyze button
        self.analyze_button = tk.Button(self, text="Analyze", command=self.perform_analysis)
        self.analyze_button.grid(row=0, column=2, padx=20, pady=20)

        # Results text box
        self.results_text = scrolledtext.ScrolledText(self, width=120, height=15)
        self.results_text.grid(row=1, column=0, columnspan=3, padx=20, pady=20)
        self.results_text.insert(tk.END, "Retrieved Articles will be displayed here...")
        self.results_text.configure(state='disabled')

        # GPT response text box
        self.gpt_response_text = scrolledtext.ScrolledText(self, width=120, height=15)
        self.gpt_response_text.grid(row=2, column=0, columnspan=3, padx=20, pady=20)
        self.gpt_response_text.insert(tk.END, "GPT-4 response will be displayed here...")
        self.gpt_response_text.configure(state='disabled')


    def perform_analysis(self):
        query = self.query_entry.get()
        if not query.strip():
            return

        # Run the analysis in a separate thread to avoid blocking the main GUI
        threading.Thread(target=self.run_analysis, args=(query,)).start()

    def run_analysis(self, query):
        relevant_documents = self.analyzer.get_relevant_documents(query)
        # Capture the relevant documents
        relevant_docs_text = "Retrieved Articles:\n"
        for i, doc in enumerate(relevant_documents):
            relevant_docs_text += f"Document {i+1}:\n"
            relevant_docs_text += f"Headline: {doc.metadata['headline']}\n"
            relevant_docs_text += f"Date and Time: {doc.metadata['date_time']}\n"
            relevant_docs_text += f"Link: {doc.metadata['link']}\n"
            relevant_docs_text += f"Content: {doc.page_content}\n"
            relevant_docs_text += "\n-----------------\n"

        # Clear and insert the relevant documents into results_text
        self.results_text.configure(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, relevant_docs_text)
        self.results_text.configure(state='disabled')

        # Capture the GPT-4 response
        summaries = self.analyzer.summarizer.summarize_documents(relevant_documents)

        doc_info_and_summary = ""
        for i, doc in enumerate(relevant_documents):
            doc_info_and_summary += f"\nDocument {i+1}:\n"
            doc_info_and_summary += f"Headline: {doc.metadata['headline']}\n"
            doc_info_and_summary += f"Date and Time: {doc.metadata['date_time']}\n"
            doc_info_and_summary += f"Link: {doc.metadata['link']}\n"
            doc_info_and_summary += f"Summary: {summaries[i]}\n"
            doc_info_and_summary += "\n-----------------\n"
        gpt_response = self.analyzer.gpt_response.get_response(query, doc_info_and_summary)

        # Clear and insert the GPT-4 response into gpt_response_text
        self.gpt_response_text.configure(state='normal')
        self.gpt_response_text.delete(1.0, tk.END)
        self.gpt_response_text.insert(tk.END, gpt_response)
        self.gpt_response_text.configure(state='disabled')


if __name__ == "__main__":
    analyzer = NewsAnalyzer()
    app = NewsAnalyzerGUI(analyzer)
    app.mainloop()

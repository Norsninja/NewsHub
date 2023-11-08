import tkinter as tk
from tkinter import scrolledtext
from analyzer import NewsAnalyzer
from summarizer import Summarizer
import threading

class NewsAnalyzerGUI(tk.Tk):
    def __init__(self, analyzer):
        super().__init__()

        self.analyzer = analyzer

        self.title("News Analyzer")
        self.geometry("1024x768")
        # Loading label
        self.loading_label = tk.Label(self, text="Loading...")
        self.loading_label.grid(row=3, column=0, columnspan=3)
        self.loading_label.grid_remove()  # Hide the label initially
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
        # Follow-up question label
        self.followup_label = tk.Label(self, text="Enter your follow-up question:")
        self.followup_label.grid(row=3, column=0, padx=20, pady=20, sticky="w")

        # Follow-up question entry
        self.followup_entry = tk.Entry(self, width=120)
        self.followup_entry.grid(row=3, column=1, padx=20, pady=20, sticky="w")

        # Follow-up button
        self.followup_button = tk.Button(self, text="Ask Follow-up", command=self.perform_followup)
        self.followup_button.grid(row=3, column=2, padx=20, pady=20)

    def perform_analysis(self):
        query = self.query_entry.get()
        if not query.strip():
            return
        # Show the loading label
        self.loading_label.grid()
        # Run the analysis in a separate thread to avoid blocking the main GUI
        threading.Thread(target=self.run_analysis, args=(query,)).start()

    def run_analysis(self, query):
        # Show the loading label
        self.after(0, self.loading_label.grid)

        relevant_documents = self.analyzer.get_relevant_documents(query)

        # Hide the loading label
        self.after(0, self.loading_label.grid_remove)

        # Capture the relevant documents
        relevant_docs_text = "Retrieved Articles:\n"
        relevant_docs_text += self.analyzer.format_documents(relevant_documents)

        # Schedule the update of the results_text on the main thread
        self.after(0, self.update_results_text, relevant_docs_text)

        # Show the loading label
        self.after(0, self.loading_label.grid)

        if self.analyzer.summarizer is None:
            self.analyzer.summarizer = Summarizer()
        summaries = self.analyzer.summarizer.summarize_documents(relevant_documents)

        # Hide the loading label
        self.after(0, self.loading_label.grid_remove)

        doc_info_and_summary = self.analyzer.create_doc_info_and_summary(relevant_documents, summaries)

        # Show the loading label
        self.after(0, self.loading_label.grid)

        gpt_response = self.analyzer.gpt_response.get_response(query, doc_info_and_summary)

        # Hide the loading label
        self.after(0, self.loading_label.grid_remove)

        # Schedule the update of the gpt_response_text on the main thread
        self.after(0, self.update_gpt_response_text, gpt_response)
        
    def perform_followup(self):
        followup_query = self.followup_entry.get()
        if not followup_query.strip():
            return

        # Run the follow-up in a separate thread to avoid blocking the main GUI
        threading.Thread(target=self.run_followup, args=(followup_query,)).start()

    def run_followup(self, followup_query):
        # Capture the GPT-4 response
        gpt_response = self.analyzer.gpt_response.get_response(followup_query, "")

        # Schedule the update of the gpt_response_text on the main thread
        self.after(0, self.update_gpt_response_text, gpt_response)

    def update_results_text(self, text):
        self.results_text.configure(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, text)
        self.results_text.configure(state='disabled')

    def update_gpt_response_text(self, text):
        self.gpt_response_text.configure(state='normal')
        self.gpt_response_text.delete(1.0, tk.END)
        self.gpt_response_text.insert(tk.END, text)
        self.gpt_response_text.configure(state='disabled')


if __name__ == "__main__":
    analyzer = NewsAnalyzer()
    app = NewsAnalyzerGUI(analyzer)
    app.mainloop()

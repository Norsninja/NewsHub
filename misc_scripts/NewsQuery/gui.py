import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter import messagebox
from analyzer import NewsAnalyzer
import threading
import json

class NewsAnalyzerGUI(tk.Tk):
    def __init__(self, analyzer):
        super().__init__()

        self.analyzer = analyzer

        self.title("News Analyzer")
        self.geometry("1920x1080")
        # Loading label
        self.loading_label = tk.Label(self, text="Loading...")
        self.loading_label.grid(row=6, column=0, columnspan=3)
        self.loading_label.grid_remove()  # Hide the label initially
        # Query label
        self.query_label = tk.Label(self, text="Enter your query:")
        self.query_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        # Query entry
        self.query_entry = tk.Entry(self, width=120)
        self.query_entry.grid(row=0, column=1, padx=20, pady=20, sticky="w")
        self.article_count_var = tk.IntVar(value=15) 
        # Article count label moved to row 1
        self.article_count_label = tk.Label(self, text="Number of articles to retrieve:")
        self.article_count_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        # Article count spinbox moved to row 1
        self.article_count_spinbox = tk.Spinbox(self, from_=1, to=100, textvariable=self.article_count_var, width=5)
        self.article_count_spinbox.grid(row=1, column=1, padx=20, pady=5, sticky="w")
        
        # Analyze button moved to row 1, column 2
        self.analyze_button = tk.Button(self, text="Analyze", command=self.perform_analysis)
        self.analyze_button.grid(row=1, column=2, padx=20, pady=20)

        # Results text box moved to row 2
        self.results_text = scrolledtext.ScrolledText(self, width=200, height=20)
        self.results_text.grid(row=2, column=0, columnspan=3, padx=20, pady=20)
        self.results_text.insert(tk.END, "Retrieved Articles will be displayed here...")
        self.results_text.configure(state='disabled')

        # GPT response text box moved to row 3
        self.gpt_response_text = scrolledtext.ScrolledText(self, width=200, height=20)
        self.gpt_response_text.grid(row=3, column=0, columnspan=3, padx=20, pady=20)
        self.gpt_response_text.insert(tk.END, "GPT-4 response will be displayed here...")
        self.gpt_response_text.configure(state='disabled')

        # Follow-up question label moved to row 4
        self.followup_label = tk.Label(self, text="Enter your follow-up question:")
        self.followup_label.grid(row=4, column=0, padx=20, pady=20, sticky="w")
        # Follow-up question entry moved to row 4
        self.followup_entry = tk.Entry(self, width=120)
        self.followup_entry.grid(row=4, column=1, padx=20, pady=20, sticky="w")

        # Follow-up button moved to row 4, column 2
        self.followup_button = tk.Button(self, text="Ask Follow-up", command=self.perform_followup)
        self.followup_button.grid(row=4, column=2, padx=20, pady=20)     

        # Save conversation button moved to row 5
        self.save_button = tk.Button(self, text="Save Research", command=self.save_chat)
        self.save_button.grid(row=5, column=0, padx=20, pady=20, sticky="w")
        # Add a new label to the GUI for displaying the token count
        self.token_count_label = tk.Label(self, text="Token count: 0")
        self.token_count_label.grid(row=6, column=0, padx=20, pady=20, sticky="w")

    def update_token_count(self):
        """
        Fetches the current token count from the GPTResponse and updates the label.
        """
        token_count = self.analyzer.gpt_response.count_tokens()
        self.token_count_label.config(text=f"Token count: {token_count}")

    def perform_analysis(self):
        query = self.query_entry.get()
        num_articles = self.article_count_var.get() 
        if not query.strip():
            return
        # Disable the buttons
        self.analyze_button.config(state=tk.DISABLED)
        self.followup_button.config(state=tk.DISABLED)
        # Show the loading label
        self.loading_label.grid()
        # Run the analysis in a separate thread to avoid blocking the main GUI
        threading.Thread(target=self.run_analysis, args=(query, num_articles)).start()

    def run_analysis(self, query, num_articles):
        # Show the loading label
        self.after(0, self.loading_label.grid)

        # Retrieve relevant documents based on the query
        relevant_documents = self.analyzer.get_relevant_documents(query, num_articles)

        # Capture the formatted documents
        formatted_documents = self.analyzer.format_documents(relevant_documents)

        # Schedule the update of the results_text on the main thread
        self.after(0, self.update_results_text, formatted_documents)

        # Get the GPT-3 response based on the formatted documents
        gpt_response = self.analyzer.gpt_response.get_response(query, formatted_documents)

        # Schedule the update of the gpt_response_text on the main thread
        self.after(0, self.update_gpt_response_text, gpt_response)

        # Hide the loading label after all operations are complete
        self.after(0, self.loading_label.grid_remove)
        self.after(0, lambda: self.analyze_button.config(state=tk.NORMAL))
        self.after(0, lambda: self.followup_button.config(state=tk.NORMAL))
        self.after(0, self.update_token_count)
        
    def perform_followup(self):
        followup_query = self.followup_entry.get()
        if not followup_query.strip():
            return
        # Disable the buttons
        self.analyze_button.config(state=tk.DISABLED)
        self.followup_button.config(state=tk.DISABLED)
        # Run the follow-up in a separate thread to avoid blocking the main GUI
        threading.Thread(target=self.run_followup, args=(followup_query,)).start()

    def run_followup(self, followup_query):
        # Capture the GPT-4 response
        gpt_response = self.analyzer.gpt_response.get_response(followup_query, "")
        # Re-enable the buttons after processing is done
        self.after(0, lambda: self.analyze_button.config(state=tk.NORMAL))
        self.after(0, lambda: self.followup_button.config(state=tk.NORMAL))
        # Schedule the update of the gpt_response_text on the main thread
        self.after(0, self.update_gpt_response_text, gpt_response)
        self.after(0, self.update_token_count)
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

    def save_chat(self):
        # Choose a default filename and extension
        default_filename = "chat_thread.txt"
        
        # Ask the user where to save the file
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], initialfile=default_filename)
        
        if not filepath:  # If the user cancels the dialog, filepath will be None
            return
        
        # Load the conversation history from JSON
        with open(self.analyzer.gpt_response.history_file, 'r', encoding='utf-8') as json_file:
            conversation_history = json.load(json_file)
        
        # Exclude the system message and format the conversation with IDs
        chat_content = ""
        for message in conversation_history[1:]:  # Skip the system message
            prefix = "User" if message['role'] == 'user' else "GPT"
            chat_content += f"{prefix} ID: {message['content']}\n\n"
        
        # Write the content to the chosen file
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(chat_content)
            messagebox.showinfo("Save Chat", "The chat thread was saved successfully.")
        except IOError as e:
            messagebox.showerror("Save Chat", f"An error occurred while saving the file: {e}")
        self.after(0, self.update_token_count)

if __name__ == "__main__":
    analyzer = NewsAnalyzer()
    app = NewsAnalyzerGUI(analyzer)
    app.mainloop()

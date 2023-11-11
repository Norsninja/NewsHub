import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter import ttk, messagebox
from analyzer import NewsAnalyzer
from ttkthemes import ThemedTk
import threading
import json

class NewsAnalyzerGUI(ThemedTk):
    def __init__(self, analyzer):
        super().__init__(theme="elegance")

        self.analyzer = analyzer

        # Set the title and size of the window
        self.title("News Analyzer")
        self.geometry("1920x1080")

        # Style Configuration
        self.style = ttk.Style(self)
        self.style.configure('TLabel', font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10))
        self.style.configure('TEntry', font=('Segoe UI', 10))
        self.style.configure('TCheckbutton', font=('Segoe UI', 10))

        # Query input section
        query_frame = ttk.LabelFrame(self, text="Query Input")
        query_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.query_label = ttk.Label(query_frame, text="Enter your query:")
        self.query_label.grid(row=0, column=0, sticky="w")
        self.query_entry = ttk.Entry(query_frame, width=60)
        self.query_entry.grid(row=0, column=1, padx=20, pady=20)
        self.analyze_button = ttk.Button(query_frame, text="Analyze", command=self.perform_analysis)
        self.analyze_button.grid(row=0, column=2, padx=20, pady=20)

        # Configuration Frame
        config_frame = ttk.LabelFrame(self, text="Configuration")
        config_frame.grid(row=1, column=0, padx=20, pady=20, sticky="w")

        # Max tokens configuration slider
        self.max_tokens_var = tk.IntVar(value=1000)
        self.max_tokens_slider = tk.Scale(config_frame, from_=1, to=2048, orient='horizontal', label='Max Tokens',
                                          variable=self.max_tokens_var, width=20)
        self.max_tokens_slider.grid(row=0, column=0, padx=20, pady=5, sticky="w")

        # Article count configuration
        self.article_count_var = tk.IntVar(value=15)
        self.article_count_label = ttk.Label(config_frame, text="Number of articles to retrieve:")
        self.article_count_label.grid(row=0, column=1, sticky="w")
        self.article_count_spinbox = ttk.Spinbox(config_frame, from_=1, to=100, textvariable=self.article_count_var, width=5)
        self.article_count_spinbox.grid(row=0, column=2, sticky="w")

        # Token count display
        self.token_count_label = ttk.Label(config_frame, text="Token count: 0")
        self.token_count_label.grid(row=0, column=3, padx=20, pady=20, sticky="w")

        # Results display area
        results_frame = ttk.LabelFrame(self, text="Analysis Results")
        results_frame.grid(row=2, column=0, padx=20, pady=20, sticky="w")

        self.results_text = scrolledtext.ScrolledText(results_frame, width=150, height=20, font=('Consolas', 10))
        self.results_text.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.results_text.insert(tk.END, "Retrieved Articles will be displayed here...")
        self.results_text.configure(state='disabled')

        # GPT response area
        gptresponse_frame = ttk.LabelFrame(self, text="GPT Response Text")
        gptresponse_frame.grid(row=3, column=0, padx=20, pady=20, sticky="w")
        self.gpt_response_text = scrolledtext.ScrolledText(gptresponse_frame, width=150, height=20, font=('Consolas', 10))
        self.gpt_response_text.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.gpt_response_text.insert(tk.END, "GPT-4 response will be displayed here...")
        self.gpt_response_text.configure(state='disabled')

        # Follow-up question section
        followup_frame = ttk.LabelFrame(self, text="Follow-up Question")
        followup_frame.grid(row=4, column=0, padx=20, pady=20, sticky="w")

        self.followup_label = ttk.Label(followup_frame, text="Enter your follow-up question:")
        self.followup_label.grid(row=0, column=0, sticky="w")
        self.followup_entry = ttk.Entry(followup_frame, width=120)
        self.followup_entry.grid(row=0, column=1, padx=20, pady=20, sticky="w")
        self.followup_button = ttk.Button(followup_frame, text="Ask Follow-up", command=self.perform_followup)
        self.followup_button.grid(row=0, column=2, padx=20, pady=20)

        # Save and clear history buttons
        history_frame = ttk.Frame(self)
        history_frame.grid(row=5, column=0, padx=20, pady=20, sticky="w")

        self.save_button = ttk.Button(history_frame, text="Save Research", command=self.save_chat)
        self.save_button.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        self.clear_history_button = ttk.Button(history_frame, text="Clear History", command=self.clear_history)
        self.clear_history_button.grid(row=0, column=1, padx=20, pady=20, sticky="e")
        # Loading label (initially hidden)
        self.loading_label = tk.Label(history_frame, text="Loading...")
        self.loading_label.grid(row=0, column=2, padx=20, pady=20, sticky="e")
        self.loading_label.grid_remove()

        # Query list display inside a frame
        querylist_frame = ttk.LabelFrame(self, text="Query List:")
        querylist_frame.grid(row=0, column=1, rowspan=4, padx=10, pady=10, sticky="nsw")
        
        # Configure the grid within the frame to allow Listbox to expand

        querylist_frame.grid_columnconfigure(0, weight=1)

        # Place the Listbox inside the frame
        self.query_listbox = tk.Listbox(querylist_frame, width=25, height=10)
        self.query_listbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")


        # Set weights for rows and columns
        self.grid_columnconfigure(0, weight=3)  # Main content column expands more
        self.grid_columnconfigure(1, weight=1)  # Query list column
        for i in range(6):  # Assuming you have 6 rows in total
            self.grid_rowconfigure(i, weight=1)

    def update_query_list(self, query):
        """Add a new query to the Listbox."""
        self.query_listbox.insert(tk.END, query)

    def update_token_count(self):
        """
        Fetches the current token count from the GPTResponse and updates the label.
        """
        token_count = self.analyzer.gpt_response.count_tokens()
        self.token_count_label.config(text=f"Token count: {token_count}")

    def perform_analysis(self):
        query = self.query_entry.get()
        # Update the query list with the new query
        self.update_query_list(query)
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
        max_tokens = self.max_tokens_var.get()  # Retrieve the current value of max_tokens from the slider
        gpt_response = self.analyzer.gpt_response.get_response(query, formatted_documents, max_tokens)

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


    def run_analysis(self, query, num_articles):
        # Show the loading label
        self.after(0, self.loading_label.grid)

        # Retrieve relevant documents based on the query
        relevant_documents = self.analyzer.get_relevant_documents(query, num_articles)

        # Capture the formatted documents
        formatted_documents = self.analyzer.format_documents(relevant_documents)

        # Schedule the update of the results_text on the main thread
        self.after(0, self.update_results_text, formatted_documents)
        max_tokens = self.max_tokens_var.get()  # Retrieve the current value of max_tokens from the slider
        gpt_response = self.analyzer.gpt_response.get_response(query, formatted_documents, max_tokens)
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
        max_tokens = self.max_tokens_var.get()  # Retrieve the current value of max_tokens from the slider
        gpt_response = self.analyzer.gpt_response.get_response(followup_query, "", max_tokens)
        # Re-enable the buttons after processing is done
        self.after(0, lambda: self.analyze_button.config(state=tk.NORMAL))
        self.after(0, lambda: self.followup_button.config(state=tk.NORMAL))
        # Schedule the update of the gpt_response_text on the main thread
        self.after(0, self.update_gpt_response_text, gpt_response)
        self.after(0, self.update_token_count)
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

    def clear_history(self):
        # Ask for user confirmation
        response = messagebox.askyesno("Clear History", "Are you sure you want to clear the history?")

        # Check the user's response
        if response:  # If the user clicked "Yes"
            self.analyzer.gpt_response.clear_history()
            
            # Clear the gpt_response_text widget
            if hasattr(self, 'gpt_response_text'):
                self.gpt_response_text.configure(state='normal')
                self.gpt_response_text.delete(1.0, tk.END)

            if hasattr(self, 'results_text'):
                self.results_text.configure(state='normal')
                self.results_text.delete(1.0, tk.END)
        else:
            # User chose not to clear the history
            print("History clear cancelled.")

if __name__ == "__main__":
    analyzer = NewsAnalyzer()
    app = NewsAnalyzerGUI(analyzer)
    app.mainloop()

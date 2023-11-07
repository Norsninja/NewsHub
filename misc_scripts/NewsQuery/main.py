from gui import NewsAnalyzerGUI
from analyzer import NewsAnalyzer


if __name__ == "__main__":
    analyzer = NewsAnalyzer()
    app = NewsAnalyzerGUI(analyzer)
    app.mainloop()
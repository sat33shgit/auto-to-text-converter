
# 📝 Meeting Notes Analyzer

A simple, local tool to analyze meeting notes (in plain text format) and generate a professional summary and action items. Outputs can be saved as a Word document or text file.

## ✨ Features
- Summarizes meeting notes into executive summary, key points, and action items
- Extracts decisions, risks, next steps, and meeting metadata
- Supports local, Ollama, or OpenAI GPT-based analysis (if available)
- Outputs a well-formatted Word (.docx) or text file
- Interactive or command-line usage

## 🚀 Quick Start

### 1. Install Requirements
```bash
pip install -r meeting_requirements.txt
```

### 2. Run the Analyzer
```bash
python meeting_analyzer.py --interactive
```

Or analyze a file directly:
```bash
python meeting_analyzer.py your_meeting_notes.txt
```

## 🛠️ Usage
- Choose to load meeting notes from a file or paste them directly
- Select the analysis model (local, Ollama, or OpenAI)
- The tool generates a summary and action items
- Output is saved as a Word document or text file

## 📁 Project Structure
```
AudioToText/
├── meeting_analyzer.py         # Main analyzer script
├── meeting_requirements.txt    # Python dependencies
├── README.md                   # This file
├── meeting_summary_*.docx      # Output files (generated)
```

## 📋 Requirements
- Python 3.8+
- `python-docx` (for Word output)
- (Optional) `ollama` or `openai` for AI-powered analysis

## 📄 License
MIT License - feel free to use and modify!

---

**Easily turn your meeting notes into actionable summaries!**

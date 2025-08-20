import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
from audio_converter import AudioToTextConverter
import json

class AudioToTextGUI:
    """
    GUI application for audio-to-text conversion using Tkinter.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Audio to Text Converter")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Initialize converter
        self.converter = AudioToTextConverter()
        
        # Variables
        self.input_files = []
        self.output_directory = tk.StringVar()
        self.selected_engine = tk.StringVar(value="google")
        self.selected_language = tk.StringVar(value="en-US")
        self.chunk_audio = tk.BooleanVar(value=False)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Audio to Text Converter", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="5")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # Input files
        ttk.Label(file_frame, text="Audio Files:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.files_listbox = tk.Listbox(file_frame, height=4)
        self.files_listbox.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        files_buttons_frame = ttk.Frame(file_frame)
        files_buttons_frame.grid(row=0, column=2, sticky=tk.N)
        
        ttk.Button(files_buttons_frame, text="Add Files", 
                  command=self.add_files).pack(pady=(0, 5))
        ttk.Button(files_buttons_frame, text="Add Folder", 
                  command=self.add_folder).pack(pady=(0, 5))
        ttk.Button(files_buttons_frame, text="Clear", 
                  command=self.clear_files).pack()
        
        # Output directory
        ttk.Label(file_frame, text="Output Directory:").grid(row=1, column=0, sticky=tk.W, 
                                                            padx=(0, 5), pady=(10, 0))
        
        output_frame = ttk.Frame(file_frame)
        output_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        output_frame.columnconfigure(0, weight=1)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_directory)
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(output_frame, text="Browse", 
                  command=self.select_output_directory).grid(row=0, column=1)
        
        # Settings section
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="5")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Engine selection
        ttk.Label(settings_frame, text="Recognition Engine:").grid(row=0, column=0, sticky=tk.W)
        
        engine_frame = ttk.Frame(settings_frame)
        engine_frame.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Radiobutton(engine_frame, text="Google Speech Recognition", 
                       variable=self.selected_engine, value="google").pack(side=tk.LEFT)
        ttk.Radiobutton(engine_frame, text="OpenAI Whisper", 
                       variable=self.selected_engine, value="whisper").pack(side=tk.LEFT, padx=(20, 0))
        
        # Language selection
        ttk.Label(settings_frame, text="Language:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        language_combo = ttk.Combobox(settings_frame, textvariable=self.selected_language, 
                                     values=[
                                         "en-US", "en-GB", "es-ES", "fr-FR", "de-DE", 
                                         "it-IT", "pt-BR", "ru-RU", "ja-JP", "ko-KR", 
                                         "zh-CN", "ar-SA", "hi-IN"
                                     ])
        language_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        
        # Advanced options
        ttk.Checkbutton(settings_frame, text="Split long audio into chunks", 
                       variable=self.chunk_audio).grid(row=2, column=0, columnspan=2, 
                                                      sticky=tk.W, pady=(10, 0))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.convert_button = ttk.Button(button_frame, text="Convert to Text", 
                                        command=self.start_conversion, style="Accent.TButton")
        self.convert_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Load Whisper Model", 
                  command=self.load_whisper_model).pack(side=tk.LEFT)
        
        # Progress and output section
        output_frame = ttk.LabelFrame(main_frame, text="Progress and Output", padding="5")
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(1, weight=1)
        
        # Progress bar
        self.progress = ttk.Progressbar(output_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, wrap=tk.WORD)
        self.output_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
    def add_files(self):
        """Add audio files to the conversion list."""
        filetypes = [
            ("Audio files", "*.mp3 *.wav *.flac *.m4a *.ogg *.aac *.wma"),
            ("MP3 files", "*.mp3"),
            ("WAV files", "*.wav"),
            ("FLAC files", "*.flac"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(title="Select Audio Files", filetypes=filetypes)
        
        for file in files:
            if file not in self.input_files:
                self.input_files.append(file)
                self.files_listbox.insert(tk.END, os.path.basename(file))
        
        self.update_status(f"Added {len(files)} file(s)")
        
    def add_folder(self):
        """Add all audio files from a folder."""
        folder = filedialog.askdirectory(title="Select Folder with Audio Files")
        
        if folder:
            audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac', '.wma'}
            added_count = 0
            
            for file_path in Path(folder).rglob("*"):
                if file_path.suffix.lower() in audio_extensions:
                    file_str = str(file_path)
                    if file_str not in self.input_files:
                        self.input_files.append(file_str)
                        self.files_listbox.insert(tk.END, file_path.name)
                        added_count += 1
            
            self.update_status(f"Added {added_count} file(s) from folder")
    
    def clear_files(self):
        """Clear the list of input files."""
        self.input_files.clear()
        self.files_listbox.delete(0, tk.END)
        self.update_status("File list cleared")
    
    def select_output_directory(self):
        """Select output directory for transcription files."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_directory.set(directory)
    
    def load_whisper_model(self):
        """Load Whisper model in a separate thread."""
        def load_model():
            self.update_status("Loading Whisper model...")
            self.progress.start()
            
            success = self.converter.load_whisper_model("base")
            
            self.progress.stop()
            
            if success:
                self.update_status("Whisper model loaded successfully")
                messagebox.showinfo("Success", "Whisper model loaded successfully!")
            else:
                self.update_status("Failed to load Whisper model")
                messagebox.showerror("Error", "Failed to load Whisper model. Make sure it's installed.")
        
        threading.Thread(target=load_model, daemon=True).start()
    
    def start_conversion(self):
        """Start the conversion process in a separate thread."""
        if not self.input_files:
            messagebox.showwarning("Warning", "Please select audio files first.")
            return
        
        if not self.output_directory.get():
            # Set default output directory
            default_output = os.path.join(os.path.dirname(self.input_files[0]), "transcriptions")
            self.output_directory.set(default_output)
        
        # Disable convert button during processing
        self.convert_button.config(state="disabled")
        
        # Start conversion in a separate thread
        threading.Thread(target=self.convert_files, daemon=True).start()
    
    def convert_files(self):
        """Convert audio files to text."""
        try:
            self.progress.start()
            self.update_status("Starting conversion...")
            
            output_dir = self.output_directory.get()
            os.makedirs(output_dir, exist_ok=True)
            
            engine = self.selected_engine.get()
            language = self.selected_language.get()
            chunk_audio = self.chunk_audio.get()
            
            results = []
            
            for i, file_path in enumerate(self.input_files, 1):
                self.update_status(f"Processing file {i}/{len(self.input_files)}: {os.path.basename(file_path)}")
                
                result = self.converter.transcribe_file(
                    file_path, 
                    engine=engine, 
                    language=language,
                    chunk_audio=chunk_audio
                )
                
                results.append(result)
                
                # Display result in output area
                file_name = os.path.basename(file_path)
                self.output_text.insert(tk.END, f"\n{'='*50}\n")
                self.output_text.insert(tk.END, f"File: {file_name}\n")
                self.output_text.insert(tk.END, f"Status: {'Success' if result['success'] else 'Failed'}\n")
                
                if result["success"]:
                    self.output_text.insert(tk.END, f"Transcription:\n{result['text']}\n")
                    
                    # Save to file
                    output_file = Path(output_dir) / f"{Path(file_path).stem}.txt"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(result['text'])
                else:
                    self.output_text.insert(tk.END, f"Error: {result['error']}\n")
                
                self.output_text.see(tk.END)
                self.root.update_idletasks()
            
            # Save summary report
            summary_file = Path(output_dir) / "conversion_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            # Show completion message
            successful = sum(1 for r in results if r["success"])
            total = len(results)
            
            self.update_status(f"Conversion completed: {successful}/{total} files successful")
            messagebox.showinfo("Conversion Complete", 
                              f"Conversion completed!\n"
                              f"Successful: {successful}/{total}\n"
                              f"Results saved to: {output_dir}")
            
        except Exception as e:
            self.update_status(f"Error during conversion: {str(e)}")
            messagebox.showerror("Error", f"An error occurred during conversion:\n{str(e)}")
        
        finally:
            self.progress.stop()
            self.convert_button.config(state="normal")
    
    def update_status(self, message):
        """Update the status bar."""
        self.status_var.set(message)
        self.root.update_idletasks()

def main():
    """Run the GUI application."""
    root = tk.Tk()
    app = AudioToTextGUI(root)
    
    # Set up proper closing
    def on_closing():
        root.quit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()

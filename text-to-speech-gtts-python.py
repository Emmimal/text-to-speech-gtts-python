import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import threading

class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text-to-Speech Reader")
        self.root.geometry("600x500")
        
        self.is_speaking = False
        self.current_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        <em># Text input area</em>
        self.text_area = scrolledtext.ScrolledText(
            self.root, 
            wrap=tk.WORD, 
            width=70, 
            height=20
        )
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        <em># Button frame</em>
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        <em># Buttons</em>
        tk.Button(button_frame, text="Load File", command=self.load_file).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Speak", command=self.start_speaking).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Stop", command=self.stop_speaking).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear", command=self.clear_text).pack(side=tk.LEFT, padx=5)
        
        <em># Status label</em>
        self.status_label = tk.Label(self.root, text="Ready")
        self.status_label.pack(pady=5)
    
    def load_file(self):
        """Load text from a file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(1.0, content)
                    self.status_label.config(text=f"Loaded: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")
    
    def start_speaking(self):
        """Start speaking the text"""
        if self.is_speaking:
            return
            
        text = self.text_area.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "No text to speak!")
            return
        
        self.is_speaking = True
        self.status_label.config(text="Speaking...")
        
        <em># Run TTS in a separate thread so UI doesn't freeze</em>
        self.current_thread = threading.Thread(target=self.speak_text, args=(text,))
        self.current_thread.daemon = True
        self.current_thread.start()
    
    def speak_text(self, text):
        """Actually do the text-to-speech conversion"""
        try:
            clean_text = clean_for_speech(text)
            chunks = split_long_text(clean_text)
            
            for i, chunk in enumerate(chunks):
                if not self.is_speaking:  <em># Check if user clicked stop</em>
                    break
                    
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Speaking chunk {i + 1}/{len(chunks)}"
                ))
                
                <em># Use our robust TTS function</em>
                audio_buffer = robust_tts(chunk)
                if audio_buffer:
                    pygame.mixer.init()
                    pygame.mixer.music.load(audio_buffer)
                    pygame.mixer.music.play()
                    
                    while pygame.mixer.music.get_busy() and self.is_speaking:
                        time.sleep(0.1)
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"TTS failed: {e}"))
        
        finally:
            self.is_speaking = False
            self.root.after(0, lambda: self.status_label.config(text="Ready"))
    
    def stop_speaking(self):
        """Stop the current speech"""
        self.is_speaking = False
        pygame.mixer.music.stop()
        self.status_label.config(text="Stopped")
    
    def clear_text(self):
        """Clear the text area"""
        self.text_area.delete(1.0, tk.END)
        self.status_label.config(text="Ready")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()

import cv2
import numpy as np
import pyautogui
import pytesseract
import keyboard
import tkinter as tk
from tkinter import ttk, scrolledtext
from googletrans import Translator
from deep_translator import GoogleTranslator, DeeplTranslator
import mtranslate
import threading

# Set Tesseract path (for Windows, adjust as needed)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def capture_screen():
    """Takes a screenshot and returns an OpenCV image."""
    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    return frame

def preprocess_image(image):
    """Enhances image for better OCR accuracy."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def extract_text(image):
    """Extracts text from an image using OCR."""
    processed_image = preprocess_image(image)
    text = pytesseract.image_to_string(processed_image, lang="eng")
    return text.strip()

def translate_text(text, service="google"):
    """Translates text using the selected translation service."""
    if not text:
        return "No text detected."

    try:
        if service == "google":
            return GoogleTranslator(source="auto", target="en").translate(text)
        elif service == "deepl":
            return DeeplTranslator(source="auto", target="EN-US").translate(text)
        elif service == "mtranslate":
            return mtranslate.translate(text, "en")
        elif service == "googletrans":
            translator = Translator()
            return translator.translate(text, dest="en").text
    except Exception as e:
        return f"Translation Error: {str(e)}"

def process_screen():
    """Processes the screen capture, extracts text, and translates it."""
    frame = capture_screen()
    extracted_text = extract_text(frame)
    translation_service = translator_var.get()
    translated_text = translate_text(extracted_text, service=translation_service)

    extracted_text_box.delete("1.0", tk.END)
    extracted_text_box.insert(tk.END, extracted_text)

    translated_text_box.delete("1.0", tk.END)
    translated_text_box.insert(tk.END, translated_text)

def hotkey_listener():
    """Listens for a hotkey and triggers screen translation."""
    keyboard.add_hotkey("ctrl+shift+t", lambda: process_screen())
    keyboard.wait()  # Keep the listener active

# GUI Setup
root = tk.Tk()
root.title("Screen Text Translator")
root.geometry("600x500")

# Label for Translator Selection
ttk.Label(root, text="Select Translator:").pack(pady=5)

# Dropdown for Translator Selection
translator_var = tk.StringVar(value="google")
translator_options = ["google", "deepl", "mtranslate", "googletrans"]
translator_menu = ttk.Combobox(root, textvariable=translator_var, values=translator_options, state="readonly")
translator_menu.pack()

# Capture Button
capture_button = ttk.Button(root, text="Capture & Translate", command=process_screen)
capture_button.pack(pady=10)

# Extracted Text Label
ttk.Label(root, text="Extracted Text:").pack()
extracted_text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=6, width=70)
extracted_text_box.pack()

# Translated Text Label
ttk.Label(root, text="Translated Text:").pack()
translated_text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=6, width=70)
translated_text_box.pack()

# Start Hotkey Listener in Background
threading.Thread(target=hotkey_listener, daemon=True).start()

# Run GUI Loop
root.mainloop()

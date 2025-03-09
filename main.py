import cv2
import numpy as np
import pyautogui
import pytesseract
import keyboard
import easyocr
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from googletrans import Translator
from deep_translator import GoogleTranslator, DeeplTranslator
import mtranslate
import threading
import datetime

# Set Tesseract path (for Windows, adjust as needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize EasyOCR Reader
reader = easyocr.Reader(['en'])


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
  """Extracts text from an image using EasyOCR."""
  results = reader.readtext(image)
  extracted_text = " ".join([res[1] for res in results])
  return extracted_text.strip()


def translate_text(text, source_lang="auto", target_lang="en", service="google"):
  """Translates text using the selected translation service."""
  if not text:
    return "No text detected."

  try:
    if service == "google":
      return GoogleTranslator(source=source_lang, target=target_lang).translate(text)
    elif service == "deepl":
      return DeeplTranslator(source=source_lang, target=target_lang).translate(text)
    elif service == "mtranslate":
      return mtranslate.translate(text, target_lang)
    elif service == "googletrans":
      translator = Translator()
      return translator.translate(text, src=source_lang, dest=target_lang).text
  except Exception as e:
    return f"Translation Error: {str(e)}"


def process_screen():
  """Processes the screen capture, extracts text, and translates it."""
  frame = capture_screen()
  extracted_text = extract_text(frame)

  source_lang = source_lang_var.get()
  target_lang = target_lang_var.get()
  translation_service = translator_var.get()

  translated_text = translate_text(extracted_text, source_lang, target_lang, service=translation_service)

  extracted_text_box.delete("1.0", tk.END)
  extracted_text_box.insert(tk.END, extracted_text)

  translated_text_box.delete("1.0", tk.END)
  translated_text_box.insert(tk.END, translated_text)

  save_translation(extracted_text, translated_text)


def save_translation(original, translated):
  """Saves translations to a file with timestamps."""
  with open("translations.txt", "a", encoding="utf-8") as file:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file.write(f"[{timestamp}]\nOriginal: {original}\nTranslated: {translated}\n\n")


def view_saved_translations():
  """Opens the saved translations file."""
  filepath = "translations.txt"
  try:
    with open(filepath, "r", encoding="utf-8") as file:
      content = file.read()
      saved_text_box.delete("1.0", tk.END)
      saved_text_box.insert(tk.END, content)
  except FileNotFoundError:
    saved_text_box.insert(tk.END, "No saved translations yet.")


def hotkey_listener():
  """Listens for a hotkey and triggers screen translation."""
  keyboard.add_hotkey("ctrl+shift+t", lambda: process_screen())
  keyboard.wait()


def overlay_text():
  """Displays an overlay of the detected text on screen."""
  frame = capture_screen()
  results = reader.readtext(frame)

  for (bbox, text, prob) in results:
    (top_left, top_right, bottom_right, bottom_left) = bbox
    top_left = tuple(map(int, top_left))
    bottom_right = tuple(map(int, bottom_right))
    cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
    cv2.putText(frame, text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

  cv2.imshow("Detected Text", frame)
  cv2.waitKey(3000)
  cv2.destroyAllWindows()


# GUI Setup
root = tk.Tk()
root.title("Screen Text Translator")
root.geometry("700x600")

# Translator Selection
ttk.Label(root, text="Select Translator:").pack(pady=5)
translator_var = tk.StringVar(value="google")
translator_options = ["google", "deepl", "mtranslate", "googletrans"]
translator_menu = ttk.Combobox(root, textvariable=translator_var, values=translator_options, state="readonly")
translator_menu.pack()

# Language Selection
ttk.Label(root, text="Source Language:").pack()
source_lang_var = tk.StringVar(value="auto")
source_lang_entry = ttk.Entry(root, textvariable=source_lang_var)
source_lang_entry.pack()

ttk.Label(root, text="Target Language:").pack()
target_lang_var = tk.StringVar(value="en")
target_lang_entry = ttk.Entry(root, textvariable=target_lang_var)
target_lang_entry.pack()

# Capture & Translate Button
capture_button = ttk.Button(root, text="Capture & Translate", command=process_screen)
capture_button.pack(pady=10)

# Extracted Text Label
ttk.Label(root, text="Extracted Text:").pack()
extracted_text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=5, width=80)
extracted_text_box.pack()

# Translated Text Label
ttk.Label(root, text="Translated Text:").pack()
translated_text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=5, width=80)
translated_text_box.pack()

# Overlay Button
overlay_button = ttk.Button(root, text="Show Overlay", command=overlay_text)
overlay_button.pack(pady=5)

# View Saved Translations Button
view_translations_button = ttk.Button(root, text="View Saved Translations", command=view_saved_translations)
view_translations_button.pack(pady=5)

# Saved Translations Box
saved_text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10, width=80)
saved_text_box.pack()

# Start Hotkey Listener in Background
threading.Thread(target=hotkey_listener, daemon=True).start()

# Run GUI Loop
root.mainloop()

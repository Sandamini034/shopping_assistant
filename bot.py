import spacy
import difflib
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

nlp = spacy.load("en_core_web_sm")

product_shelves = {
    "milk": "Shelf 1", "bread": "Shelf 2", "egg": "Shelf 3",
    "chicken": "Shelf 5", "rice": "Shelf 6", "pasta": "Shelf 6",
    "cereal": "Shelf 7", "cheese": "Shelf 8"
}
fruits = {"apple", "banana", "orange", "grape", "mango", "pineapple"}
vegetables = {"carrot", "potato", "tomato", "onion", "spinach", "cabbage"}
fruit_shelf = "Shelf 4"
vegetable_shelf = "Shelf 9"
all_items = list(product_shelves.keys()) + list(fruits) + list(vegetables)

shopping_list = {}
last_suggestion = None
last_original_word = None

# Save folder
SAVE_FOLDER = r"E:\Semester_5\NLP\Assignments\Assignment_2\22_ENG_057_Assignment_2\Shopping_list"
os.makedirs(SAVE_FOLDER, exist_ok=True) 

# Words we don’t want to treat as products
ignore_words = {"shopping", "list", "buy", "need", "want"}

def extract_items(user_input):
    doc = nlp(user_input.lower())
    return [
        (token.text, token.lemma_) 
        for token in doc 
        if token.pos_ in ["NOUN", "PROPN"] and token.lemma_ not in ignore_words
    ]


def get_shelf(item):
    if item in fruits: return fruit_shelf
    if item in vegetables: return vegetable_shelf
    if item in product_shelves: return product_shelves[item]
    return None

def save_shopping_list_to_txt():
    if not shopping_list: return " Shopping list empty, nothing to save."
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"shopping_list_{timestamp}.txt"
    filepath = os.path.join(SAVE_FOLDER, filename)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("--- Shopping List with Shelf Numbers ---\n")
            for item, shelf in shopping_list.items():
                f.write(f"{item.capitalize()} → {shelf}\n")
            f.write("-------------------------------------------\n")
    except Exception as e:
        return f" Error saving TXT: {e}"
    return f" Shopping list saved as TXT at:\n{filepath}"

def save_shopping_list_to_pdf():
    if not shopping_list: return " Shopping list empty, nothing to save."
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"shopping_list_{timestamp}.pdf"
    filepath = os.path.join(SAVE_FOLDER, filename)
    try:
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 16)
        c.drawString(200, height - 50, "Shopping List 🛒")

        c.setFont("Helvetica", 12)
        y = height - 100
        for item, shelf in shopping_list.items():
            c.drawString(100, y, f"{item.capitalize()} → {shelf}")
            y -= 20
            if y < 50: 
                c.showPage()
                c.setFont("Helvetica", 12)
                y = height - 50

        c.save()
    except Exception as e:
        return f" Error saving PDF: {e}"
    return f" Shopping list saved as PDF at:\n{filepath}"

def chatbot_response(user_input):
    global last_suggestion, last_original_word
    user_input = user_input.lower().strip()

    # Handle confirmation of suggested correction
    if user_input in ["yes", "y"] and last_suggestion:
        corrected_item = last_suggestion
        shelf = get_shelf(corrected_item)
        if shelf:
            shopping_list[corrected_item] = shelf
            response = f"{corrected_item.capitalize()} → {shelf}"
        else:
            response = f"Could not find {corrected_item}"
        last_suggestion = None
        last_original_word = None
        return response

    # Handle rejection of suggested correction
    if user_input in ["no", "n"] and last_suggestion:
        last_suggestion = None
        last_original_word = None
        return "Okay, item not added."

    # Handle saving commands
    if "save as pdf" in user_input or "save pdf" in user_input:
        return save_shopping_list_to_pdf()
    if "save my list" in user_input or "save list" in user_input or "save shopping list" in user_input:
        return save_shopping_list_to_txt()

    # Greetings / farewells
    if user_input in ["hi", "hello", "hey"]:
        return "Hi there! How can I help you today?"
    if user_input in ["thanks", "thank you"]:
        return "You're welcome! Anything else?"
    if user_input in ["bye", "goodbye"]:
        return "Goodbye, happy shopping!"

    items = extract_items(user_input)
    if not items:
        return "Could not detect any items."

    responses = []
    for original, lemma in items:
        shelf = get_shelf(lemma) or get_shelf(original)
        if shelf:
            shopping_list[original] = shelf  # Add only valid items directly
            responses.append(f"{original.capitalize()} → {shelf}")
        else:
            suggestion = difflib.get_close_matches(lemma, all_items, n=1, cutoff=0.7)
            if suggestion:
                last_suggestion = suggestion[0]
                last_original_word = original
                responses.append(f"Item '{original}' not found. Did you mean '{suggestion[0]}'?")
            else:
                responses.append(f"{original.capitalize()} → Item not found")

    return "\n".join(responses)

def send_message():
    user_input = entry.get()
    if not user_input.strip(): return
    chat_window.config(state=tk.NORMAL)
    chat_window.insert(tk.END, "You: " + user_input + "\n")
    response = chatbot_response(user_input)
    chat_window.insert(tk.END, "Bot: " + response + "\n\n")
    chat_window.config(state=tk.DISABLED)
    chat_window.see(tk.END)
    entry.delete(0, tk.END)

# GUI
root = tk.Tk()
root.title("Elsa - Your Shopping Assistant 🛒")
root.geometry("500x500")

chat_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED)
chat_window.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

entry = tk.Entry(root, width=70)
entry.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)

send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack(side=tk.RIGHT, padx=10, pady=10)

root.mainloop()

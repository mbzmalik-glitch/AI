import tkinter as tk
from tkinter import messagebox
import random
import string
import json
import os
from datetime import datetime

# ============================================================================
# REUSABLE KEY GENERATION FUNCTIONS - Can be imported by other programs
# ============================================================================

KEYS_FILE = "secret_keys.json"

def generate_secret_key(length=16):
    """
    Generate a single random secret key.
    
    Args:
        length (int): Length of the key (default: 16)
    
    Returns:
        str: Random secret key containing letters, digits, and special characters
    """
    valid_chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(valid_chars) for _ in range(length))

def generate_multiple_keys(count=4, length=16):
    """
    Generate multiple random secret keys.
    
    Args:
        count (int): Number of keys to generate (default: 4)
        length (int): Length of each key (default: 16)
    
    Returns:
        list: List of random secret keys
    """
    return [generate_secret_key(length) for _ in range(count)]

def save_keys_to_file(keys, length):
    """
    Save generated keys to a JSON file.
    
    Args:
        keys (list): List of keys to save
        length (int): Length of the keys
    """
    data = {
        "keys": keys,
        "length": length,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(KEYS_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"Keys saved to {KEYS_FILE}")

def load_keys_from_file():
    """
    Load previously generated keys from file.
    
    Returns:
        dict: Dictionary with 'keys', 'length', and 'generated_at' or None if no file exists
    """
    if os.path.exists(KEYS_FILE):
        try:
            with open(KEYS_FILE, 'r') as f:
                data = json.load(f)
            print(f"Loaded existing keys from {KEYS_FILE}")
            return data
        except:
            return None
    return None

def get_all_keys():
    """
    Get all saved keys.
    
    Returns:
        list: List of all keys, or empty list if no keys exist
    """
    data = load_keys_from_file()
    if data:
        return data['keys']
    return []

def get_key_by_index(index):
    """
    Get a specific key by index (0-3).
    
    Args:
        index (int): Index of the key (0-3)
    
    Returns:
        str: The key at that index, or None if index is invalid or no keys exist
    """
    keys = get_all_keys()
    if 0 <= index < len(keys):
        return keys[index]
    return None

def get_key_info():
    """
    Get information about the saved keys.
    
    Returns:
        dict: Dictionary with keys info or None if no keys exist
    """
    return load_keys_from_file()

# ============================================================================
# GUI INTERFACE
# ============================================================================

class SecretKeyGenerator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Secret Key Generator")
        self.root.geometry("600x550")
        self.root.resizable(False, False)
        
        # All keyboard valid characters
        self.valid_chars = string.ascii_letters + string.digits + string.punctuation
        
        # Load existing keys if available
        self.existing_keys = load_keys_from_file()
        
        self.setup_ui()
        
        # Display existing keys if available
        if self.existing_keys:
            self.display_existing_keys()
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="Secret Key Generator", 
                        font=('Arial', 20, 'bold'), fg='darkblue', pady=15)
        title.pack()
        
        # Status label (shows if keys are loaded from previous session)
        self.status_label = tk.Label(self.root, text="", 
                                     font=('Arial', 10, 'italic'), fg='gray')
        self.status_label.pack()
        
        # Instructions
        instructions = tk.Label(self.root, 
                               text="Select key length and click 'Generate Keys'",
                               font=('Arial', 12))
        instructions.pack(pady=10)
        
        # Key length selection frame
        length_frame = tk.Frame(self.root)
        length_frame.pack(pady=20)
        
        tk.Label(length_frame, text="Key Length:", font=('Arial', 12, 'bold')).pack(side='left', padx=10)
        
        self.key_length = tk.IntVar(value=16)
        
        # Radio buttons for length selection
        for length in [8, 16, 32]:
            rb = tk.Radiobutton(length_frame, text=str(length), 
                               variable=self.key_length, value=length,
                               font=('Arial', 11))
            rb.pack(side='left', padx=10)
        
        # Generate button
        generate_btn = tk.Button(self.root, text="Generate Keys", 
                                command=self.generate_keys,
                                font=('Arial', 14, 'bold'), 
                                bg='green', fg='white',
                                padx=30, pady=10)
        generate_btn.pack(pady=20)
        
        # Display frame for keys
        self.display_frame = tk.Frame(self.root, bg='lightgray', relief='sunken', bd=2)
        self.display_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        self.key_labels = []
        for i in range(4):
            frame = tk.Frame(self.display_frame, bg='white', pady=5)
            frame.pack(pady=5, padx=10, fill='x')
            
            label_text = tk.Label(frame, text=f"Key {i+1}:", 
                                 font=('Courier', 11, 'bold'), bg='white')
            label_text.pack(side='left', padx=5)
            
            key_display = tk.Label(frame, text="", 
                                  font=('Courier', 10), bg='white',
                                  fg='darkgreen', wraplength=500, justify='left')
            key_display.pack(side='left', padx=5, fill='x', expand=True)
            
            self.key_labels.append(key_display)
    
    def generate_keys(self):
        """Generate 4 random secret keys using the reusable function"""
        length = self.key_length.get()
        
        # Use the reusable function
        keys = generate_multiple_keys(count=4, length=length)
        
        # Save to file
        save_keys_to_file(keys, length)
        
        # Display the keys
        for i, key in enumerate(keys):
            self.key_labels[i].config(text=key)
        
        # Update status
        self.status_label.config(text=f"Keys generated and saved! (Length: {length})")
        
        print(f"\nGenerated {len(keys)} secret keys of length {length}:")
        for i, key in enumerate(keys, 1):
            print(f"Key {i}: {key}")
    
    def display_existing_keys(self):
        """Display previously generated keys"""
        keys = self.existing_keys['keys']
        length = self.existing_keys['length']
        generated_at = self.existing_keys['generated_at']
        
        # Set the radio button to match loaded key length
        self.key_length.set(length)
        
        # Display the keys
        for i, key in enumerate(keys):
            self.key_labels[i].config(text=key)
        
        # Update status
        self.status_label.config(text=f"Loaded existing keys (Generated: {generated_at})")
        
        print(f"\nLoaded existing keys from previous session:")
        for i, key in enumerate(keys, 1):
            print(f"Key {i}: {key}")
    
    def run(self):
        self.root.mainloop()

def main():
    print("="*60)
    print("SECRET KEY GENERATOR")
    print("="*60)
    print("\nThis program generates 4 random secret keys.")
    print("Choose a key length: 8, 16, or 32 characters")
    print("Keys can contain letters, digits, and special characters")
    print("\nNote: You can also import this module in other programs:")
    print("  from secret_key_generator import generate_secret_key")
    print("  from secret_key_generator import generate_multiple_keys")
    print("="*60 + "\n")
    
    app = SecretKeyGenerator()
    app.run()

if __name__ == "__main__":
    main()

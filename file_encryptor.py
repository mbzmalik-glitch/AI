import tkinter as tk
from tkinter import filedialog, messagebox
import os
from cryptography.fernet import Fernet
import base64
import hashlib
from secret_key_generator import get_key_by_index, get_all_keys, get_key_info

class FileEncryptorDecryptor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("File Encryptor/Decryptor")
        self.root.geometry("600x550")
        self.root.resizable(False, False)
        
        self.selected_file = None
        self.selected_key_index = tk.IntVar(value=0)
        
        self.setup_ui()
        self.load_available_keys()
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="File Encryptor/Decryptor", 
                        font=('Arial', 20, 'bold'), fg='darkblue', pady=20)
        title.pack()
        
        # File selection section
        file_frame = tk.Frame(self.root, bg='lightgray', relief='ridge', bd=2)
        file_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(file_frame, text="Selected File:", font=('Arial', 11, 'bold'), bg='lightgray').pack(pady=5)
        
        self.file_label = tk.Label(file_frame, text="No file selected", 
                                   font=('Arial', 10), bg='white', 
                                   relief='sunken', padx=10, pady=5)
        self.file_label.pack(pady=5, padx=10, fill='x')
        
        select_btn = tk.Button(file_frame, text="Select File", 
                              command=self.select_file,
                              font=('Arial', 11), bg='lightblue', padx=20, pady=5)
        select_btn.pack(pady=10)
        
        # Key selection section
        key_frame = tk.Frame(self.root, bg='lightyellow', relief='ridge', bd=2)
        key_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(key_frame, text="Select Encryption Key:", 
                font=('Arial', 11, 'bold'), bg='lightyellow').pack(pady=5)
        
        self.key_display_frame = tk.Frame(key_frame, bg='lightyellow')
        self.key_display_frame.pack(pady=5, padx=10)
        
        # Action buttons
        action_frame = tk.Frame(self.root)
        action_frame.pack(pady=20)
        
        encrypt_btn = tk.Button(action_frame, text="🔒 Encrypt File", 
                               command=self.encrypt_file,
                               font=('Arial', 12, 'bold'), 
                               bg='green', fg='white', padx=30, pady=10)
        encrypt_btn.pack(side='left', padx=10)
        
        decrypt_btn = tk.Button(action_frame, text="🔓 Decrypt File", 
                               command=self.decrypt_file,
                               font=('Arial', 12, 'bold'), 
                               bg='orange', fg='white', padx=30, pady=10)
        decrypt_btn.pack(side='left', padx=10)
        
        # Status label
        self.status_label = tk.Label(self.root, text="", 
                                     font=('Arial', 10, 'italic'), 
                                     fg='gray', wraplength=550)
        self.status_label.pack(pady=10)
    
    def load_available_keys(self):
        """Load and display available keys"""
        keys = get_all_keys()
        
        if not keys:
            tk.Label(self.key_display_frame, 
                    text="⚠️ No keys available! Generate keys first.", 
                    font=('Arial', 10, 'bold'), fg='red', 
                    bg='lightyellow').pack()
            return
        
        # Create radio buttons for each key
        for i, key in enumerate(keys):
            # Truncate key display for readability
            display_key = key[:20] + "..." if len(key) > 20 else key
            
            rb = tk.Radiobutton(self.key_display_frame, 
                               text=f"Key {i}: {display_key}",
                               variable=self.selected_key_index, 
                               value=i,
                               font=('Courier', 9), 
                               bg='lightyellow')
            rb.pack(anchor='w', padx=10)
    
    def select_file(self):
        """Open file dialog to select a file"""
        filename = filedialog.askopenfilename(
            title="Select a file to encrypt/decrypt",
            filetypes=[("All files", "*.*")]
        )
        
        if filename:
            self.selected_file = filename
            self.file_label.config(text=os.path.basename(filename))
            self.status_label.config(text=f"Selected: {filename}")
    
    def key_to_fernet_key(self, secret_key):
        """Convert secret key to Fernet-compatible key"""
        # Hash the secret key to get consistent 32 bytes
        key_hash = hashlib.sha256(secret_key.encode()).digest()
        # Base64 encode for Fernet
        return base64.urlsafe_b64encode(key_hash)
    
    def encrypt_file(self):
        """Encrypt the selected file"""
        if not self.selected_file:
            messagebox.showwarning("No File", "Please select a file first!")
            return
        
        if not get_all_keys():
            messagebox.showerror("No Keys", "No encryption keys available! Generate keys first.")
            return
        
        try:
            # Get the selected key
            key_index = self.selected_key_index.get()
            secret_key = get_key_by_index(key_index)
            
            if not secret_key:
                messagebox.showerror("Error", "Could not retrieve the selected key!")
                return
            
            # Convert to Fernet key
            fernet_key = self.key_to_fernet_key(secret_key)
            fernet = Fernet(fernet_key)
            
            # Read the file
            with open(self.selected_file, 'rb') as f:
                file_data = f.read()
            
            # Encrypt the data
            encrypted_data = fernet.encrypt(file_data)
            
            # Save encrypted file
            encrypted_filename = self.selected_file + ".encrypted"
            with open(encrypted_filename, 'wb') as f:
                f.write(encrypted_data)
            
            # Save key index used for encryption
            key_info_file = self.selected_file + ".keyinfo"
            with open(key_info_file, 'w') as f:
                f.write(f"{key_index}")
            
            self.status_label.config(
                text=f"✓ File encrypted successfully!\n"
                     f"Encrypted file: {os.path.basename(encrypted_filename)}\n"
                     f"Key used: Key {key_index}",
                fg='green'
            )
            
            messagebox.showinfo("Success", 
                               f"File encrypted successfully!\n\n"
                               f"Encrypted file: {encrypted_filename}\n"
                               f"Key used: Key {key_index}")
            
            print(f"\n✓ Encrypted: {self.selected_file}")
            print(f"  Output: {encrypted_filename}")
            print(f"  Key index: {key_index}")
            
        except Exception as e:
            messagebox.showerror("Encryption Failed", f"Error: {str(e)}")
            self.status_label.config(text=f"✗ Encryption failed: {str(e)}", fg='red')
    
    def decrypt_file(self):
        """Decrypt the selected file"""
        if not self.selected_file:
            messagebox.showwarning("No File", "Please select a file first!")
            return
        
        if not get_all_keys():
            messagebox.showerror("No Keys", "No encryption keys available!")
            return
        
        try:
            # Check if it's an encrypted file
            if not self.selected_file.endswith('.encrypted'):
                response = messagebox.askyesno(
                    "File Type", 
                    "This doesn't appear to be an encrypted file. Continue anyway?"
                )
                if not response:
                    return
            
            # Try to load key info
            key_info_file = self.selected_file.replace('.encrypted', '') + '.keyinfo'
            key_index = self.selected_key_index.get()
            
            if os.path.exists(key_info_file):
                with open(key_info_file, 'r') as f:
                    saved_key_index = int(f.read().strip())
                    
                if saved_key_index != key_index:
                    response = messagebox.askyesno(
                        "Key Mismatch",
                        f"This file was encrypted with Key {saved_key_index}.\n"
                        f"You selected Key {key_index}.\n\n"
                        f"Use the correct key (Key {saved_key_index})?"
                    )
                    if response:
                        key_index = saved_key_index
                        self.selected_key_index.set(key_index)
            
            # Get the selected key
            secret_key = get_key_by_index(key_index)
            
            if not secret_key:
                messagebox.showerror("Error", "Could not retrieve the selected key!")
                return
            
            # Convert to Fernet key
            fernet_key = self.key_to_fernet_key(secret_key)
            fernet = Fernet(fernet_key)
            
            # Read the encrypted file
            with open(self.selected_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt the data
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # Save decrypted file
            if self.selected_file.endswith('.encrypted'):
                decrypted_filename = self.selected_file[:-10]  # Remove .encrypted
            else:
                decrypted_filename = self.selected_file + ".decrypted"
            
            with open(decrypted_filename, 'wb') as f:
                f.write(decrypted_data)
            
            self.status_label.config(
                text=f"✓ File decrypted successfully!\n"
                     f"Decrypted file: {os.path.basename(decrypted_filename)}\n"
                     f"Key used: Key {key_index}",
                fg='green'
            )
            
            messagebox.showinfo("Success", 
                               f"File decrypted successfully!\n\n"
                               f"Decrypted file: {decrypted_filename}\n"
                               f"Key used: Key {key_index}")
            
            print(f"\n✓ Decrypted: {self.selected_file}")
            print(f"  Output: {decrypted_filename}")
            print(f"  Key index: {key_index}")
            
        except Exception as e:
            messagebox.showerror("Decryption Failed", 
                               f"Error: {str(e)}\n\n"
                               f"Make sure you're using the correct key!")
            self.status_label.config(text=f"✗ Decryption failed: {str(e)}", fg='red')
    
    def run(self):
        self.root.mainloop()

def main():
    print("="*60)
    print("FILE ENCRYPTOR/DECRYPTOR")
    print("="*60)
    print("\nThis program encrypts and decrypts files using your saved keys.")
    print("Make sure you have generated keys first!")
    print("="*60 + "\n")
    
    app = FileEncryptorDecryptor()
    app.run()

if __name__ == "__main__":
    main()

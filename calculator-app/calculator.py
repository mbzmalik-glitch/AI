import tkinter as tk
import math

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        
        self.expression = ""
        self.base_mode = "DEC"  # DEC, HEX, BIN, OCT
        
        # Mode display
        self.mode_label = tk.Label(root, text="DEC", font=('Arial', 12), bg='lightgray')
        self.mode_label.grid(row=0, column=0, columnspan=4, sticky='ew', padx=5, pady=2)
        
        # Display
        self.display = tk.Entry(root, font=('Arial', 20), justify='right', bd=10)
        self.display.grid(row=1, column=0, columnspan=4, sticky='nsew', padx=5, pady=5)
        
        # Mode buttons
        mode_frame = tk.Frame(root)
        mode_frame.grid(row=2, column=0, columnspan=4, sticky='ew', padx=5, pady=2)
        
        modes = ['DEC', 'HEX', 'BIN', 'OCT']
        for i, mode in enumerate(modes):
            btn = tk.Button(mode_frame, text=mode, font=('Arial', 10),
                          command=lambda m=mode: self.change_base(m))
            btn.pack(side='left', expand=True, fill='both', padx=1)
        
        # Button layout
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', 'C', 'CE', '+',
            '√', '=', '%', 'A',
            'B', 'C', 'D', 'E',
            'F', 'AND', 'OR', 'XOR'
        ]
        
        # Create buttons
        row = 3
        col = 0
        for button in buttons:
            btn = tk.Button(root, text=button, font=('Arial', 14), 
                          command=lambda b=button: self.on_button_click(b))
            btn.grid(row=row, column=col, sticky='nsew', padx=2, pady=2)
            
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        # Configure grid weights for responsive layout
        for i in range(10):
            root.grid_rowconfigure(i, weight=1)
        for i in range(4):
            root.grid_columnconfigure(i, weight=1)
    
    def change_base(self, mode):
        """Change the number base mode"""
        try:
            # Convert current value to decimal first
            if self.expression and self.expression not in ['+', '-', '*', '/', '%']:
                current_val = self.get_decimal_value()
                self.base_mode = mode
                self.mode_label.config(text=mode)
                
                # Convert and display in new base
                if current_val is not None:
                    self.expression = self.convert_from_decimal(int(current_val))
                    self.display.delete(0, tk.END)
                    self.display.insert(0, self.expression)
            else:
                self.base_mode = mode
                self.mode_label.config(text=mode)
        except:
            pass
    
    def get_decimal_value(self):
        """Convert current expression value to decimal"""
        try:
            if self.base_mode == "DEC":
                return eval(self.expression)
            elif self.base_mode == "HEX":
                return int(self.expression.replace('0x', ''), 16)
            elif self.base_mode == "BIN":
                return int(self.expression.replace('0b', ''), 2)
            elif self.base_mode == "OCT":
                return int(self.expression.replace('0o', ''), 8)
        except:
            return None
    
    def convert_from_decimal(self, value):
        """Convert decimal value to current base"""
        if self.base_mode == "DEC":
            return str(value)
        elif self.base_mode == "HEX":
            return hex(value)
        elif self.base_mode == "BIN":
            return bin(value)
        elif self.base_mode == "OCT":
            return oct(value)
    
    def on_button_click(self, button):
        if button == 'C':
            self.expression = ""
            self.display.delete(0, tk.END)
        elif button == 'CE':
            self.expression = self.expression[:-1]
            self.display.delete(0, tk.END)
            self.display.insert(0, self.expression)
        elif button == '=':
            try:
                # Handle bitwise operations
                expr = self.expression
                if 'AND' in expr:
                    parts = expr.split('AND')
                    result = int(self.get_decimal_value_from_part(parts[0])) & int(self.get_decimal_value_from_part(parts[1]))
                elif 'OR' in expr:
                    parts = expr.split('OR')
                    result = int(self.get_decimal_value_from_part(parts[0])) | int(self.get_decimal_value_from_part(parts[1]))
                elif 'XOR' in expr:
                    parts = expr.split('XOR')
                    result = int(self.get_decimal_value_from_part(parts[0])) ^ int(self.get_decimal_value_from_part(parts[1]))
                else:
                    result = eval(self.expression)
                
                # Convert result to current base
                if isinstance(result, float):
                    self.expression = str(result)
                else:
                    self.expression = self.convert_from_decimal(int(result))
                
                self.display.delete(0, tk.END)
                self.display.insert(0, self.expression)
            except:
                self.display.delete(0, tk.END)
                self.display.insert(0, "Error")
                self.expression = ""
        elif button == '√':
            try:
                result = math.sqrt(float(self.get_decimal_value()))
                self.display.delete(0, tk.END)
                self.display.insert(0, str(result))
                self.expression = str(result)
            except:
                self.display.delete(0, tk.END)
                self.display.insert(0, "Error")
                self.expression = ""
        elif button in ['AND', 'OR', 'XOR']:
            self.expression += button
            self.display.delete(0, tk.END)
            self.display.insert(0, self.expression)
        elif button in ['A', 'B', 'C', 'D', 'E', 'F']:
            # Hex digits only available in HEX mode
            if self.base_mode == 'HEX':
                self.expression += button
                self.display.delete(0, tk.END)
                self.display.insert(0, self.expression)
        elif button != '':
            self.expression += button
            self.display.delete(0, tk.END)
            self.display.insert(0, self.expression)
    
    def get_decimal_value_from_part(self, part):
        """Helper to get decimal value from a part of expression"""
        try:
            return eval(part.strip())
        except:
            return 0

if __name__ == "__main__":
    root = tk.Tk()
    calculator = Calculator(root)
    root.mainloop()

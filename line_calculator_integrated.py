import matplotlib.pyplot as plt
import tkinter as tk
import math
import sys
import os

# Import the calculator from calculator-app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'calculator-app'))
from calculator import Calculator

def run_calculator_with_instructions(size, increment):
    """Run the calculator with instructions for the user"""
    root = tk.Tk()
    root.title("Step 1: Use Calculator")
    root.geometry("500x250")
    
    instructions = f"""
    CALCULATE LINES PER SET USING THE CALCULATOR
    =============================================
    
    Size: {size}
    Increment: {increment}
    
    When you click "Open Calculator", use it to compute:
    
        {size} ÷ {increment} = ?
    
    Steps:
    1. Click "Open Calculator" button below
    2. Enter {size}
    3. Click / (division)
    4. Enter {increment}
    5. Click =
    6. Remember the result!
    7. Close the calculator window
    8. Click "Continue" below
    """
    
    label = tk.Label(root, text=instructions, font=('Courier', 10), 
                    justify='left', bg='lightyellow', padx=15, pady=15)
    label.pack(pady=10, fill='both', expand=True)
    
    # Function to open calculator
    def open_calculator():
        calc_window = tk.Toplevel(root)
        calc_window.title("Programmer Calculator")
        calculator = Calculator(calc_window)
    
    # Function to continue
    def continue_program():
        root.quit()
        root.destroy()
    
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)
    
    calc_button = tk.Button(button_frame, text="Open Calculator", 
                           command=open_calculator, font=('Arial', 11), 
                           bg='blue', fg='white', padx=15, pady=8)
    calc_button.pack(side='left', padx=5)
    
    continue_button = tk.Button(button_frame, text="Continue to Results", 
                               command=continue_program, font=('Arial', 11), 
                               bg='green', fg='white', padx=15, pady=8)
    continue_button.pack(side='left', padx=5)
    
    root.mainloop()

def show_prediction_window(size, increment):
    """Show final prediction"""
    # Calculate expected lines using math
    lines_per_set = math.floor(size / increment) + 1
    total_lines = lines_per_set * 4
    
    root = tk.Tk()
    root.title("Step 2: Line Prediction Results")
    root.geometry("450x300")
    
    info_text = f"""
    LINE CALCULATION RESULTS
    ========================
    
    Size: {size}
    Increment: {increment}
    
    Mathematical calculation:
    Lines per set = floor({size}/{increment}) + 1 = {lines_per_set}
    Number of sets: 4
    
    TOTAL EXPECTED LINES: {total_lines}
    
    Formula: {lines_per_set} × 4 = {total_lines}
    
    (Did your calculator give you {size}/{increment} = {size/increment:.2f}?)
    """
    
    label = tk.Label(root, text=info_text, font=('Courier', 10), justify='left', 
                    padx=20, pady=20, bg='lightblue')
    label.pack(fill='both', expand=True)
    
    def proceed():
        root.quit()
        root.destroy()
    
    button = tk.Button(root, text="Proceed to Draw Lines", command=proceed, 
                      font=('Arial', 12), bg='darkgreen', fg='white', padx=20, pady=10)
    button.pack(pady=15)
    
    root.mainloop()
    
    return total_lines

def draw_lines(size, increment):
    """Original line drawing logic"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    
    # First set of lines
    line_count = 0
    y1 = size
    x2 = 1
    
    while y1 >= 0 and x2 <= size:
        P1 = (0, y1)
        P2 = (x2, 0)
        ax.plot([P1[0], P2[0]], [P1[1], P2[1]], color='teal', linewidth=0.5)
        
        if line_count == 0 or y1 - increment < 0 or x2 + increment > size:
            ax.plot(P1[0], P1[1], 'o', color='teal', markersize=5)
            ax.plot(P2[0], P2[1], 'o', color='teal', markersize=5)
        
        y1 -= increment
        x2 += increment
        line_count += 1
    
    print(f"Drew {line_count} lines in first set (teal)")
    
    # Second set of lines
    line_count2 = 0
    y3 = 0
    x4 = size - 1
    
    while y3 <= size and x4 >= 0:
        P3 = (size, y3)
        P4 = (x4, size)
        ax.plot([P3[0], P4[0]], [P3[1], P4[1]], color='coral', linewidth=0.5)
        
        if line_count2 == 0 or y3 + increment > size or x4 - increment < 0:
            ax.plot(P3[0], P3[1], 'o', color='coral', markersize=5)
            ax.plot(P4[0], P4[1], 'o', color='coral', markersize=5)
        
        y3 += increment
        x4 -= increment
        line_count2 += 1
    
    print(f"Drew {line_count2} lines in second set (coral)")
    
    # Third set of lines
    line_count3 = 0
    y5 = 0
    x6 = 1
    
    while y5 <= size and x6 <= size:
        P5 = (0, y5)
        P6 = (x6, size)
        ax.plot([P5[0], P6[0]], [P5[1], P6[1]], color='purple', linewidth=0.5)
        
        if line_count3 == 0 or y5 + increment > size or x6 + increment > size:
            ax.plot(P5[0], P5[1], 'o', color='purple', markersize=5)
            ax.plot(P6[0], P6[1], 'o', color='purple', markersize=5)
        
        y5 += increment
        x6 += increment
        line_count3 += 1
    
    print(f"Drew {line_count3} lines in third set (purple)")
    
    # Fourth set of lines
    line_count4 = 0
    y7 = size - 1
    x8 = size - 1
    
    while y7 >= 0 and x8 >= 0:
        P7 = (size, y7)
        P8 = (x8, 0)
        ax.plot([P7[0], P8[0]], [P7[1], P8[1]], color='gold', linewidth=0.5)
        
        if line_count4 == 0 or y7 - increment < 0 or x8 - increment < 0:
            ax.plot(P7[0], P7[1], 'o', color='gold', markersize=5)
            ax.plot(P8[0], P8[1], 'o', color='gold', markersize=5)
        
        y7 -= increment
        x8 -= increment
        line_count4 += 1
    
    print(f"Drew {line_count4} lines in fourth set (gold)")
    
    total_drawn = line_count + line_count2 + line_count3 + line_count4
    print(f"\nACTUAL TOTAL: {total_drawn} lines")
    
    # Compare with prediction
    expected = (math.floor(size / increment) + 1) * 4
    print(f"EXPECTED TOTAL: {expected} lines")
    print(f"Difference: {abs(total_drawn - expected)}")
    
    # Set axis limits
    ax.set_xlim(0, size)
    ax.set_ylim(0, size)
    ax.set_aspect('equal')
    
    # Add grid and labels
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('X Axis', fontsize=12)
    ax.set_ylabel('Y Axis', fontsize=12)
    ax.set_title(f'Lines Pattern (size={size}, increment={increment}, total={total_drawn})', 
                 fontsize=14, fontweight='bold')
    
    # Save as PNG
    filename = 'line_output.png'
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\nVisualization saved to {filename}")
    
    # Display
    plt.show()
    
    return total_drawn

def main():
    # Ask user for inputs
    size = float(input("Enter the size for the axes: "))
    increment = float(input("Enter the increment: "))
    
    print("\n" + "="*50)
    print("STEP 1: USE YOUR CALCULATOR")
    print("="*50)
    
    # Step 1: Instructions and calculator
    run_calculator_with_instructions(size, increment)
    
    print("\n" + "="*50)
    print("STEP 2: VIEW PREDICTION")
    print("="*50)
    
    # Step 2: Show prediction
    expected = show_prediction_window(size, increment)
    
    print(f"\nExpected lines: {expected}")
    print("\n" + "="*50)
    print("STEP 3: DRAWING LINES")
    print("="*50 + "\n")
    
    # Step 3: Draw the lines
    actual_lines = draw_lines(size, increment)
    
    print("\n" + "="*50)
    print("✓ PROCESS COMPLETE!")
    print("="*50)

if __name__ == "__main__":
    main()

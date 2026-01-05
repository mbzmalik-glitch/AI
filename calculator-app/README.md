# Programmer Calculator

A feature-rich calculator application with standard and programmer functionality built with Python and tkinter.

## Features

### Standard Calculator
- Basic arithmetic operations: +, -, *, /
- Square root (√)
- Modulo (%)
- Clear (C) and Clear Entry (CE/Backspace)

### Programmer Mode
- Multiple number base support:
  - **DEC** - Decimal
  - **HEX** - Hexadecimal  
  - **BIN** - Binary
  - **OCT** - Octal
- Hexadecimal digit input (A-F)
- Bitwise operations:
  - AND
  - OR
  - XOR
- Easy base conversion - switch between modes instantly

## Requirements

- Python 3.x
- tkinter (usually comes with Python)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/YOUR_USERNAME/calculator-app.git
cd calculator-app
```

2. Run the calculator:
```bash
python calculator.py
```

## Usage

### Basic Operations
1. Click number buttons (0-9) to enter numbers
2. Click operator buttons (+, -, *, /, %) for operations
3. Click = to calculate result
4. Click C to clear all or CE to delete last character

### Programmer Mode
1. Use the mode buttons (DEC, HEX, BIN, OCT) at the top to switch number bases
2. Enter a number and click a different base to convert it
3. In HEX mode, use A-F buttons for hexadecimal digits
4. Use AND, OR, XOR for bitwise operations

### Examples
- Square root: Enter `16`, click `√`, result: `4.0`
- Base conversion: Enter `255` in DEC mode, click HEX, result: `0xff`
- Bitwise AND: Enter `5`, click `AND`, enter `3`, click `=`, result: `1`

## Screenshot

The calculator features an intuitive interface with:
- Display screen showing current input/result
- Mode indicator showing current number base
- Base conversion buttons
- Standard numeric keypad and operators
- Programmer-specific buttons (A-F, AND, OR, XOR)

## License

MIT License - Feel free to use and modify!

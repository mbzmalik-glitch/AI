import matplotlib.pyplot as plt

def main():
    # Ask user for inputs
    size = float(input("Enter the size for the axes: "))
    increment = float(input("Enter the increment: "))
    
    # Create figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    
    # Draw lines in a loop
    line_count = 0
    
    # First set of lines: Start with initial values
    y1 = size
    x2 = 1
    
    while y1 >= 0 and x2 <= size:
        P1 = (0, y1)
        P2 = (x2, 0)
        
        # Draw line with same color and thinner width
        ax.plot([P1[0], P2[0]], [P1[1], P2[1]], color='teal', linewidth=0.5)
        
        # Mark the points for first and last lines
        if line_count == 0 or y1 - increment < 0 or x2 + increment > size:
            ax.plot(P1[0], P1[1], 'o', color='teal', markersize=5)
            ax.plot(P2[0], P2[1], 'o', color='teal', markersize=5)
        
        # Update for next iteration
        y1 -= increment
        x2 += increment
        line_count += 1
    
    print(f"Drew {line_count} lines in first set")
    
    # Second set of lines: Mirror pattern in top-right corner
    print(f"Increment value for second set: {increment}")
    line_count2 = 0
    
    # Start with initial values (mirroring the first pattern)
    y3 = 0
    x4 = size - 1
    
    while y3 <= size and x4 >= 0:
        P3 = (size, y3)
        P4 = (x4, size)
        
        # Draw line with same color and thinner width
        ax.plot([P3[0], P4[0]], [P3[1], P4[1]], color='coral', linewidth=0.5)
        
        # Mark the points for first and last lines
        if line_count2 == 0 or y3 + increment > size or x4 - increment < 0:
            ax.plot(P3[0], P3[1], 'o', color='coral', markersize=5)
            ax.plot(P4[0], P4[1], 'o', color='coral', markersize=5)
        
        # Update for next iteration
        y3 += increment
        x4 -= increment
        line_count2 += 1
    
    print(f"Drew {line_count2} lines in second set")
    
    # Third set of lines: Top-left corner
    print(f"Increment value for third set: {increment}")
    line_count3 = 0
    
    y5 = 0
    x6 = 1
    
    while y5 <= size and x6 <= size:
        P5 = (0, y5)
        P6 = (x6, size)
        
        # Draw line
        ax.plot([P5[0], P6[0]], [P5[1], P6[1]], color='purple', linewidth=0.5)
        
        # Mark the points for first and last lines
        if line_count3 == 0 or y5 + increment > size or x6 + increment > size:
            ax.plot(P5[0], P5[1], 'o', color='purple', markersize=5)
            ax.plot(P6[0], P6[1], 'o', color='purple', markersize=5)
        
        # Update for next iteration
        y5 += increment
        x6 += increment
        line_count3 += 1
    
    print(f"Drew {line_count3} lines in third set")
    
    # Fourth set of lines: Bottom-right corner
    print(f"Increment value for fourth set: {increment}")
    line_count4 = 0
    
    y7 = size - 1
    x8 = size - 1
    
    while y7 >= 0 and x8 >= 0:
        P7 = (size, y7)
        P8 = (x8, 0)
        
        # Draw line
        ax.plot([P7[0], P8[0]], [P7[1], P8[1]], color='gold', linewidth=0.5)
        
        # Mark the points for first and last lines
        if line_count4 == 0 or y7 - increment < 0 or x8 - increment < 0:
            ax.plot(P7[0], P7[1], 'o', color='gold', markersize=5)
            ax.plot(P8[0], P8[1], 'o', color='gold', markersize=5)
        
        # Update for next iteration
        y7 -= increment
        x8 -= increment
        line_count4 += 1
    
    print(f"Drew {line_count4} lines in fourth set")
    print(f"Total: {line_count + line_count2 + line_count3 + line_count4} lines")
    
    # Set axis limits to the size provided
    ax.set_xlim(0, size)
    ax.set_ylim(0, size)
    ax.set_aspect('equal')
    
    # Add grid and labels
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('X Axis', fontsize=12)
    ax.set_ylabel('Y Axis', fontsize=12)
    ax.set_title(f'Multiple Lines (size={size}, increment={increment})', fontsize=14, fontweight='bold')
    #ax.legend()
    
    # Save as PNG
    filename = 'line_output.png'
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\nLine visualization saved to {filename}")
    
    # Display on screen
    plt.show()

if __name__ == "__main__":
    main()

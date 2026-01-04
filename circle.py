import matplotlib.pyplot as plt
import matplotlib.patches as patches

def main():
    # Ask user for inputs
    size = float(input("Enter the size for the axes: "))
    increment = float(input("Enter the increment (radius): "))
    
    # Create figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    
    # Draw 4 circles: first at (3, 4), then increase x by 1 each time
    colors = ['blue', 'red', 'green', 'orange']
    for i in range(4):
        x_coord = 3 + i
        circle = patches.Circle((x_coord, 4), increment, fill=False, 
                               edgecolor=colors[i], linewidth=2)
        ax.add_patch(circle)
        
        # Mark the center point
        ax.plot(x_coord, 4, 'o', color=colors[i], markersize=8, 
                label=f'Center ({x_coord}, 4)')
    
    # Set axis limits to the size provided
    ax.set_xlim(0, size)
    ax.set_ylim(0, size)
    ax.set_aspect('equal')
    
    # Add grid and labels
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('X Axis', fontsize=12)
    ax.set_ylabel('Y Axis', fontsize=12)
    ax.set_title(f'4 Circles with radius {increment}', fontsize=14, fontweight='bold')
    ax.legend()
    
    # Save as PNG
    filename = 'circle_output.png'
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\nCircle visualization saved to {filename}")
    
    # Display on screen
    plt.show()

if __name__ == "__main__":
    main()


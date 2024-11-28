from PIL import Image, ImageDraw

def create_icon():
    # Create a 256x256 image with transparency
    icon_size = 256
    icon = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Define colors
    shadow_color = "#3B4252"    # Darkest - for shadow
    base_color = "#4C566A"      # Base color
    mid_color = "#D8DEE9"       # Mid tone
    highlight = "#ECEFF4"       # Lightest - for highlights
    
    # Scale factor for larger icon
    scale = 8
    
    # Draw the cloud shape with 3D effect
    # Shadow layer
    draw.ellipse([72, 136, 200, 232], fill=shadow_color)  # Bottom
    draw.ellipse([56, 104, 152, 200], fill=shadow_color)  # Middle-left
    draw.ellipse([104, 72, 216, 184], fill=shadow_color)  # Middle-right
    draw.ellipse([136, 88, 232, 184], fill=shadow_color)  # Top
    
    # Base layer
    draw.ellipse([64, 128, 192, 224], fill=base_color)    # Bottom
    draw.ellipse([48, 96, 144, 192], fill=base_color)     # Middle-left
    draw.ellipse([96, 64, 208, 176], fill=base_color)     # Middle-right
    draw.ellipse([128, 80, 224, 176], fill=base_color)    # Top
    
    # Mid-tone highlights
    draw.ellipse([72, 112, 128, 168], fill=mid_color)     # Middle-left
    draw.ellipse([112, 80, 176, 144], fill=mid_color)     # Middle-right
    draw.ellipse([144, 96, 200, 152], fill=mid_color)     # Top
    
    # Bright highlights
    draw.ellipse([80, 120, 104, 144], fill=highlight)     # Small highlight 1
    draw.ellipse([120, 88, 144, 112], fill=highlight)     # Small highlight 2
    draw.ellipse([152, 104, 176, 128], fill=highlight)    # Small highlight 3
    
    # Save as ICO file
    icon.save('app_icon.ico', format='ICO', sizes=[(256, 256)])

if __name__ == '__main__':
    create_icon()

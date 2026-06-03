from PIL import Image, ImageDraw, ImageFont
import os

# Create a simple hospital logo
def create_hospital_logo():
    # Create image with transparent background
    size = (200, 200)
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a blue circle background
    circle_color = (30, 58, 138, 255)  # Primary blue
    draw.ellipse([20, 20, 180, 180], fill=circle_color)
    
    # Draw white cross (hospital symbol)
    cross_color = (255, 255, 255, 255)
    # Vertical bar
    draw.rectangle([85, 50, 115, 150], fill=cross_color)
    # Horizontal bar
    draw.rectangle([50, 85, 150, 115], fill=cross_color)
    
    # Save the logo using absolute path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(BASE_DIR, 'static', 'assets', 'hospital_logo.png')
    os.makedirs(os.path.dirname(logo_path), exist_ok=True)
    img.save(logo_path)
    print(f"[OK] Hospital logo created at {logo_path}")

if __name__ == '__main__':
    create_hospital_logo()

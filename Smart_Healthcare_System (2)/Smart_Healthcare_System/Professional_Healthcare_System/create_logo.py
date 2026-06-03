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
    
    # Save PWA icons
    try:
        # Use Resampling if available, fallback to ANTIALIAS for older Pillow versions
        try:
            resample_method = Image.Resampling.LANCZOS
        except AttributeError:
            resample_method = Image.ANTIALIAS
            
        icon_192 = img.resize((192, 192), resample_method)
        icon_192_path = os.path.join(BASE_DIR, 'static', 'assets', 'pwa_icon_192.png')
        icon_192.save(icon_192_path)
        print(f"[OK] PWA 192x192 icon created at {icon_192_path}")

        icon_512 = img.resize((512, 512), resample_method)
        icon_512_path = os.path.join(BASE_DIR, 'static', 'assets', 'pwa_icon_512.png')
        icon_512.save(icon_512_path)
        print(f"[OK] PWA 512x512 icon created at {icon_512_path}")
    except Exception as e:
        print(f"[Error] Failed to generate PWA icons: {e}")

if __name__ == '__main__':
    create_hospital_logo()


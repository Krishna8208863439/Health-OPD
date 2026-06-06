from PIL import Image, ImageDraw

def generate_medical_icons():
    # Create static/assets directory if it doesn't exist
    import os
    os.makedirs('static/assets', exist_ok=True)
    
    # 512x512 base canvas
    size = 512
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Outer circle (clinical dark blue gradient effect / solid nice blue)
    # HSL-like blue: #0066CC (RGB: 0, 102, 204)
    padding = 24
    draw.ellipse([padding, padding, size - padding, size - padding], fill=(0, 102, 204, 255))
    
    # Inner glowing border
    border_w = 12
    draw.ellipse([padding + border_w, padding + border_w, size - padding - border_w, size - padding - border_w], 
                 outline=(40, 167, 69, 255), width=8) # green glow
    
    # Draw cross (white)
    cross_width = 70
    cross_length = 240
    cx = size // 2
    cy = size // 2
    
    # Horizontal bar
    draw.rectangle([cx - cross_length // 2, cy - cross_width // 2, cx + cross_length // 2, cy + cross_width // 2], fill=(255, 255, 255, 255))
    # Vertical bar
    draw.rectangle([cx - cross_width // 2, cy - cross_length // 2, cx + cross_width // 2, cy + cross_length // 2], fill=(255, 255, 255, 255))
    
    # Draw green details inside the cross
    detail_w = 16
    detail_l = 210
    draw.rectangle([cx - detail_l // 2, cy - detail_w // 2, cx + detail_l // 2, cy + detail_w // 2], fill=(40, 167, 69, 255))
    draw.rectangle([cx - detail_w // 2, cy - detail_l // 2, cx + detail_w // 2, cy + detail_l // 2], fill=(40, 167, 69, 255))
    
    # Save 512x512 PWA splash icon
    img.save('static/assets/icon-512.png', 'PNG')
    print("Generated static/assets/icon-512.png")
    
    # Resize and save 192x192 PWA launcher icon
    img_192 = img.resize((192, 192), Image.Resampling.LANCZOS)
    img_192.save('static/assets/icon-192.png', 'PNG')
    print("Generated static/assets/icon-192.png")
    
    # Resize and save 180x180 Apple Touch Icon
    img_180 = img.resize((180, 180), Image.Resampling.LANCZOS)
    img_180.save('static/assets/apple-touch-icon.png', 'PNG')
    print("Generated static/assets/apple-touch-icon.png")

if __name__ == '__main__':
    generate_medical_icons()

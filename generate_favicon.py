"""
Generate Favicon and Open Graph Image from Logo
Automatically generates multiple favicon sizes and OG image
"""
import os
from PIL import Image

def generate_favicon_from_logo(logo_path, output_dir='app/static'):
    """
    Generate favicon files from logo
    
    Args:
        logo_path: Path to source logo file
        output_dir: Directory to save generated files
    
    Returns:
        dict: Paths to generated files
    """
    try:
        print(f"\n📁 Reading logo from: {logo_path}")
        
        # Check if file exists
        if not os.path.exists(logo_path):
            print(f"❌ Logo file not found: {logo_path}")
            return None
        
        # Open and process logo
        img = Image.open(logo_path)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        print(f"✓ Logo loaded: {img.size[0]}x{img.size[1]} ({img.mode})")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        generated_files = {}
        
        # 1. Generate favicon.ico (32x32)
        print("\n🔨 Generating favicon files...")
        favicon_path = os.path.join(output_dir, 'favicon.ico')
        favicon = img.resize((32, 32), Image.Resampling.LANCZOS)
        favicon.save(favicon_path, format='ICO')
        generated_files['favicon'] = favicon_path
        print(f"✅ favicon.ico (32x32)")
        
        # 2. Generate PNG favicons for different sizes
        sizes = [
            (16, 'favicon-16x16.png'),
            (32, 'favicon-32x32.png'),
            (180, 'apple-touch-icon.png')  # Apple touch icon
        ]
        
        for size, filename in sizes:
            png_path = os.path.join(output_dir, filename)
            png_icon = img.resize((size, size), Image.Resampling.LANCZOS)
            png_icon.save(png_path, format='PNG')
            generated_files[f'favicon_{size}'] = png_path
            print(f"✅ {filename} ({size}x{size})")
        
        # 3. Generate Open Graph image (1200x630 - recommended size)
        print("\n🔨 Generating Open Graph image...")
        og_path = os.path.join(output_dir, 'og-image.png')
        
        # Create canvas with white background
        og_width, og_height = 1200, 630
        og_img = Image.new('RGBA', (og_width, og_height), (255, 255, 255, 255))
        
        # Calculate logo size (max 600x600, centered)
        logo_max = 600
        ratio = min(logo_max / img.width, logo_max / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        logo_resized = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Center logo on canvas
        x = (og_width - logo_resized.width) // 2
        y = (og_height - logo_resized.height) // 2
        og_img.paste(logo_resized, (x, y), logo_resized)
        
        # Convert to RGB for better compatibility
        og_img = og_img.convert('RGB')
        og_img.save(og_path, format='PNG', quality=95)
        generated_files['og_image'] = og_path
        print(f"✅ og-image.png (1200x630)")
        
        print("\n🎉 All favicon and OG images generated successfully!")
        print(f"\n📊 Generated {len(generated_files)} files:")
        for key, path in generated_files.items():
            print(f"   • {key}: {path}")
        
        return generated_files
        
    except Exception as e:
        print(f"\n❌ Error generating favicon: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def generate_from_database():
    """Generate favicon from logo in database"""
    try:
        from app import create_app, db
        from app.models import SystemSettings
        from config import Config
        
        app = create_app()
        
        with app.app_context():
            logo_filename = SystemSettings.get_setting('logo_filename', None)
            
            if not logo_filename:
                print("❌ No logo found in database.")
                print("📝 Please upload logo via Admin Settings → Logo Upload first.")
                return False
            
            # Path to uploaded logo
            logo_path = os.path.join(Config.UPLOAD_FOLDER, 'logos', logo_filename)
            
            print(f"\n🎯 M-Coder Platform - Favicon Generator")
            print(f"=" * 60)
            print(f"Logo file: {logo_filename}")
            print(f"Logo path: {logo_path}")
            
            # Generate favicons
            result = generate_favicon_from_logo(logo_path, output_dir='app/static')
            
            if result:
                print("\n📋 Next steps:")
                print("1. ✅ Favicon files generated")
                print("2. 🔄 Restart Flask app: python run_app.py")
                print("3. 🌐 Open browser: http://127.0.0.1:5000")
                print("4. 🧹 Clear browser cache (Ctrl+Shift+Delete)")
                print("5. ✓ Check browser tab for logo")
                print("6. 📱 Share link to test OG preview in WhatsApp")
                print(f"=" * 60)
                return True
            else:
                return False
                
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # Check if Pillow is installed
    try:
        from PIL import Image
    except ImportError:
        print("\n❌ Pillow library not found!")
        print("📦 Installing Pillow...")
        import subprocess
        subprocess.run(['pip', 'install', 'Pillow'], check=True)
        print("✅ Pillow installed successfully!")
    
    generate_from_database()

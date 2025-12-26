"""Quick test favicon access"""
import requests

base_url = "http://127.0.0.1:5000"

print("\n🧪 Testing Favicon Access...")
print("=" * 60)

tests = [
    ("/favicon.ico", "Favicon ICO"),
    ("/favicon-16x16.png", "Favicon 16x16"),
    ("/favicon-32x32.png", "Favicon 32x32"),
    ("/apple-touch-icon.png", "Apple Touch Icon"),
    ("/og-image.png", "Open Graph Image"),
]

for path, name in tests:
    try:
        response = requests.get(f"{base_url}{path}", timeout=5)
        status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
        size = len(response.content) if response.status_code == 200 else 0
        print(f"{status} {name:20s} - {path:25s} ({size:,} bytes)")
    except Exception as e:
        print(f"❌ ERROR {name:20s} - {str(e)}")

print("=" * 60)
print("\n📋 Next Steps:")
print("1. Open browser: http://127.0.0.1:5000")
print("2. Clear cache: Ctrl+Shift+Delete")
print("3. Check browser tab for favicon")
print("4. If still not showing, try Incognito mode")

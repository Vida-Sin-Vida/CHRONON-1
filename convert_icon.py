from PIL import Image
import os

try:
    img = Image.open("logo_trans.png")
    # Resize to standard icon sizes
    img.save("logo_trans.ico", format="ICO", sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
    print("Successfully converted logo_trans.png to logo_trans.ico")
except Exception as e:
    print(f"Error converting icon: {e}")

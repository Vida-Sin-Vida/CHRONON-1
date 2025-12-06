from PIL import Image
import sys

def convert():
    try:
        img = Image.open("logo/logo_zenodo_pro_white.png")
        img.save("logo_zenodo_v2.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
        print("Converted to logo_zenodo_v2.ico")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    convert()

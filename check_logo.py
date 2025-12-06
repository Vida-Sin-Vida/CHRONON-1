from PIL import Image
try:
    img = Image.open("logo/logo_trans.png")
    print(f"Format: {img.format}, Mode: {img.mode}")
    if img.mode == 'RGBA':
        print("Alpha channel present.")
        # Check corner pixel alpha
        print(f"Pixel (0,0): {img.getpixel((0,0))}")
    else:
        print("No alpha channel.")
except Exception as e:
    print(e)

from PIL import Image
import numpy as np

def make_transparent():
    try:
        img = Image.open("logo/logo_trans.png").convert("RGBA")
        datas = img.getdata()
        
        # Get background color from top-left
        bg_color = datas[0] # (R, G, B, A)
        print(f"Detected Background Color: {bg_color}")
        
        tolerance = 30 # Allow slight variance for JPEG compression artifacts
        newData = []
        
        bg_r, bg_g, bg_b, _ = bg_color
        
        for item in datas:
            # Check if pixel is close to background color
            if (abs(item[0] - bg_r) < tolerance and 
                abs(item[1] - bg_g) < tolerance and 
                abs(item[2] - bg_b) < tolerance):
                newData.append((255, 255, 255, 0)) # Transparent
            else:
                newData.append(item)
                
        img.putdata(newData)
        img.save("logo/logo_sidebar.png", "PNG")
        print("Saved transparent logo to logo/logo_sidebar.png")
        
        # Also update ICO
        img.save("logo_original.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64)])
        print("Updated logo_original.ico")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    make_transparent()

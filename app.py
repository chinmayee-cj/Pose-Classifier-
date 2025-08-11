import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import requests
from io import BytesIO
import subprocess, sys, os, signal

process = None

def start_inference():
    global process
    if process is None:
        process = subprocess.Popen([sys.executable, "inference.py"])
        draw_glass_button("Stop", stop_inference)

def stop_inference():
    global process
    if process:
        if os.name == 'nt':
            process.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            process.terminate()
        process = None
        draw_glass_button("Start", start_inference)

root = tk.Tk()
root.title("Yoga Asana Classifier")
root.geometry("900x600")

# Load background
url = "https://images.squarespace-cdn.com/content/v1/5e0fb198de7ce9381aea16be/1603694286070-SN47XDN1MIVAZXCK0BL1/yoga03.jpg"
bg_img = Image.open(BytesIO(requests.get(url).content)).resize((900, 600))

# Darken background with semi-transparent black overlay
dark_overlay = Image.new("RGBA", bg_img.size, (0, 0, 0, 100))  # 100/255 alpha
bg_img = Image.alpha_composite(bg_img.convert("RGBA"), dark_overlay)
bg_tk = ImageTk.PhotoImage(bg_img)

# Canvas for layering
canvas = tk.Canvas(root, width=900, height=600, highlightthickness=0)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_tk, anchor="nw")

# Add heading directly onto canvas
canvas.create_text(450, 80, text="Yoga Asana Classifier", fill="white",
                   font=("Helvetica", 36, "bold"))

# Function to create frosted glass button with orange tint
def draw_glass_button(text, command):
    # Crop area behind button from background
    x0, y0, w, h = 350, 220, 200, 60  # y0 moved up from 250 to 220
    crop = bg_img.crop((x0, y0, x0 + w, y0 + h))
    # Apply blur
    glass = crop.filter(ImageFilter.GaussianBlur(5))
    # Apply semi-transparent orange overlay
    overlay = Image.new("RGBA", glass.size, (255, 140, 0, 120))  # orange with alpha
    glass = Image.alpha_composite(glass.convert("RGBA"), overlay)
    # Round corners
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, w, h), radius=20, fill=255)
    glass.putalpha(mask)
    glass_tk = ImageTk.PhotoImage(glass)

    # Create button image and bind clicks
    btn_img = canvas.create_image(x0, y0, image=glass_tk, anchor="nw")
    btn_text = canvas.create_text(x0 + w/2, y0 + h/2, text=text,
                                  font=("Helvetica", 18, "bold"), fill="white")
    canvas.tag_bind(btn_img, "<Button-1>", lambda e: command())
    canvas.tag_bind(btn_text, "<Button-1>", lambda e: command())
    canvas.image_refs = [glass_tk]  # prevent GC

draw_glass_button("Start", start_inference)

root.mainloop()

import streamlit as st
from neopixel_control import set_all_leds, set_brightness
import glob
import os
from PIL import Image

st.title("LED Strip Controller + Latest Camera Image")

# LED control sliders
r = st.slider("Red", 0, 255, 0)
g = st.slider("Green", 0, 255, 0)
b = st.slider("Blue", 0, 255, 0)
brightness = st.slider("Brightness", 0, 255, 65)

if st.button("Apply LED Settings"):
    set_brightness(brightness)
    set_all_leds(r, g, b)
    st.success(f"Set color to RGB({r},{g},{b}) with brightness {brightness}")

# Load latest camera image
image_folder = "/app/images/usb_cam_0"

def get_latest_image(folder):
    files = glob.glob(os.path.join(folder, "*.jpg"))
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    return latest_file

latest_img = get_latest_image(image_folder)
if latest_img:
    image = Image.open(latest_img)
    st.image(image, caption="Latest camera image", use_column_width=True)
else:
    st.warning("No images found yet.")

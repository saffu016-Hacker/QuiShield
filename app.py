import streamlit as st
from PIL import Image
import cv2
import numpy as np
import requests

st.set_page_config(page_title="QuiShield")

# --- TITLE - SIMPLE NO HTML ---
st.title("🛡️ QuiShield")
st.write("Single QR Deep Scanner - Detects Real & Fake Links")

def read_single_qr(pil_img):
    img = np.array(pil_img.convert("RGB"))
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(img)
    return data

def get_final_link(url):
    try:
        if not url.startswith("http"):
            return url, False
        r = requests.get(url, timeout=4, allow_redirects=True)
        if r.url != url:
            return r.url, True
        return url, False
    except:
        return url, False

# --- SINGLE UPLOAD ---
file = st.file_uploader("Upload ONE QR to Scan", type=["png","jpg","jpeg"])

if file:
    pil_img = Image.open(file)
    st.image(pil_img, width=300)
    
    raw_data = read_single_qr(pil_img)

    if raw_data == "":
        st.error("No QR found - Upload clear image")
    else:
        st.code(raw_data, language="text")

        # --- VERIFICATION - YOUR POINT ---
        dl = raw_data.lower()

        # Type check
        if "@ybl" in dl or "upi://" in dl:
            st.info("💳 Type: Payment QR (UPI) - @ybl found")
        elif dl.startswith("http"):
            st.info("🌐 Type: Website Link")

        # http vs https
        if dl.startswith("http://"):
            st.error("🚨 http = Not Safe (no security)")
        if dl.startswith("https://"):
            st.success("✅ https = Secure")

        # @ in link
        if "@" in dl and "http" in dl and "@ybl" not in dl:
            st.warning("⚠️ Contains @ in link = Suspicious (fake login trick)")

        # Redirect check - your generator point
        if dl.startswith("http"):
            final_url, is_redirect = get_final_link(raw_data)
            if is_redirect:
                st.warning(f"🔍 This QR redirects! Generator link found")
                st.write(f"Original: {raw_data}")
                st.write(f"Real Final Link: {final_url}")
                if "http://" in final_url:
                    st.error("🚨 Final link is http = Dangerous!")
            else:
                st.write(f"Final Link (no redirect): {final_url}")

        # Final verdict
        if "http://" in dl or ("@" in dl and "http" in dl):
            st.error("FINAL VERDICT: DANGEROUS / FAKE")
        elif is_redirect if 'is_redirect' in locals() else False:
            st.warning("FINAL VERDICT: SUSPICIOUS - Check final link")
        else:
            st.success("FINAL VERDICT: SAFE")
else:
    st.info("Upload a QR image - Only ONE at a time")
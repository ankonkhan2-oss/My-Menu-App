import streamlit as st
import google.generativeai as genai
import json
import pandas as pd  # স্প্রেডশিট ফরম্যাটের জন্য
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Menu OCR Tool", layout="wide")
st.title("🍽️ Smart Restaurant Menu Extractor")
st.write("আপনার মেনুর ছবি আপলোড করুন এবং শর্ত অনুযায়ী সাজানো ডেটা সরাসরি স্প্রেডশিটে নিয়ে যান!")

api_key = st.text_input("আপনার Gemini API Key দিন:", type="password")
uploaded_file = st.file_uploader("মেনুর ছবি আপলোড করুন", type=["jpg", "jpeg", "png"])

if st.button("Extract & Export Data"):
    if not api_key or not uploaded_file:
        st.error("API Key এবং ছবি দুটোই প্রয়োজন!")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            image = Image.open(uploaded_file)
            
            with st.spinner("ডেটা প্রসেস হচ্ছে..."):
                prompt = """
                Extract menu data strictly into a JSON array of objects.
                COLUMNS: "Item Type", "Category", "Item", "Price (Cents)".
                RULES:
                1. Main Dish first, then Appetizers, Soups, etc.
                2. Combine Item Name + Size for options (e.g. "Wonton Soup (Pt.)").
                3. Split 'or' items into two rows.
                4. Convert prices to cents.
                Return ONLY JSON.
                """
                response = model.generate_content([image, prompt])
                json_text = response.text.strip().replace("```json", "").replace("```", "").strip()
                menu_data = json.loads(json_text)
                
                # ডেটাকে Pandas DataFrame-এ রূপান্তর (যাতে কপি/ডাউনলোড সহজ হয়)
                df = pd.DataFrame(menu_data)
                
                st.success("সফলভাবে ডেটা এক্সট্র্যাক্ট করা হয়েছে!")
                
                # ১. স্ক্রিনে টেবিল দেখানো
                st.dataframe(df, use_container_width=True)
                
                # ২. Google Spreadsheet-এ নেওয়ার জন্য CSV ডাউনলোড বাটন
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download for Google Sheets (CSV)",
                    data=csv,
                    file_name='menu_data.csv',
                    mime='text/csv',
                )
                st.info("উপরের বাটন থেকে ফাইলটি ডাউনলোড করে সরাসরি Google Sheets-এ 'Import' করতে পারবেন।")

        except Exception as e:
            st.error(f"Error: {e}")

import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
from PIL import Image

# UI Setup
st.set_page_config(page_title="Menu OCR Tool", layout="wide")
st.title("🍽️ Smart Restaurant Menu Extractor")

api_key = st.text_input("আপনার Gemini API Key দিন:", type="password")
uploaded_file = st.file_uploader("মেনুর ছবি আপলোড করুন", type=["jpg", "jpeg", "png"])

if st.button("Extract & Format Data"):
    if not api_key or not uploaded_file:
        st.error("API Key এবং ছবি দুটোই দিন!")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            image = Image.open(uploaded_file)
            
            with st.spinner("ডেটা প্রসেস হচ্ছে... অনুগ্রহ করে ১০-১৫ সেকেন্ড অপেক্ষা করুন।"):
                # প্রম্পটটি আরও সহজবোধ্য করা হয়েছে যাতে AI দ্রুত রেসপন্স দেয়
                prompt = """
                Read the menu image and extract data as a JSON array.
                FORMAT: [{"Item Type": "...", "Category": "...", "Item": "...", "Price (Cents)": ...}]

                REQUIRED LOGIC:
                1. Item Type: "Item" for main dish, "Option" for sizes/variations.
                2. Category: Section name from the menu.
                3. Item Name: Include the serial number if present (e.g., "1. Egg Roll").
                4. Split 'or' / '/': If an item is "1. Chicken or Pork Lo Mein", create TWO rows: 
                   - Row 1: "1. Chicken Lo Mein"
                   - Row 2: "1. Pork Lo Mein"
                5. Prices: Convert to cents ($2.00 -> 200).
                6. Options: Combine name and size: "13. Wonton Soup (Pt.)".

                Ensure no data is skipped. Return ONLY the JSON array.
                """
                response = model.generate_content([image, prompt])
                
                # Cleaning JSON text
                clean_text = response.text.strip().replace("```json", "").replace("```", "").strip()
                menu_data = json.loads(clean_text)
                
                # Result Processing
                df = pd.DataFrame(menu_data)
                cols = ["Item Type", "Category", "Item", "Price (Cents)"]
                df = df[cols] # Re-order columns

                st.success("সফলভাবে ডেটা এক্সট্র্যাক্ট করা হয়েছে!")
                st.dataframe(df, use_container_width=True)
                
                # Download Button
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download for Google Sheets (CSV)",
                    data=csv,
                    file_name='menu_final_output.csv',
                    mime='text/csv',
                )

        except Exception as e:
            st.error(f"কোথাও একটি সমস্যা হয়েছে। এররটি হলো: {e}")
            st.info("টিপস: যদি বারবার লোডিং দেখায়, তবে কিছুক্ষণ পর আবার চেষ্টা করুন বা ছবিটির সাইজ ছোট করে দেখুন।")

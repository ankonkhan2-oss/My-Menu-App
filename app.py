import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
from PIL import Image

st.set_page_config(page_title="Menu OCR Tool", layout="wide")
st.title("🍽️ Smart Restaurant Menu Extractor")
st.write("নিখুঁতভাবে সিরিয়াল নম্বরসহ মেনু ডেটা স্প্রেডশিটে নিয়ে যান!")

api_key = st.text_input("আপনার Gemini API Key দিন:", type="password")
uploaded_file = st.file_uploader("মেনুর ছবি আপলোড করুন", type=["jpg", "jpeg", "png"])

if st.button("Extract & Export Data"):
    if not api_key or not uploaded_file:
        st.error("API Key এবং ছবি দুটোই দিন!")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            image = Image.open(uploaded_file)
            
            with st.spinner("ডেটা স্প্লিট করা হচ্ছে এবং সিরিয়াল নম্বর যাচাই করা হচ্ছে..."):
                prompt = """
                Extract menu data into a JSON array. 
                Each object MUST have: "Item Type", "Category", "Item", "Price (Cents)".

                STRICT SPLITTING & SERIAL RULES:
                1. Split 'or' / '/': If an item is "1. Egg Roll or Vegetable Roll", you MUST create TWO separate rows:
                   - Row 1: Item: "1. Egg Roll", Price: 200
                   - Row 2: Item: "1. Vegetable Roll", Price: 200
                2. Serial Numbers: If the menu shows "5. Chicken Chow Mein", the "Item" column MUST be "5. Chicken Chow Mein". Never skip the number.
                3. Item Type: Use "Item" for main foods and "Option" for sizes (Pt., Qt., etc.).
                4. Category: Use the section name (e.g., Appetizers, Soup). Do NOT put this in "Item Type".
                5. Options: For sizes, merge name: "13. Wonton Soup (Pt.)".

                Order: Main Dish, Appetizers, Soups, then others.
                Return ONLY a JSON array.
                """
                response = model.generate_content([image, prompt])
                json_text = response.text.strip().replace("```json", "").replace("```", "").strip()
                menu_data = json.loads(json_text)
                
                df = pd.DataFrame(menu_data)
                
                # Column order fix
                cols = ["Item Type", "Category", "Item", "Price (Cents)"]
                df = df[cols] 

                st.success("সফলভাবে ডেটা এক্সট্র্যাক্ট এবং স্প্লিট করা হয়েছে!")
                st.dataframe(df, use_container_width=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download for Google Sheets (CSV)",
                    data=csv,
                    file_name='menu_split_fixed.csv',
                    mime='text/csv',
                )

        except Exception as e:
            st.error(f"Error: {e}")

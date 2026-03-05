import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
from PIL import Image

st.set_page_config(page_title="Menu OCR Tool", layout="wide")
st.title("🍽️ Smart Restaurant Menu Extractor")
st.write("Apnar menu-r chhobi upload korun ebong nikhut bhabe sajano data spreadsheet-e niye jan!")

api_key = st.text_input("Apnar Gemini API Key din:", type="password")
uploaded_file = st.file_uploader("Menu-r chhobi upload korun", type=["jpg", "jpeg", "png"])

if st.button("Extract & Export Data"):
    if not api_key or not uploaded_file:
        st.error("API Key ebong chhobi duto-i din!")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            image = Image.open(uploaded_file)
            
            with st.spinner("Serial number o column thik kora hochche..."):
                prompt = """
                Extract menu data into a JSON array. 
                Each object MUST have exactly these 4 keys: "Item Type", "Category", "Item", "Price (Cents)".

                STRICT FORMATTING RULES:
                1. "Item Type": Only "Item" (for main food) or "Option" (for size/variation).
                2. "Category": The menu section name.
                3. "Item": IMPORTANT! If a serial number (like 1, 2, 89) exists before the food name in the image, you MUST include it (e.g., "1. Egg Roll", "89. General Tso's Chicken"). If it's an option, add size: "13. Wonton Soup (Pt.)".
                4. "Price (Cents)": Convert to cents.

                EXTRA RULES:
                - Maintain order: Main Dish first, then Appetizers, then others.
                - Never swap Category with Item Type.
                - Keep serial numbers exactly as they appear on the menu.

                Return ONLY a JSON array.
                """
                response = model.generate_content([image, prompt])
                json_text = response.text.strip().replace("```json", "").replace("```", "").strip()
                menu_data = json.loads(json_text)
                
                df = pd.DataFrame(menu_data)
                
                # Column sequence fix
                cols = ["Item Type", "Category", "Item", "Price (Cents)"]
                df = df[cols] 

                st.success("Successfully data extract kora hoyeche!")
                st.dataframe(df, use_container_width=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download for Google Sheets (CSV)",
                    data=csv,
                    file_name='menu_fixed_final.csv',
                    mime='text/csv',
                )

        except Exception as e:
            st.error(f"Error: {e}")

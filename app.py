import streamlit as st
import google.generativeai as genai
import json
from PIL import Image

# ওয়েবসাইটের ডিজাইন ও টাইটেল
st.set_page_config(page_title="Menu OCR Tool", layout="wide")
st.title("🍽️ Smart Restaurant Menu Extractor")
st.write("আপনার মেনুর ছবি আপলোড করুন এবং ১১টি শর্ত অনুযায়ী সাজানো ডেটা পেয়ে যান!")

# ইউজারের কাছ থেকে API Key নেওয়ার বক্স (যাতে আপনার কোড নিরাপদ থাকে)
api_key = st.text_input("আপনার Gemini API Key দিন (Security-র জন্য):", type="password")

# ছবি আপলোড করার অপশন
uploaded_file = st.file_uploader("মেনুর ছবি আপলোড করুন (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

if st.button("Extract Menu Data"):
    if not api_key:
        st.error("দয়া করে প্রথমে আপনার API Key দিন!")
    elif not uploaded_file:
        st.error("দয়া করে একটি ছবি আপলোড করুন!")
    else:
        try:
            # মডেল রেডি করা
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # ছবি পড়া
            image = Image.open(uploaded_file)
            
            with st.spinner("এআই আপনার মেনু স্ক্যান করছে এবং শর্তগুলো মেলাচ্ছে... দয়া করে অপেক্ষা করুন।"):
                # ১১টি কন্ডিশন সহ প্রম্পট
                prompt = """
                You are an expert menu data extractor. Extract data strictly into a flat JSON array.
                RULES:
                1. 4-column table data: "Item Type", "Category", "Item", "Price (Cents)".
                2. Categories: "Main Dish" first (like Chef's Specialties, Combination Plates), then "Appetizers", "Salads", "Soups", then the rest.
                3 & 10. Options/Sizes: If an item has sizes (e.g., Pt., Qt., Sm., Lg.), create separate items combining the name and size, e.g., "13. Wonton Soup (Pt.)".
                4. Split 'or' / '/': e.g., "Chicken or Shrimp Noodles" -> two separate items.
                5. Convert ALL prices to cents (e.g., $10.25 -> 1025).
                6 & 7. Serials: Keep if they exist (with dot), do not add if missing.
                8. Item Type: "Item" for regular items, "Option" for variations/sizes.
                9. 100% spelling and price accuracy.
                
                Return ONLY a JSON array of objects. Example:
                [
                  {"Item Type": "Item", "Category": "Appetizers", "Item": "1. Egg Roll", "Price": 200},
                  {"Item Type": "Option", "Category": "Soup", "Item": "13. Wonton Soup (Pt.)", "Price": 375}
                ]
                """
                response = model.generate_content([image, prompt])
                
                # JSON ডাটা ক্লিন করা
                json_text = response.text.strip().replace("```json", "").replace("```", "").strip()
                menu_data = json.loads(json_text)
                
                st.success("সফলভাবে ডাটা বের করা হয়েছে!")
                
                # সুন্দর টেবিল আকারে দেখানো
                st.table(menu_data)
                
        except Exception as e:
            st.error(f"কোথাও একটি সমস্যা হয়েছে: {e}")
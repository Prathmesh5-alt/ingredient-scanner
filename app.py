import streamlit as st
from paddleocr import PaddleOCR
import cv2
import numpy as np

# Set the page configuration with a wide layout
st.set_page_config(page_title="Ingredient Scanner", layout="wide")

# Initialize PaddleOCR
ocr = PaddleOCR(lang='en')

# Cache the OCR results to avoid re-processing
#@st.experimental_memo
def perform_ocr(img):
    # Perform OCR using PaddleOCR
    result = ocr.ocr(img)
    return result

# Define a function to highlight specific words in an image
def highlight_specific_words(image, boxes, texts, target_words, color=(255, 0, 0), thickness=3):
    for box, text in zip(boxes, texts):
        if any(word.lower() in text.lower() for word in target_words):
            word_box = [tuple(map(int, point)) for point in box]
            cv2.polylines(image, [np.array(word_box)], isClosed=True, color=color, thickness=thickness)
    return image

# Define a function to check if the ingredient list meets dietary preferences
def check_dietary_preferences(ingredients, preferences):
    problematic_words = []
    
    keywords = {
        'Gluten-Free': ['wheat', 'barley', 'rye', 'oats'],
        'Lactose Intolerant': ['milk', 'lactose', 'cheese', 'butter', 'cream'],
        'Nut Allergies': ['nut', 'almond', 'walnut', 'peanut'],
        'Shellfish Allergy': ['shrimp', 'crab', 'lobster', 'shellfish'],
        'Egg Allergy': ['egg', 'eggs'],
        'Soy Allergy': ['soy', 'tofu', 'soy sauce'],
        'Dairy Allergy': ['milk', 'dairy', 'cheese', 'butter'],
        'Vegetarian': ['meat', 'chicken', 'fish', 'pork'],
        'Vegan': ['meat', 'dairy', 'eggs', 'honey'],
        'FODMAPs Intolerance': ['onion', 'garlic', 'wheat', 'legumes'],
        'Paleo': ['grains', 'legumes', 'dairy', 'processed'],
        'Keto': ['sugar', 'bread', 'pasta', 'rice'],
    }

    for preference in preferences:
        if preference in keywords:
            problematic_words.extend([word for word in keywords[preference] if any(word in ingredient.lower() for ingredient in ingredients)])
    
    return len(problematic_words) == 0, problematic_words

# Custom CSS for a darker theme
st.markdown("""
    <style>
    /* Main background color */
    .main {
        background-color: #1e1e1e;
        padding: 10px;
    }

    /* Text color and style */
    .stTextInput>div>div>input {
        background-color: #2c2c2c;
        color: #f1f1f1;
        border-radius: 10px;
        font-size: 18px;
    }

    /* Button styling */
    .stButton>button {
        background-color: #4caf50;
        color: white;
        border-radius: 10px;
        padding: 10px;
        font-size: 16px;
    }

    .stButton>button:hover {
        background-color: #45a049;
    }

    /* Checkbox styling */
    .st-checkbox-label {
        font-size: 18px;
        color: #dcdcdc;
    }

    /* Image border */
    .stImage>img {
        border-radius: 15px;
        border: 3px solid #4caf50;
    }

    /* Success and error messages */
    .stAlert {
        background-color: #333;
        color: #f1f1f1;
        border-left: 6px solid #4caf50;
    }

    .stAlert-error {
        background-color: #333;
        border-left: 6px solid #ff6347;
    }
    </style>
    """, unsafe_allow_html=True)

# Streamlit app layout improvements
st.title("🍽️ Ingredient Scanner for Dietary Preferences")

st.markdown("""
    Welcome to the **Ingredient Scanner**! Use this tool to quickly check if a product meets your dietary restrictions. 
    Just select your preferences, scan the ingredient list, and let the app do the rest.
    """)

# User dietary preferences
st.subheader("Step 1: Select Your Dietary Restrictions")
st.markdown("Check the boxes below to select dietary restrictions that apply to you:")

# Create 2 columns to arrange checkboxes neatly
col1, col2 = st.columns(2)

preferences = []
with col1:
    if st.checkbox('Gluten-Free'):
        preferences.append('Gluten-Free')
    if st.checkbox('Lactose Intolerant'):
        preferences.append('Lactose Intolerant')
    if st.checkbox('Nut Allergies'):
        preferences.append('Nut Allergies')
    if st.checkbox('Shellfish Allergy'):
        preferences.append('Shellfish Allergy')
    if st.checkbox('Egg Allergy'):
        preferences.append('Egg Allergy')

with col2:
    if st.checkbox('Soy Allergy'):
        preferences.append('Soy Allergy')
    if st.checkbox('Dairy Allergy'):
        preferences.append('Dairy Allergy')
    if st.checkbox('Vegetarian'):
        preferences.append('Vegetarian')
    if st.checkbox('Vegan'):
        preferences.append('Vegan')
    if st.checkbox('FODMAPs Intolerance'):
        preferences.append('FODMAPs Intolerance')
    if st.checkbox('Paleo'):
        preferences.append('Paleo')
    if st.checkbox('Keto'):
        preferences.append('Keto')

if preferences:
    st.markdown("### Step 2: Scan the Ingredient List")
    
    # Camera input with placeholder
    camera_image = st.camera_input("📷 Take a picture of the ingredient list")

    if camera_image is not None:
        # Process image button
        if st.button("Process Image"):
            # Read the image from the camera input
            image = np.array(bytearray(camera_image.read()), dtype=np.uint8)
            img = cv2.imdecode(image, cv2.IMREAD_COLOR)
            img = cv2.cvtColor(img, cv2

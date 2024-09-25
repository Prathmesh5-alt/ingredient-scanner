import streamlit as st
from paddleocr import PaddleOCR
import cv2
import numpy as np

# Initialize PaddleOCR
ocr = PaddleOCR(lang='en')

# Cache the OCR results to avoid re-processing
@st.experimental_memo
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

# Streamlit app
st.set_page_config(page_title="Ingredient Scanner", layout="wide")
st.title("🍽️ Ingredient Scanner for Dietary Preferences")
st.markdown("""
    This app helps you check if a product meets your dietary restrictions. 
    Select your preferences below and scan the ingredient list!
""")

# User dietary preferences
st.subheader("Select Your Dietary Restrictions:")
preferences_options = [
    'Gluten-Free',
    'Lactose Intolerant',
    'Nut Allergies',
    'Shellfish Allergy',
    'Egg Allergy',
    'Soy Allergy',
    'Dairy Allergy',
    'Vegetarian',
    'Vegan',
    'FODMAPs Intolerance',
    'Paleo',
    'Keto'
]

# Get user-selected preferences
preferences = []
for option in preferences_options:
    if st.checkbox(option):
        preferences.append(option)

if preferences:
    st.markdown("### Now scan the ingredient list:")
    
    # Camera input
    camera_image = st.camera_input("📷 Click to take a picture")

    if camera_image is not None:
        # Only process the image when preferences and camera input are ready
        if st.button("Process Image"):
            # Read the image from the camera input
            image = np.array(bytearray(camera_image.read()), dtype=np.uint8)
            img = cv2.imdecode(image, cv2.IMREAD_COLOR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Perform OCR and cache the result
            result = perform_ocr(img)
            
            if not result or not result[0]:  # Check if OCR detected any text
                st.error("❌ Please provide a clear image of the ingredient list.")
            else:
                boxes = [res[0] for res in result[0]]
                texts = [res[1][0] for res in result[0]]

                # Check if the ingredients meet the preferences and get problematic words
                is_acceptable, problematic_words = check_dietary_preferences(texts, preferences)
                
                # Highlight problematic words
                highlighted_img = highlight_specific_words(img, boxes, texts, problematic_words)
                
                # Display the image with bounding boxes
                st.image(highlighted_img, caption='Highlighted Ingredients', use_column_width=True)
                
                # Display ingredient text and preference result
                if is_acceptable:
                    st.success("✅ The product is suitable for your dietary preferences.")
                else:
                    st.error("❌ The product is NOT suitable for your dietary preferences.")
                    st.write(f"**Problematic ingredients:** {', '.join(problematic_words)}")
else:
    st.warning("⚠️ Please select at least one dietary restriction before scanning.")

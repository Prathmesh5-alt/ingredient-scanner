import streamlit as st
from paddleocr import PaddleOCR
import cv2
import numpy as np
import base64
import json
import os

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Scan&Shop", layout="wide")

# ---------- LOAD LOCAL BACKGROUND IMAGE ----------
def add_blurred_bg(image_path):
    with open(image_path, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()
    css = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        position: relative;
    }}
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        backdrop-filter: blur(10px);
        background: rgba(0, 0, 0, 0.55);
        z-index: 0;
    }}
    [data-testid="stAppViewContainer"] > div:first-child {{
        position: relative;
        z-index: 1;
    }}
    .main-heading {{
        font-size: 48px;
        font-weight: 800;
        text-align: center;
        margin-top: 10px;
        color: #A7FFEB;
        text-shadow: 3px 3px 12px rgba(0,0,0,0.9);
        animation: glow 3s ease-in-out infinite alternate;
    }}
    @keyframes glow {{
        from {{
            text-shadow: 0 0 10px #00FFAA, 0 0 20px #00FFAA, 0 0 30px #00FFAA;
        }}
        to {{
            text-shadow: 0 0 20px #00FFFF, 0 0 30px #00FFFF, 0 0 40px #00FFFF;
        }}
    }}
    .marquee {{
        width: 100%;
        overflow: hidden;
        white-space: nowrap;
        border-bottom: 2px solid #4CAF50;
        padding: 8px;
        margin-bottom: 20px;
        color: #00FF88;
        font-size: 24px;
        font-family: 'Courier New', monospace;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.8);
        animation: marquee 25s linear infinite;
    }}
    @keyframes marquee {{
        0% {{ transform: translateX(100%); }}
        100% {{ transform: translateX(-100%); }}
    }}
    .stButton>button {{
        background: grey;
        color: black;
        border-radius: 12px;
        font-weight: 600;
        border: none;
        padding: 10px 25px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        transform: scale(1.05);
        background: #bdbdbd;
        color: black;
    }}
    input[type="text"], input[type="password"] {{
        width: 45% !important;
        margin: 10px auto !important;
        display: block !important;
        padding: 10px 15px !important;
        background-color: #d9d9d9 !important;
        border-radius: 8px !important;
        border: 1px solid #aaa !important;
        color: #000 !important;
        font-size: 16px !important;
    }}
    h1, h2, h3, label, p, span {{
        color: #E8FFE8 !important;
        text-shadow: 1px 1px 5px rgba(0,0,0,0.9);
    }}
    .highlight {{
        font-size: 22px;
        font-weight: 600;
        color: #00FFB9;
        text-shadow: 0px 0px 10px #00FFB9;
    }}
    [data-testid="stSidebar"] {{
        background-color: rgba(0, 0, 0, 0.8);
        color: white;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

add_blurred_bg(r"C:\Users\varad\Desktop\ingredient-scanner1\foods_bg.jpg")

# ---------- FLOATING FOOD EMOJIS ----------
def add_floating_foods():
    st.markdown("""
    <style>
    .floating-food {
        position: absolute;
        font-size: 40px;
        opacity: 0.9;
        animation: float 12s ease-in-out infinite;
        z-index: 0;
    }
    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); opacity: 1; }
        50% { transform: translateY(-50px) rotate(20deg); opacity: 0.8; }
        100% { transform: translateY(0px) rotate(0deg); opacity: 1; }
    }
    .food1 { top: 20%; left: 10%; animation-delay: 0s; }
    .food2 { top: 50%; left: 80%; animation-delay: 2s; }
    .food3 { top: 70%; left: 30%; animation-delay: 4s; }
    .food4 { top: 40%; left: 60%; animation-delay: 6s; }
    .food5 { top: 25%; left: 75%; animation-delay: 8s; }
    </style>
    <div class="floating-food food1">🍎</div>
    <div class="floating-food food2">🍌</div>
    <div class="floating-food food3">🥦</div>
    <div class="floating-food food4">🍓</div>
    <div class="floating-food food5">🥕</div>
    """, unsafe_allow_html=True)

add_floating_foods()

# ---------- MAIN HEADING ----------
st.markdown("<div class='main-heading'>🍏 Scan&Shop — AI Ingredient Scanner</div>", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "users" not in st.session_state:
    st.session_state.users = {"demo@example.com": "1234"}
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ---------- AUTH FUNCTIONS ----------
def login(email, password):
    users = st.session_state.users
    if email in users and users[email] == password:
        st.session_state.authenticated = True
        st.success("✅ Login successful!")
        st.rerun()
    else:
        st.error("❌ Invalid credentials.")

def signup(email, password):
    users = st.session_state.users
    if email in users:
        st.warning("⚠️ User already exists. Please log in.")
    else:
        users[email] = password
        st.success("✅ Signup successful! Please log in.")

def logout():
    st.session_state.authenticated = False
    st.rerun()

# ---------- ALLERGEN DATA (MERGED JSON) ----------
allergen_data = {
    # Major Allergens (with hidden / alternative names)
    "milk": ["milk", "cow's milk", "whole milk", "skim milk", "lactose", "whey", "casein", "buttermilk", "butterfat", "cream", "cheese", "yogurt"],
    "egg": ["egg", "eggs", "egg white", "egg yolk", "albumin", "ovalbumin", "lysozyme", "egg protein"],
    "peanut": ["peanut", "peanuts", "groundnut", "arachis oil", "peanut butter", "peanut flour"],
    "tree_nut": ["almond", "walnut", "cashew", "hazelnut", "pecan", "pistachio", "brazil nut", "macadamia", "tree nuts", "nut oils"],
    "soy": ["soy", "soya", "soybean", "soy protein", "soy lecithin", "tofu", "edamame", "soya sauce"],
    "wheat_gluten": ["wheat", "barley", "rye", "malt", "malt extract", "triticale", "wheat starch", "hydrolyzed wheat protein", "gluten"],
    "fish": ["fish", "salmon", "tuna", "cod", "haddock", "anchovy", "bass", "trout", "fish oil"],
    "shellfish": ["shellfish", "shrimp", "prawn", "crab", "lobster", "scallop", "mollusc", "molluscs", "clam", "oyster"],
    "sesame": ["sesame", "sesame seed", "sesame oil", "tahini", "benne seed", "gingelly", "sesamol"],
    "mustard": ["mustard", "mustard seed", "mustard flour", "mustard greens", "prepared mustard"],
    "celery": ["celery", "celeriac", "celery seed", "celery salt"],
    "sulphite": ["sulphite", "sulfite", "sulfur dioxide", "metabisulphite", "potassium bisulphite", "E220", "E221", "E222", "E223", "E224", "E226"],

    # Intolerances / Sensitivities / Diet-types (with hidden names)
    "lactose_intolerant": ["lactose", "milk powder", "whey", "lactase deficient", "dairy", "milk solids"],
    "gluten_intolerant": ["wheat", "barley", "rye", "malt", "triticale", "gluten", "hydrolysed wheat", "bread crumbs"],
    "fructose_intolerant": ["fructose", "high fructose corn syrup", "corn syrup", "honey", "fruit juice concentrate", "invert sugar"],
    "histamine_intolerant": ["fermented", "aged cheese", "wine", "beer", "smoked", "cured meat", "pickled", "processed fish"],
    "sugar_intolerant": ["sugar", "sucrose", "glucose", "fructose", "corn syrup", "dextrose", "maltose", "evaporated cane juice", "brown rice syrup"],
    "maida_intolerant": ["refined flour", "maida", "white flour", "all-purpose flour", "enriched wheat flour"],
    "vegan": ["egg", "eggs", "milk", "butter", "cheese", "gelatin", "honey", "dairy", "lactose", "casein", "whey"],
    "vegetarian": ["gelatin", "fish", "meat", "chicken", "beef", "pork", "shellfish", "seafood"],
    "keto": ["sugar", "glucose", "dextrose", "maida", "rice", "potato", "corn", "bread", "pasta", "cereal"],
    "diabetic_friendly": ["sugar", "sucrose", "glucose", "fructose", "corn syrup", "dextrose", "high glucose syrup"],
    "low_sodium": ["salt", "sodium", "monosodium glutamate", "msg", "sodium nitrite", "sodium benzoate"],
    "heart_safe": ["trans fat", "partially hydrogenated oil", "hydrogenated oil", "palm oil", "shortening", "cholesterol", "saturated fat high"]
}


# ---------- LOGIN / SIGNUP ----------
if not st.session_state.authenticated:
    st.markdown("<div class='marquee'>🌿 Healthy Living Starts with Smart Choices • Eat Clean • Stay Green • Live Fit 💪 • Choose Real Food • Love Your Body ❤️</div>", unsafe_allow_html=True)
    st.title("🔐 Sign In or Create an Account")
    st.markdown("### Scan, Analyze, and Shop Smart ✨")

    left_col, right_col = st.columns([1.2, 1])

    with left_col:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        with tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                login(email, password)

        with tab2:
            new_email = st.text_input("New Email", key="signup_email")
            new_password = st.text_input("New Password", type="password", key="signup_password")
            if st.button("Sign Up"):
                signup(new_email, new_password)

        st.info("💡 Demo Login → **demo@example.com / 1234**")

    with right_col:
        st.markdown("### 📰 Health Reads & Food Tips")
        blogs = {
    "🍋 Benefits of Lemon Water": """
Lemon water is one of the simplest yet most powerful drinks for your health. It provides a great dose of vitamin C, which strengthens immunity and helps fight infections. 
Drinking it first thing in the morning kickstarts your metabolism and flushes out toxins. 
It also supports digestion by stimulating bile production and balancing stomach acids. 
For clear skin, the antioxidants in lemon water help reduce blemishes and promote a radiant glow. 
If you suffer from acidity, a diluted glass of lemon water can actually alkalize your body. 
Remember not to overdo it — always dilute it well and rinse your mouth afterward to protect your tooth enamel.
""",

    "🍎 Why Eat an Apple a Day": """
The old saying “An apple a day keeps the doctor away” is surprisingly true! 
Apples are rich in dietary fiber, which aids digestion and promotes gut health. 
They are also loaded with antioxidants like quercetin that protect cells from damage. 
Eating apples regularly can lower the risk of heart disease and improve cholesterol balance. 
Their natural sugars are slowly released, providing sustained energy without sugar spikes. 
Apples also contribute to hydration, as they contain nearly 85% water. 
For the best health benefits, eat apples with the skin — that’s where most nutrients are!
""",

    "🥗 Importance of a Balanced Diet": """
A balanced diet is the foundation of good health and well-being. 
It ensures that your body receives the right proportions of carbohydrates, proteins, fats, vitamins, and minerals. 
Eating a mix of colorful fruits, vegetables, grains, and proteins helps your body repair tissues, generate energy, and fight illness. 
Too much of one nutrient or too little of another can lead to deficiencies or lifestyle diseases. 
Whole foods should make up most of your plate, while processed items should be limited. 
Hydration is equally important — water aids nutrient absorption and detoxification. 
Balance is the key — moderation, variety, and mindful eating make a real difference.
""",

    "🥑 Good Fats vs Bad Fats": """
Not all fats are your enemies — in fact, good fats are essential for heart health, hormone balance, and brain function. 
Healthy fats include monounsaturated and polyunsaturated fats found in foods like avocados, nuts, seeds, and olive oil. 
These fats can lower bad cholesterol (LDL) and increase good cholesterol (HDL). 
Bad fats, on the other hand, include trans fats and hydrogenated oils found in fried and processed foods. 
These increase the risk of heart disease, stroke, and inflammation. 
Always cook with minimal oil and choose oils like olive, sunflower, or canola over butter or margarine. 
Remember — it’s about quality and quantity. A handful of nuts a day keeps your heart happy!
""",

    "🍞 Understanding Gluten": """
Gluten is a protein found in grains such as wheat, barley, and rye. 
It helps dough rise and gives bread its chewy texture. 
However, some people experience gluten intolerance or celiac disease — a condition where gluten damages the small intestine. 
Symptoms can include bloating, fatigue, and digestive distress. 
For those affected, gluten-free diets can significantly improve health. 
Alternatives like rice flour, almond flour, and millet can replace wheat in cooking and baking. 
Even for non-allergic individuals, reducing refined gluten sources may improve digestion and energy levels.
""",

    "🥛 Lactose Intolerance Fix": """
Lactose intolerance occurs when the body lacks the enzyme lactase, which digests lactose in milk. 
This can cause bloating, cramps, or diarrhea after consuming dairy. 
Fortunately, there are plenty of alternatives — lactose-free milk, almond milk, soy milk, and oat milk are delicious and nutritious. 
Yogurt and aged cheeses may also be easier to digest, as they contain less lactose. 
Reading food labels carefully can help avoid hidden lactose in processed foods. 
Calcium can still be obtained from non-dairy sources like leafy greens, tofu, and fortified cereals.
""",

    "🍫 Sugar Cravings & Healthy Fixes": """
Sugar cravings are natural — your brain craves quick energy! 
But processed sugar causes spikes in blood glucose, leading to fatigue and mood swings later. 
Instead of candy or desserts, try natural sweeteners like dates, figs, or jaggery in moderation. 
Dark chocolate (70% cocoa or higher) satisfies sweet cravings while providing antioxidants. 
Pairing protein or fiber-rich foods with a small sweet treat can help stabilize blood sugar. 
Over time, reducing sugar intake sharpens your taste buds, and even fruits begin to taste sweeter!
""",

    "🌾 Go Whole Grain": """
Whole grains like brown rice, oats, quinoa, and whole wheat are rich in fiber, B vitamins, and essential minerals. 
They improve digestion, promote satiety, and help control cholesterol. 
Unlike refined grains, they contain the bran, germ, and endosperm — the most nutritious parts of the grain. 
Regular consumption of whole grains can reduce the risk of heart disease, diabetes, and obesity. 
Start your day with oats or switch to brown rice for dinner — your gut will thank you!
""",

    "🍇 Antioxidant Power of Berries": """
Berries such as blueberries, strawberries, raspberries, and blackberries are nutrient powerhouses. 
They are packed with antioxidants like anthocyanins and vitamin C, which protect your cells from free radical damage. 
Eating berries regularly supports brain function, slows aging, and strengthens immunity. 
They are also low in calories but high in fiber, making them perfect for weight control. 
Add them to smoothies, oatmeal, or salads for a colorful, health-boosting treat.
""",

    "🥕 Eat the Rainbow": """
The phrase “Eat the Rainbow” reminds us to include colorful fruits and vegetables in our meals. 
Each color represents a unique set of nutrients — red foods like tomatoes boost heart health, orange foods like carrots improve vision, and green veggies support detoxification. 
Purple and blue foods like berries promote brain health, while white foods like garlic boost immunity. 
The more variety on your plate, the broader your nutrient intake. 
So next time you cook, aim to make your plate as colorful as a rainbow — your body will love you for it!
""",

    "🍵 Green Tea Benefits": """
Green tea has been celebrated for centuries as a wellness elixir. 
It’s rich in catechins, a type of antioxidant that supports fat metabolism and protects the heart. 
Regular consumption may aid weight loss by enhancing thermogenesis (fat burning). 
It also helps reduce stress, improve mental clarity, and lower the risk of chronic diseases. 
Replace your sugary beverages with 2–3 cups of green tea a day to stay fresh and focused.
""",

    "🍊 Vitamin C Foods": """
Vitamin C is a powerful antioxidant that boosts your immune system and enhances skin glow. 
It helps your body absorb iron and repair tissues. 
Foods rich in vitamin C include oranges, guava, kiwi, strawberries, and bell peppers. 
A deficiency can cause fatigue, slow healing, and gum problems. 
Since vitamin C isn’t stored in the body, you need it daily from fresh foods. 
Start your mornings with a fruit salad or citrus juice to meet your daily dose naturally.
"""
}

        for title, content in blogs.items():
            with st.expander(title):
                st.write(content)

# ---------- MAIN APP ----------
else:
    st.sidebar.button("🚪 Logout", on_click=logout)
    st.markdown("<div class='marquee'>🛍️ Welcome to Scan&Shop — Smart Ingredient Scanner 🌱 Eat Smart • Stay Fit • Live Happy 💚</div>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    with st.sidebar.expander("❓ Not sure about an allergy or diet type? Click here to learn more!", expanded=False):
        st.markdown(
            """
            <div style='max-height:400px; overflow-y:auto; padding-right:10px'>
            <b>🥛 Milk Allergy:</b> Reaction to milk proteins like casein and whey. Avoid dairy, cheese, butter, yogurt.<br><br>
            <b>🥚 Egg Allergy:</b> Caused by egg proteins. Found in cakes, mayonnaise, and baked foods.<br><br>
            <b>🥜 Peanut Allergy:</b> Common severe allergy. Avoid peanuts, peanut oil, and peanut butter.<br><br>
            <b>🌰 Tree Nut Allergy:</b> Includes almonds, walnuts, cashews, pistachios. Check for nut oils.<br><br>
            <b>🌾 Gluten Intolerance:</b> Found in wheat, barley, rye. Choose gluten-free grains like rice, quinoa.<br><br>
            <b>🍣 Fish Allergy:</b> Avoid all types of fish and fish sauce. Common in Asian cuisines.<br><br>
            <b>🦐 Shellfish Allergy:</b> Avoid prawns, crab, shrimp, lobster, clams, oysters.<br><br>
            <b>🌱 Soy Allergy:</b> Found in soy sauce, tofu, soy protein. Read labels carefully.<br><br>
            <b>🥯 Sesame Allergy:</b> Includes sesame seeds, tahini, sesame oil. Common in breads.<br><br>
            <b>🌿 Mustard Allergy:</b> Avoid mustard condiments, dressings, and mustard oil.<br><br>
            <b>🥬 Celery Allergy:</b> Common in soups, spice mixes, and seasonings.<br><br>
            <b>🧂 Sulphite Sensitivity:</b> Avoid dried fruits, wines, and processed foods with E220–E224.<br><br>
            <b>🥛 Lactose Intolerance:</b> Body lacks enzyme lactase. Use lactose-free milk or plant alternatives.<br><br>
            <b>🍞 Maida Intolerance:</b> Caused by refined white flour. Prefer whole-grain or millet alternatives.<br><br>
            <b>🍭 Sugar Intolerance:</b> Affects blood sugar balance. Choose fruits or natural sweeteners.<br><br>
            <b>🥑 Vegan:</b> Avoid all animal products including dairy, eggs, and honey.<br><br>
            <b>🥗 Vegetarian:</b> Avoid meat, fish, poultry. Eggs and dairy may be optional.<br><br>
            <b>🥩 Keto:</b> Low-carb, high-fat diet. Avoid sugar, grains, and starchy foods.<br><br>
            <b>🩸 Diabetic Friendly:</b> Low sugar, high fiber foods preferred. Avoid syrups and sweets.<br><br>
            <b>🧘 Low Sodium:</b> Minimize salt, processed snacks, and sodium preservatives.<br><br>
            <b>❤️ Heart Safe:</b> Avoid trans fats, processed meats, and fried foods.<br><br>
            </div>
            """, unsafe_allow_html=True
        )
    st.sidebar.markdown("---")

    st.title("🌿 Dietary Preference Scanner")

    ocr = PaddleOCR(lang='en')

    def perform_ocr(img):
        return ocr.ocr(img)

    def highlight_specific_words(image, boxes, texts, target_words, color=(255, 0, 0), thickness=2):
        for box, text in zip(boxes, texts):
            if any(word.lower() in text.lower() for word in target_words):
                pts = np.array([tuple(map(int, p)) for p in box])
                cv2.polylines(image, [pts], isClosed=True, color=color, thickness=thickness)
        return image

    def check_dietary_preferences(ingredients, preferences):
        bad_words = []
        for pref in preferences:
            if pref.lower().replace(" ", "_") in allergen_data:
                keywords = allergen_data[pref.lower().replace(" ", "_")]
                for kw in keywords:
                    if any(kw.lower() in i.lower() for i in ingredients):
                        bad_words.append(kw)
        return len(bad_words) == 0, list(set(bad_words))

        st.markdown("<p class='highlight'>Step 1️⃣ — Select Your Dietary Preferences</p>", unsafe_allow_html=True)

    cols = st.columns(4)
    preferences = []

    options = [
        'milk', 'egg', 'peanut', 'tree_nut', 'gluten', 'soy', 'fish', 'shellfish',
        'sesame', 'mustard', 'celery', 'sulphite', 'lactose_intolerant', 'gluten_intolerant',
        'fructose_intolerant', 'histamine_intolerant', 'sugar_intolerant', 'maida_intolerant',
        'vegan', 'vegetarian', 'keto', 'diabetic_friendly', 'low_sodium', 'heart_safe'
    ]

    # Dynamically distribute checkboxes across columns
    for i, opt in enumerate(options):
        with cols[i % 4]:
            if st.checkbox(opt.replace("_", " ").title()):
                preferences.append(opt)


    if preferences:
        st.markdown("<p class='highlight'>Step 2️⃣ — Scan the Ingredient List</p>", unsafe_allow_html=True)
        camera_image = st.camera_input("📷 Take a picture of the ingredient list")

        if camera_image is not None:
            if st.button("🔍 Process Image"):
                image = np.frombuffer(camera_image.read(), np.uint8)
                img = cv2.imdecode(image, cv2.IMREAD_COLOR)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                result = perform_ocr(img)
                if not result or not result[0]:
                    st.error("❌ Please provide a clear image.")
                else:
                    boxes = [res[0] for res in result[0]]
                    texts = [res[1][0] for res in result[0]]
                    is_ok, bad_words = check_dietary_preferences(texts, preferences)

                    highlighted = highlight_specific_words(img, boxes, texts, bad_words)
                    st.image(highlighted, caption="Highlighted Ingredients", use_column_width=True)

                    if is_ok:
                        st.success("✅ Product is suitable for your preferences!")
                    else:
                        st.error("❌ Product is NOT suitable.")
                        st.write(f"⚠️ Problematic ingredients: **{', '.join(bad_words)}**")
    else:
        st.warning("⚠️ Please select at least one preference before scanning.")
# ✅ END OF FILE — DO NOT ADD app.run()
if __name__ == "__main__":
    st.warning("Please run this app using: streamlit run app.py")


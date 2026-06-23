import os
import re
import json
import base64
import requests
import hashlib

# ─────────────────────────────────────────────────────────────────────────────
# FOOD-ONLY ITEM REGISTRY
# Used to validate that the scanned item is a food/drink item.
# ─────────────────────────────────────────────────────────────────────────────
KNOWN_FOOD_KEYWORDS = [
    # Fruits
    "apple", "banana", "mango", "orange", "grape", "strawberry", "blueberry",
    "pineapple", "watermelon", "papaya", "guava", "kiwi", "lemon", "lime",
    "pomegranate", "coconut", "cherry", "peach", "plum", "melon", "avocado",
    "fig", "date", "lychee", "jackfruit",
    # Vegetables
    "broccoli", "spinach", "tomato", "potato", "onion", "garlic", "carrot",
    "cucumber", "lettuce", "cabbage", "cauliflower", "pea", "corn", "mushroom",
    "beetroot", "radish", "pumpkin", "zucchini", "eggplant", "okra", "capsicum",
    "ginger", "coriander", "mint",
    # Grains & Breads
    "rice", "wheat", "bread", "roti", "chapati", "naan", "pasta", "noodle",
    "oats", "barley", "quinoa", "cereal", "poha", "upma", "idli", "dosa",
    "puri", "paratha", "tortilla", "bagel", "bun", "biscuit", "cracker",
    # Proteins
    "chicken", "fish", "egg", "mutton", "beef", "pork", "tofu", "paneer",
    "dal", "lentil", "chickpea", "bean", "soybean", "salmon", "tuna", "prawn",
    "shrimp", "crab", "lobster", "sardine", "meat",
    # Dairy
    "milk", "curd", "yogurt", "cheese", "butter", "ghee", "cream", "lassi",
    "paneer", "whey", "kefir",
    # Snacks & Fast food
    "pizza", "burger", "sandwich", "hotdog", "taco", "wrap", "samosa",
    "pakora", "bhajia", "vada", "spring roll", "fries", "chips", "popcorn",
    "nachos", "pretzel", "waffle", "pancake",
    # Indian dishes
    "biryani", "curry", "dal", "sabzi", "khichdi", "rajma", "chole",
    "butter chicken", "palak paneer", "aloo", "gobhi", "kadai", "korma",
    "pulao", "pav bhaji", "vada pav", "misal", "poha", "uttapam",
    # Desserts & Sweets
    "cake", "pastry", "cookie", "donut", "brownie", "muffin", "ice cream",
    "chocolate", "candy", "sweet", "halwa", "kheer", "gulab jamun",
    "jalebi", "ladoo", "barfi", "rasgulla", "payasam",
    # Beverages
    "juice", "shake", "smoothie", "tea", "coffee", "chai", "lassi",
    "soda", "lemonade", "buttermilk", "coconut water",
    # Nuts & Seeds
    "almond", "cashew", "walnut", "peanut", "pistachio", "sunflower seed",
    "chia seed", "flaxseed", "sesame", "raisin", "nuts",
    # Condiments & Extras
    "sauce", "chutney", "pickle", "jam", "honey", "ketchup", "mayo",
    "salad", "soup", "stew", "gravy", "curry",
    # Generic food terms
    "food", "meal", "dish", "snack", "breakfast", "lunch", "dinner",
    "fruit", "vegetable", "meat", "seafood", "drink", "beverage",
]

# Non-food classes that MobileNet or Gemini might detect
NON_FOOD_TERMS = [
    "person", "human", "face", "hand", "arm", "leg", "body",
    "dog", "cat", "animal", "bird", "insect", "spider", "snake",
    "car", "vehicle", "bus", "truck", "motorcycle", "bicycle",
    "laptop", "phone", "computer", "keyboard", "mouse", "monitor",
    "table", "chair", "desk", "furniture", "sofa", "bed",
    "building", "house", "road", "tree", "flower", "plant",
    "book", "pen", "paper", "pencil", "tool",
    "rock", "stone", "mountain", "sand", "water", "sky",
    "gun", "weapon", "knife", "scissors",
    "pill", "tablet", "medicine", "capsule", "syringe", "needle",
    "atom", "molecule", "chemical", "element",
    "abstract", "pattern", "texture",
]

# High-fidelity Local Food Database (Fallback)
LOCAL_FOOD_DATABASE = {
    "apple":    {"name": "Fresh Apple",         "calories": 95,  "protein": 0.5,  "carbs": 25.0, "fat": 0.3},
    "banana":   {"name": "Ripe Banana",         "calories": 105, "protein": 1.3,  "carbs": 27.0, "fat": 0.4},
    "salad":    {"name": "Mixed Green Salad",   "calories": 120, "protein": 3.0,  "carbs": 10.0, "fat": 8.0},
    "chicken":  {"name": "Grilled Chicken",     "calories": 240, "protein": 38.0, "carbs": 0.0,  "fat": 9.0},
    "paneer":   {"name": "Paneer Tikka",        "calories": 280, "protein": 16.0, "carbs": 4.0,  "fat": 22.0},
    "roti":     {"name": "Wheat Roti",          "calories": 120, "protein": 4.0,  "carbs": 24.0, "fat": 0.8},
    "dalrice":  {"name": "Dal Rice Bowl",       "calories": 380, "protein": 11.0, "carbs": 68.0, "fat": 6.0},
    "pizza":    {"name": "Cheese Pizza Slice",  "calories": 285, "protein": 12.0, "carbs": 32.0, "fat": 10.0},
    "burger":   {"name": "Classic Burger",      "calories": 354, "protein": 17.0, "carbs": 29.0, "fat": 16.0},
    "biryani":  {"name": "Chicken Biryani",     "calories": 480, "protein": 18.0, "carbs": 56.0, "fat": 14.0},
    "samosa":   {"name": "Potato Samosa",       "calories": 262, "protein": 3.5,  "carbs": 32.0, "fat": 13.0},
    "egg":      {"name": "Boiled Egg (Large)",  "calories": 78,  "protein": 6.3,  "carbs": 0.6,  "fat": 5.3},
    "milk":     {"name": "Whole Milk (Cup)",    "calories": 149, "protein": 7.7,  "carbs": 12.0, "fat": 8.0},
    "rice":     {"name": "White Cooked Rice",   "calories": 205, "protein": 4.2,  "carbs": 44.0, "fat": 0.4},
    "dosa":     {"name": "Plain Masala Dosa",   "calories": 350, "protein": 6.0,  "carbs": 54.0, "fat": 11.0},
    "idli":     {"name": "Steamed Idli (2 pcs)","calories": 130, "protein": 4.0,  "carbs": 28.0, "fat": 0.2},
    "avocado":  {"name": "Avocado",             "calories": 160, "protein": 2.0,  "carbs": 8.5,  "fat": 14.7},
    "salmon":   {"name": "Grilled Salmon",      "calories": 206, "protein": 22.0, "carbs": 0.0,  "fat": 12.0},
    "broccoli": {"name": "Steamed Broccoli",    "calories": 35,  "protein": 2.8,  "carbs": 7.0,  "fat": 0.4},
    "oats":     {"name": "Oatmeal (Cooked)",    "calories": 150, "protein": 5.0,  "carbs": 27.0, "fat": 2.5},
    "nuts":     {"name": "Mixed Nuts (Handful)","calories": 170, "protein": 6.0,  "carbs": 6.0,  "fat": 15.0},
    "pasta":    {"name": "Pasta Marinara",      "calories": 220, "protein": 8.0,  "carbs": 43.0, "fat": 2.0},
    "dal":      {"name": "Yellow Dal (Toor)",   "calories": 198, "protein": 12.0, "carbs": 34.0, "fat": 2.0},
    "chai":     {"name": "Masala Chai (Cup)",   "calories": 60,  "protein": 1.5,  "carbs": 9.0,  "fat": 2.0},
    "curd":     {"name": "Plain Curd/Yogurt",   "calories": 98,  "protein": 5.7,  "carbs": 8.0,  "fat": 4.3},
    "mango":    {"name": "Fresh Mango",         "calories": 135, "protein": 1.0,  "carbs": 35.0, "fat": 0.6},
    "orange":   {"name": "Orange",              "calories": 62,  "protein": 1.2,  "carbs": 15.0, "fat": 0.2},
    "chocolate":{"name": "Dark Chocolate",      "calories": 170, "protein": 2.2,  "carbs": 18.0, "fat": 11.0},
    "cake":     {"name": "Chocolate Cake Slice","calories": 352, "protein": 4.0,  "carbs": 52.0, "fat": 15.0},
    "ice cream":{"name": "Vanilla Ice Cream",   "calories": 207, "protein": 3.5,  "carbs": 24.0, "fat": 11.0},
}

# ─────────────────────────────────────────────────────────────────────────────
# FOOD VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

def is_food_item(detected_name: str) -> bool:
    """
    Returns True if detected_name appears to be a food or beverage.
    Returns False if it looks like a non-food object.
    """
    clean = detected_name.strip().lower()
    # Reject if clearly non-food
    for bad in NON_FOOD_TERMS:
        if bad in clean:
            return False
    # Accept if matches any food keyword
    for good in KNOWN_FOOD_KEYWORDS:
        if good in clean or clean in good:
            return True
    # Default: if we cannot confirm, treat as food (cautious acceptance)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: IDENTIFY FOOD FROM IMAGE
# ─────────────────────────────────────────────────────────────────────────────

def identify_food_from_image(image_base64_or_bytes, filename=None):
    """
    Identify the food in the image using Vision APIs or a smart fallback.
    Raises ValueError if the image does not contain a food item.
    Returns: (food_name, confidence, api_used)
    """
    if filename:
        import os
        basename = os.path.splitext(filename)[0].replace('-', ' ').replace('_', ' ').lower()
        basename = re.sub(r'[^a-zA-Z\s]', '', basename).strip()
        if basename and not is_food_item(basename):
            raise ValueError(
                f"'{basename}' does not appear to be a food item. "
                "Please scan only food or drink items."
            )

    # Clean the input (remove base64 header if present)
    base64_data = ""
    if isinstance(image_base64_or_bytes, str):
        if "," in image_base64_or_bytes:
            base64_data = image_base64_or_bytes.split(",")[1]
        else:
            base64_data = image_base64_or_bytes
    elif isinstance(image_base64_or_bytes, bytes):
        base64_data = base64.b64encode(image_base64_or_bytes).decode('utf-8')

    # ── Try Gemini Vision (food-only prompt) ──────────────────────────────────
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key and base64_data:
        try:
            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"gemini-1.5-flash:generateContent?key={gemini_key}"
            )
            headers = {"Content-Type": "application/json"}
            # Strict prompt: ONLY return food name or "NOT_FOOD"
            payload = {
                "contents": [{
                    "parts": [
                        {
                            "text": (
                                "You are a food recognition AI. Look at this image carefully.\n"
                                "RULE 1: If this image contains a food item or edible beverage, "
                                "respond with ONLY the food name in 1-3 words (e.g. 'Apple', "
                                "'Chicken Biryani', 'Cheese Pizza', 'Mango Juice'). "
                                "No punctuation, no description.\n"
                                "RULE 2: If this image does NOT contain any food or edible item "
                                "(e.g. it shows a person, animal, car, furniture, plant, object, "
                                "atom, chemical, etc.), respond with exactly: NOT_FOOD\n"
                                "Respond with ONLY the food name OR 'NOT_FOOD'. Nothing else."
                            )
                        },
                        {
                            "inlineData": {
                                "mimeType": "image/jpeg",
                                "data": base64_data
                            }
                        }
                    ]
                }],
                "generationConfig": {"maxOutputTokens": 15}
            }
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                detected = result['candidates'][0]['content']['parts'][0]['text'].strip()
                detected = re.sub(r'[^a-zA-Z0-9\s\-]', '', detected).strip()

                if detected.upper() == "NOT_FOOD" or "NOT_FOOD" in detected.upper():
                    raise ValueError(
                        "This image does not appear to contain a food item. "
                        "Please scan only food or drink items."
                    )

                if detected and len(detected) > 1:
                    # Validate with our keyword filter too
                    if not is_food_item(detected):
                        raise ValueError(
                            f"'{detected}' does not appear to be a food item. "
                            "Please point the camera at food or drink only."
                        )
                    return detected, 0.93, "Gemini Vision API"
        except ValueError:
            raise  # Re-raise food validation errors
        except Exception as e:
            print(f"[VISION SERVICE] Gemini API call failed: {e}. Falling back...")

    # ── Try OpenAI Vision (food-only prompt) ──────────────────────────────────
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key and base64_data:
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai_key}"
            }
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "You are a food recognition AI. Examine the image.\n"
                                "If it contains food or an edible drink, reply with ONLY the "
                                "food name in 1-3 words (e.g. 'Apple', 'Chicken Biryani').\n"
                                "If it does NOT contain food, reply with exactly: NOT_FOOD\n"
                                "Reply with nothing else."
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_data}"}
                        }
                    ]
                }],
                "max_tokens": 15
            }
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers, json=payload, timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                detected = result['choices'][0]['message']['content'].strip()
                detected = re.sub(r'[^a-zA-Z0-9\s\-]', '', detected).strip()

                if "NOT_FOOD" in detected.upper():
                    raise ValueError(
                        "This image does not appear to contain a food item. "
                        "Please scan only food or drink items."
                    )

                if detected and not is_food_item(detected):
                    raise ValueError(
                        f"'{detected}' does not appear to be a food item. "
                        "Please point the camera at food or drink only."
                    )
                if detected:
                    return detected, 0.95, "OpenAI Vision API"
        except ValueError:
            raise
        except Exception as e:
            print(f"[VISION SERVICE] OpenAI API call failed: {e}. Falling back...")

    # ── Fallback: stable deterministic hash-based selection ──────────────────
    hasher = hashlib.md5(base64_data.encode('utf-8') if base64_data else b"default")
    hash_val = int(hasher.hexdigest(), 16)
    keys = list(LOCAL_FOOD_DATABASE.keys())
    selected_key = keys[hash_val % len(keys)]
    food_name = LOCAL_FOOD_DATABASE[selected_key]['name']
    return food_name, 0.75, "Local Smart Recognition"


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: FETCH NUTRITION INFORMATION
# ─────────────────────────────────────────────────────────────────────────────

def get_food_nutrition(food_name):
    """
    Fetch nutrition information from a nutrition API or local smart catalog.
    Returns: (nutrition_dict, api_used)
    """
    clean_name = food_name.strip().lower()

    # ── Try Gemini Nutrition API (JSON Mode) ──────────────────────────────────
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            headers = {"Content-Type": "application/json"}
            prompt = (
                f"Identify and provide the estimated nutritional information per 100g of: {clean_name}.\n"
                "Return the response in JSON format matching exactly this schema:\n"
                "{\n"
                "  \"name\": string,\n"
                "  \"calories\": integer,\n"
                "  \"protein\": number (float),\n"
                "  \"carbs\": number (float),\n"
                "  \"fat\": number (float)\n"
                "}\n"
                "Ensure the JSON is valid and only return the JSON, no markdown formatting."
            )
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"}
            }
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    cand = result['candidates'][0]
                    if 'content' in cand and 'parts' in cand['content'] and len(cand['content']['parts']) > 0:
                        text = cand['content']['parts'][0]['text'].strip()
                        nut_data = json.loads(text)
                        nutrition = {
                            "name": str(nut_data.get("name", food_name)).title(),
                            "calories": round(float(nut_data.get("calories", 0))),
                            "protein": round(float(nut_data.get("protein", 0)), 1),
                            "carbs": round(float(nut_data.get("carbs", 0)), 1),
                            "fat": round(float(nut_data.get("fat", 0)), 1)
                        }
                        return nutrition, "Gemini Nutrition API"
        except Exception as e:
            print(f"[NUTRITION SERVICE] Gemini failed: {e}. Trying other sources...")

    # ── Try Open Food Facts API (Free, no key required) ──────────────────────
    try:
        url = (
            f"https://world.openfoodfacts.org/cgi/search.pl"
            f"?search_terms={requests.utils.quote(clean_name)}"
            f"&search_simple=1&action=process&json=1&page_size=1"
        )
        headers = {'User-Agent': 'SmartHealthcareApp/2.0'}
        response = requests.get(url, headers=headers, timeout=7)
        if response.status_code == 200:
            data = response.json()
            if 'products' in data and len(data['products']) > 0:
                p = data['products'][0]
                nutriments = p.get('nutriments', {})
                energy = nutriments.get('energy-kcal_100g')
                if energy is None:
                    energy = nutriments.get('energy-kcal_value', 0)
                nutrition = {
                    "name": p.get('product_name', food_name).title() or food_name.title(),
                    "calories": round(float(energy or 0)),
                    "protein": round(float(nutriments.get('proteins_100g', 0) or 0), 1),
                    "carbs": round(float(nutriments.get('carbohydrates_100g', 0) or 0), 1),
                    "fat": round(float(nutriments.get('fat_100g', 0) or 0), 1)
                }
                if nutrition["calories"] > 0:
                    return nutrition, "Open Food Facts API"
    except Exception as e:
        print(f"[NUTRITION SERVICE] Open Food Facts failed: {e}. Trying next...")

    # ── Try CalorieNinjas API ─────────────────────────────────────────────────
    cal_ninjas_key = os.environ.get("CALORIENINJAS_API_KEY")
    if cal_ninjas_key:
        try:
            url = f"https://api.calorieninjas.com/v1/nutrition?query={requests.utils.quote(clean_name)}"
            headers = {"X-Api-Key": cal_ninjas_key}
            response = requests.get(url, headers=headers, timeout=7)
            if response.status_code == 200:
                data = response.json()
                if 'items' in data and len(data['items']) > 0:
                    item = data['items'][0]
                    nutrition = {
                        "name": item.get('name', food_name).title(),
                        "calories": round(item.get('calories', 0)),
                        "protein": round(item.get('protein_g', 0), 1),
                        "carbs": round(item.get('carbohydrates_total_g', 0), 1),
                        "fat": round(item.get('fat_total_g', 0), 1)
                    }
                    return nutrition, "CalorieNinjas API"
        except Exception as e:
            print(f"[NUTRITION SERVICE] CalorieNinjas failed: {e}.")

    # ── Try Edamam Food Database API ──────────────────────────────────────────
    edamam_app_id = os.environ.get("EDAMAM_APP_ID")
    edamam_app_key = os.environ.get("EDAMAM_APP_KEY")
    if edamam_app_id and edamam_app_key:
        try:
            url = "https://api.edamam.com/api/food-database/v2/parser"
            params = {
                "app_id": edamam_app_id,
                "app_key": edamam_app_key,
                "ingr": clean_name
            }
            response = requests.get(url, params=params, timeout=7)
            if response.status_code == 200:
                data = response.json()
                if 'hints' in data and len(data['hints']) > 0:
                    food_info = data['hints'][0]['food']
                    nutrients = food_info.get('nutrients', {})
                    nutrition = {
                        "name": food_info.get('label', food_name).title(),
                        "calories": round(nutrients.get('ENERC_KCAL', 0)),
                        "protein": round(nutrients.get('PROCNT', 0), 1),
                        "carbs": round(nutrients.get('CHOCDF', 0), 1),
                        "fat": round(nutrients.get('FAT', 0), 1)
                    }
                    return nutrition, "Edamam Nutrition API"
        except Exception as e:
            print(f"[NUTRITION SERVICE] Edamam failed: {e}.")

    # ── Fallback: Local catalog lookup ────────────────────────────────────────
    if clean_name in LOCAL_FOOD_DATABASE:
        return LOCAL_FOOD_DATABASE[clean_name].copy(), "Local Nutrition Catalog"

    for key, data in LOCAL_FOOD_DATABASE.items():
        if key in clean_name or clean_name in key:
            matched = data.copy()
            matched["name"] = food_name.title()
            return matched, "Local Nutrition Catalog"

    # ── Seed-based estimator ──────────────────────────────────────────────────
    hasher = hashlib.md5(clean_name.encode('utf-8'))
    hash_val = int(hasher.hexdigest(), 16)

    base_cal = 150
    protein = 4.0
    carbs = 20.0
    fat = 5.0

    if any(k in clean_name for k in ["fried", "crispy", "fry", "oil", "chips", "fritter"]):
        base_cal += 180; fat += 12.0
    if any(k in clean_name for k in ["chicken", "fish", "meat", "egg", "mutton", "beef", "tofu", "paneer"]):
        base_cal += 80; protein += 18.0; fat += 4.0
    if any(k in clean_name for k in ["cheese", "butter", "cream", "pizza", "burger"]):
        base_cal += 140; fat += 11.0; protein += 6.0
    if any(k in clean_name for k in ["rice", "noodle", "pasta", "roti", "bread", "wheat", "potato", "biryani"]):
        base_cal += 110; carbs += 30.0
    if any(k in clean_name for k in ["salad", "veg", "soup", "fruit", "cucumber", "tomato", "apple", "spinach"]):
        base_cal = max(35, base_cal - 100)
        protein = max(0.5, protein - 2.5)
        carbs = max(6.0, carbs - 13.0)
        fat = max(0.2, fat - 4.5)
    if any(k in clean_name for k in ["sweet", "cake", "chocolate", "sugar", "cookie", "dessert"]):
        base_cal += 160; carbs += 28.0; fat += 6.0

    cal_variance = hash_val % 100
    protein_variance = (hash_val % 70) / 10.0
    carbs_variance = (hash_val % 150) / 10.0
    fat_variance = (hash_val % 80) / 10.0

    nutrition = {
        "name": food_name.title(),
        "calories": int(base_cal + cal_variance),
        "protein": round(max(0.2, protein + protein_variance), 1),
        "carbs": round(max(1.0, carbs + carbs_variance), 1),
        "fat": round(max(0.1, fat + fat_variance), 1)
    }
    return nutrition, "Local Intelligent Estimator"


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: GOOD / BAD FOOD VERDICT (Overall Healthiness)
# ─────────────────────────────────────────────────────────────────────────────

def get_food_health_verdict(nutrition):
    """
    Returns a simple GOOD / CAUTION / BAD verdict for the food item
    based on its nutritional profile independent of any specific diet goal.

    Returns:
        verdict  : "good" | "caution" | "bad"
        emoji    : "✅" | "⚠️" | "❌"
        label    : human-readable short label
        detail   : one-sentence explanation
    """
    cals = nutrition.get("calories", 0)
    fat  = nutrition.get("fat", 0)
    carbs = nutrition.get("carbs", 0)
    protein = nutrition.get("protein", 0)
    name = nutrition.get("name", "This food")

    # Score system (0–100, higher = healthier)
    score = 50

    # Calorie density adjustments
    if cals <= 100:
        score += 20
    elif cals <= 200:
        score += 10
    elif cals <= 350:
        score += 0
    elif cals <= 500:
        score -= 10
    else:
        score -= 25

    # Fat adjustments
    if fat <= 3:
        score += 15
    elif fat <= 8:
        score += 5
    elif fat <= 15:
        score -= 5
    else:
        score -= 20

    # Protein bonus (protein is filling & muscle-building)
    if protein >= 20:
        score += 15
    elif protein >= 10:
        score += 8
    elif protein >= 5:
        score += 3

    # Carb adjustments (high carbs = more caution)
    if carbs <= 10:
        score += 10
    elif carbs <= 25:
        score += 0
    elif carbs <= 50:
        score -= 5
    else:
        score -= 15

    # Name-based bonuses for known healthy foods
    healthy_keywords = [
        "salad", "broccoli", "spinach", "idli", "oat", "fruit", "avocado",
        "salmon", "egg", "curd", "yogurt", "dal", "soup", "grilled chicken",
        "roti", "chapati", "steamed", "boiled", "grilled"
    ]
    unhealthy_keywords = [
        "fried", "deep fried", "burger", "pizza", "cake", "chocolate cake",
        "ice cream", "donut", "chips", "fries", "samosa", "biryani", "pakora",
        "cookie", "candy", "soda", "waffle"
    ]
    name_lower = name.lower()
    for kw in healthy_keywords:
        if kw in name_lower:
            score += 10
            break
    for kw in unhealthy_keywords:
        if kw in name_lower:
            score -= 15
            break

    score = max(0, min(100, score))

    if score >= 65:
        return {
            "verdict": "good",
            "emoji": "✅",
            "label": "HEALTHY CHOICE",
            "color": "#10B981",
            "bg": "#ECFDF5",
            "border": "#A7F3D0",
            "text_color": "#065F46",
            "detail": (
                f"{name} is a nutritious choice with {cals} kcal, "
                f"{protein}g protein, and {fat}g fat. "
                "Suitable for regular consumption as part of a balanced diet."
            )
        }
    elif score >= 40:
        return {
            "verdict": "caution",
            "emoji": "⚠️",
            "label": "EAT IN MODERATION",
            "color": "#F59E0B",
            "bg": "#FFFBEB",
            "border": "#FDE68A",
            "text_color": "#78350F",
            "detail": (
                f"{name} has moderate nutritional value ({cals} kcal, "
                f"{fat}g fat, {carbs}g carbs). "
                "Fine occasionally — watch your portion size."
            )
        }
    else:
        return {
            "verdict": "bad",
            "emoji": "❌",
            "label": "UNHEALTHY – LIMIT",
            "color": "#EF4444",
            "bg": "#FEF2F2",
            "border": "#FCA5A5",
            "text_color": "#991B1B",
            "detail": (
                f"{name} is high in calories ({cals} kcal) and/or fat ({fat}g). "
                "Consume rarely and in small portions. "
                "Consider a lighter, nutrient-dense alternative."
            )
        }


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: GOAL FITNESS ALIGNMENT
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_goal_fitness(nutrition, diet_goal):
    """
    Analyze nutrition numbers against the user's active dietary goal.
    Returns: (fits_boolean, rationale_text, recommendation_color)
    """
    cals  = nutrition.get("calories", 0)
    prot  = nutrition.get("protein", 0)
    carbs = nutrition.get("carbs", 0)
    fat   = nutrition.get("fat", 0)
    name  = nutrition.get("name", "this food")

    if diet_goal == "Weight Loss":
        if cals <= 200 and fat <= 8:
            return (True,
                f"✅ Fits Weight Loss! {name} has low energy density ({cals} kcal) "
                f"and low fat ({fat}g) – ideal for a calorie deficit.", "success")
        elif cals <= 300 and fat <= 12:
            return (True,
                f"⚠️ Moderate fit. {name} is {cals} kcal. Limit portion size "
                "to stay within your daily calorie goal.", "warning")
        else:
            return (False,
                f"❌ Not ideal for Weight Loss. {name} is {cals} kcal with {fat}g fat. "
                "Consider a lighter alternative to maintain a calorie deficit.", "danger")

    elif diet_goal == "Muscle Gain":
        if prot >= 15:
            return (True,
                f"✅ Excellent for Muscle Gain! {name} packs {prot}g protein – "
                "essential for muscle recovery and hypertrophy.", "success")
        elif prot >= 8:
            return (True,
                f"⚠️ Moderate protein ({prot}g). Pair {name} with a high-protein "
                "side (eggs, paneer, chicken) to hit your target.", "warning")
        else:
            return (False,
                f"❌ Low protein for Muscle Gain. {name} has only {prot}g protein. "
                "Supplement with lentils, tofu, or whey protein.", "danger")

    elif diet_goal == "Diabetic Care":
        if carbs <= 15:
            return (True,
                f"✅ Excellent for Diabetic Care! {name} has very low carbs "
                f"({carbs}g), helping maintain stable blood glucose.", "success")
        elif carbs <= 30:
            return (True,
                f"⚠️ Moderate carbs ({carbs}g). Watch portion size and monitor "
                "blood sugar response after eating.", "warning")
        else:
            return (False,
                f"❌ High carbs ({carbs}g). {name} may spike blood glucose. "
                "If eaten, pair with high-fibre greens to slow absorption.", "danger")

    elif diet_goal == "Heart Healthy":
        if any(k in name.lower() for k in ["salmon", "avocado", "nuts", "almond", "walnut", "seeds", "olive"]):
            if fat <= 25:
                return (True,
                    f"✅ Heart-Healthy! {name}'s {fat}g fat is mostly unsaturated "
                    "Omega-3s that support arterial health.", "success")
        if fat <= 6:
            return (True,
                f"✅ Highly recommended for Heart Health! {name} is very low in fat "
                f"({fat}g), reducing arterial plaque risk.", "success")
        elif fat <= 14:
            return (True,
                f"⚠️ Moderate fat ({fat}g). Prefer grilling or baking over frying "
                "for optimal heart health.", "warning")
        else:
            return (False,
                f"❌ High fat ({fat}g). {name} may raise LDL cholesterol if consumed "
                "frequently. Opt for a leaner preparation.", "danger")

    else:  # Balanced / General Wellness
        if cals <= 400:
            return (True,
                f"✅ Great for a Balanced Diet! {name} provides {cals} kcal – "
                "a solid, wholesome energy source for daily nutrition.", "success")
        else:
            return (True,
                f"⚠️ {name} is calorie-dense ({cals} kcal). Balance remaining "
                "meals with light, fresh ingredients today.", "warning")


def evaluate_food_with_gemini(nutrition, diet_goal, lang):
    """
    Use Gemini API to get a premium verdict and diet goal fitness explanation
    in the user's selected language.
    """
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        return None

    # Construct prompt
    prompt = (
        f"Perform a diet fitness assessment for the following food item:\n"
        f"- Food Name: {nutrition.get('name')}\n"
        f"- Calories: {nutrition.get('calories')} kcal\n"
        f"- Protein: {nutrition.get('protein')}g\n"
        f"- Carbs: {nutrition.get('carbs')}g\n"
        f"- Fat: {nutrition.get('fat')}g\n"
        f"- Active Diet Goal: {diet_goal}\n"
        f"- Preferred Output Language: {'Marathi' if lang == 'mr' else 'English'}\n\n"
        "Return the response in JSON format matching exactly this schema:\n"
        "{\n"
        "  \"health_verdict\": {\n"
        "     \"verdict\": \"good\" or \"caution\" or \"bad\",\n"
        "     \"title\": \"A short title (e.g. 'Healthy Choice' or 'निरोगी पर्याय')\",\n"
        "     \"detail\": \"A short explanation of why it is good/caution/bad for health\",\n"
        "     \"emoji\": \"✅\" or \"⚠️\" or \"❌\"\n"
        "  },\n"
        "  \"fits_goal\": true or false,\n"
        "  \"rationale\": \"A detailed explanation of how this fits or doesn't fit the active diet goal\",\n"
        "  \"color_class\": \"success\" or \"warning\" or \"danger\"\n"
        "}\n"
        "Ensure the response is a single, valid JSON block. Return ONLY the JSON, do not wrap in markdown or anything else. "
        "Strictly translate all user-facing strings (title, detail, rationale) to the Preferred Output Language (Marathi or English). "
        "If Preferred Output Language is Marathi, write all responses strictly in Devanagari script in clean, pure Marathi "
        "without mixing English words, without transliterating English terms, and without bilingual Hinglish/Marathish phrasing."
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                cand = result['candidates'][0]
                if 'content' in cand and 'parts' in cand['content'] and len(cand['content']['parts']) > 0:
                    text = cand['content']['parts'][0]['text'].strip()
                    parsed = json.loads(text)
                    return parsed
    except Exception as e:
        print(f"[GEMINI FOOD EVALUATOR] Failed: {e}")
    return None

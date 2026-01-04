from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.generativeai as genai
import os
import base64

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

app = FastAPI()

# Allow React to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with React URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# 1️⃣ IMAGE → INGREDIENTS API
# -----------------------------
@app.post("/detect-ingredients")
async def detect_ingredients(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    response = model.generate_content([
        "Identify all edible food ingredients visible in this fridge image. "
        "Return ONLY a comma-separated list.",
        {
            "mime_type": "image/jpeg",
            "data": image_base64
        }
    ])

    return {
        "ingredients": response.text
    }

# -----------------------------
# 2️⃣ INGREDIENTS → RECIPE API
# -----------------------------
@app.post("/generate-recipe")
async def generate_recipe(payload: dict):
    ingredients = payload.get("ingredients")

    prompt = f"""
You are a smart cooking assistant.

Create ONE recipe using ONLY these ingredients:
{ingredients}

Rules:
- Do not invent ingredients
- If absolutely necessary, suggest ONLY ONE missing item
- Give recipe name, time, and steps
"""

    response = model.generate_content(prompt)

    return {
        "recipe": response.text
    }

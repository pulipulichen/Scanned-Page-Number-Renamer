import os
import io
import time
import json
import requests
from PIL import Image

MAX_RETRIES = int(os.environ.get("MAX_RETRIES", 1))
RETRY_DELAY_SECONDS = int(os.environ.get("RETRY_DELAY_SECONDS", 5))
GEMINI_TIMEOUT = int(os.environ.get("GEMINI_TIMEOUT", 30)) # Default to 30 seconds

# Relaxed safety settings (backend still filters, not 100% off)
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

api_key = os.environ.get("GOOGLE_API_KEY")
gemini_model = os.environ.get("GEMINI_MODEL", "gemini-pro-vision") # Default to gemini-pro-vision
prompt_text = os.environ.get("PROMPT_TEXT", "Detected page number, 'cover', or 'copyright'.")
gemini_baseurl = os.environ.get("GEMINI_BASEURL", "https://generativelanguage.googleapis.com/") # Default to gemini-pro-vision

# Define a simple response schema for page number detection
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "page_number": {
            "type": "string",
            "description": prompt_text
        }
    },
    "required": ["page_number"]
}

from .image_to_base64 import image_to_base64

def detect_page_number(image_path: str) -> str:
    """
    Detects the page number in an image using the Gemini API via URL with retry mechanism.
    Returns "cover", "copyright", or the detected page number as a string.
    """
    
    if not api_key:
        return "Error: GOOGLE_API_KEY not found in environment variables."
    
    url = f"{gemini_baseurl}v1beta/models/{gemini_model}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

    if not os.path.exists(image_path):
        return f"Error: Image file not found at {image_path}"

    try:
        # Load the image and convert to base64
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        img_b64 = image_to_base64(image_path)

        # For structured format, we can pass the image directly
        image_part = {
            "inline_data": {
                "mime_type": "image/png", # Assuming JPEG, adjust if needed or detect dynamically
                "data": img_b64
            }
        }

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt_text},
                        image_part
                    ]
                }
            ],
            "safetySettings": SAFETY_SETTINGS,
            "generationConfig": {
                "response_mime_type": "application/json",
                "response_schema": RESPONSE_SCHEMA
            }
        }

        for attempt in range(MAX_RETRIES):
            try:
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=GEMINI_TIMEOUT)
                print(response.json())
                response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

                data = response.json()
                
                # Check for prompt feedback blocking
                pf = data.get("promptFeedback")
                if pf and pf.get("blockReason"):
                    raise RuntimeError(f"Prompt blocked by Gemini: {pf.get('blockReason')}")

                json_text = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed_response = json.loads(json_text)
                
                result = parsed_response.get("page_number", "Detection Failed")


                # 如果result(現在是字串)是由數字組成，那把它轉換成4位數，前面補0
                if result.isdigit():
                    result = f"{int(result):04d}"

                return result

            except requests.exceptions.Timeout:
                if attempt < MAX_RETRIES - 1:
                    print(f"Attempt {attempt + 1} failed: Gemini API request exceeded {GEMINI_TIMEOUT} seconds timeout. Retrying in {RETRY_DELAY_SECONDS} seconds...")
                    time.sleep(RETRY_DELAY_SECONDS)
                else:
                    return f"Error: Gemini API request exceeded {GEMINI_TIMEOUT} seconds timeout after {MAX_RETRIES} attempts."
            except requests.exceptions.RequestException as e:
                if attempt < MAX_RETRIES - 1:
                    print(f"Attempt {attempt + 1} failed: Request failed: {e}. Retrying in {RETRY_DELAY_SECONDS} seconds...")
                    time.sleep(RETRY_DELAY_SECONDS)
                else:
                    return f"Error: Request failed after {MAX_RETRIES} attempts: {e}"
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                if attempt < MAX_RETRIES - 1:
                    print(f"Attempt {attempt + 1} failed: Response parsing error: {repr(e)}. Raw response: {data}. Retrying in {RETRY_DELAY_SECONDS} seconds...")
                    time.sleep(RETRY_DELAY_SECONDS)
                else:
                    return f"Error: Response parsing error after {MAX_RETRIES} attempts: {repr(e)}. Raw response: {data}"
            except RuntimeError as e: # For prompt blocked errors
                return f"Error: {e}"

    except Exception as e:
        return f"Error loading image or initial setup: {e}"

if __name__ == "__main__":
    # Example usage (replace with a valid image path for testing)
    # For local testing, you might need to provide a dummy image or
    # integrate with the main script's image handling.
    # For now, just a placeholder.
    print("This script is intended to be called with an image path.")
    print("Example: python scripts/detect_page_number.py /path/to/your/image.jpg")
    # You would typically call detect_page_number(image_file_path) here
    # For demonstration, let's simulate a call if an argument is provided
    import sys
    if len(sys.argv) > 1:
        test_image_path = sys.argv[1]
        result = detect_page_number(test_image_path)
        print(f"Detected page number for '{test_image_path}': {result}")
    else:
        print("No image path provided for testing.")

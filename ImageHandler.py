from flask import Flask, request, jsonify
from PIL import Image
import requests
from io import BytesIO
import logging

# Setup basic logging to see requests in Render logs
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/convert')
def convert():
    # Parameters from Roblox
    img_url = request.args.get('url')
    res = int(request.args.get('res', 400)) # Defaults to 400 (480p tier)

    if not img_url:
        return "Error: No URL provided", 400

    try:
        # Increase timeout for high-res images
        response = requests.get(img_url, timeout=15)
        response.raise_for_status()
        
        img = Image.open(BytesIO(response.content))
        
        # Ensure the image is in RGB (removes transparency/alpha which can break scripts)
        img = img.convert('RGB')
        
        # High-quality LANCZOS resampling for "non-pixelated" look
        img = img.resize((res, res), Image.Resampling.LANCZOS)
        
        # Efficiently extract pixel data
        pixels = []
        for y in range(res):
            row = []
            for x in range(res):
                # Gets (R, G, B) tuple
                r, g, b = img.getpixel((x, y))
                row.append([r, g, b])
            pixels.append(row)
            
        logging.info(f"Successfully processed {res}x{res} image.")
        return jsonify(pixels)

    except Exception as e:
        logging.error(f"Failed to process image: {str(e)}")
        return f"Server Error: {str(e)}", 500

if __name__ == "__main__":
    # Render requires host 0.0.0.0 to be visible to the web
    app.run(host='0.0.0.0', port=8080)

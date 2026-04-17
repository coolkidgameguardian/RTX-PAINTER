from flask import Flask, request, jsonify
from PIL import Image
import requests
from io import BytesIO

app = Flask(__name__)

@app.route('/convert')
def convert_image():
    # 1. Get the Image Link and Resolution from the Roblox request
    img_url = request.args.get('url')
    # Defaulting to 60 for mobile stability
    resolution = int(request.args.get('res', 60)) 

    if not img_url:
        return "Error: No image URL provided", 400

    try:
        # 2. Download the image from Discord/Imgur
        response = requests.get(img_url, timeout=10)
        img = Image.open(BytesIO(response.content))
        
        # 3. Resize it (e.g., to 60x60) and make it RGB
        img = img.resize((resolution, resolution), Image.Resampling.LANCZOS).convert('RGB')
        
        # 4. Loop through every pixel and grab the [R, G, B]
        pixel_map = []
        for y in range(resolution):
            row = []
            for x in range(resolution):
                r, g, b = img.getpixel((x, y))
                row.append([r, g, b])
            pixel_map.append(row)
            
        # 5. Send that giant list back to your Roblox Executor
        return jsonify(pixel_map)

    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    # Standard port for hosting services
    app.run(host='0.0.0.0', port=8080)

import re
import os

frontend_dir = r"c:\Users\B K SHANTHI\Desktop\Crop advisory system\Crop advisory system\frontend\src"

fixes = {
    "AutomaticDashboard.js": [
        ("const response = await fetch('http://localhost:5000\r\n        method: 'POST',", "const response = await fetch('http://localhost:5000/api/comprehensive-analysis', {\r\n        method: 'POST',"),
        ("'https:\r\n      'wheat': 'https:", "'https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=400',\r\n      'wheat': 'https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=400',"),
    ],
    "FarmerChatbot.js": [
        ('const response = await axios.post(\r\n          "http://localhost:5000\r\n          { image: reader.result },', 'const response = await axios.post(\r\n          "http://localhost:5000/api/detect-disease",\r\n          { image: reader.result },'),
        ('"http://localhost:5000\r\n        { ', '"http://localhost:5000/api/translate",\r\n        { '),
        ('"http://localhost:5000//localhost:5000/api/rag-chat"', '"http://localhost:5000/api/rag-chat"'),
        ("'http://localhost:5000\r\n            { headers:", "'http://localhost:5000/api/chat-history',\r\n            { headers:"),
    ],
    "GlobalLocationSearch.js": [
        ("const response = await axios.post('http://localhost:5000\r\n        query: query.trim()", "const response = await axios.post('http://localhost:5000/api/search-location', {\r\n        query: query.trim()"),
        ("'http://localhost:5000\r\n            {", "'http://localhost:5000/api/update-location',\r\n            {"),
    ],
    "pages\\Dashboard.js": [
        ("fetch('http://localhost:5000\r\n      .then(res => res.json())", "fetch('http://localhost:5000/api/price-analysis')\r\n      .then(res => res.json())"),
    ],
    "pages\\History.js": [
        ('const response = await axios.get("http://localhost:5000\r\n        headers:', 'const response = await axios.get("http://localhost:5000/api/history", {\r\n        headers:'),
        ('await axios.delete("http://localhost:5000\r\n        headers:', 'await axios.delete("http://localhost:5000/api/history", {\r\n        headers:'),
    ],
    "pages\\Login.js": [
        ('const response = await axios.post("http://localhost:5000\r\n      localStorage.setItem', 'const response = await axios.post("http://localhost:5000/api/login", { email, password });\r\n      localStorage.setItem'),
    ],
    "pages\\Register.js": [
        ('await axios.post("http://localhost:5000\r\n      setMessage', 'await axios.post("http://localhost:5000/api/register", { email, password });\r\n      setMessage'),
    ],
}

for filename, replacements in fixes.items():
    filepath = os.path.join(frontend_dir, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for old, new in replacements:
            if old in content:
                content = content.replace(old, new)
                print(f"Fixed in {filename}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] Updated {filename}")
    else:
        print(f"[ERROR] File not found: {filepath}")

print("\nAll URL fixes applied!")

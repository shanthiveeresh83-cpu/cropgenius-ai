# 📍 Location-Based Crop Advisory - Implementation Guide

## 🎯 Overview
Automatic location detection system for personalized crop recommendations based on user's geographical location.

---

## 🗄️ 1. Database Schema Update

### Add Location Columns to Users Table

```sql
-- Run this migration
ALTER TABLE users ADD COLUMN latitude REAL;
ALTER TABLE users ADD COLUMN longitude REAL;
ALTER TABLE users ADD COLUMN district TEXT;
ALTER TABLE users ADD COLUMN state TEXT;
ALTER TABLE users ADD COLUMN city TEXT;
ALTER TABLE users ADD COLUMN formatted_address TEXT;
ALTER TABLE users ADD COLUMN location_updated_at DATETIME;
```

---

## 🔧 2. Backend Setup

### Step 1: Install Dependencies

```bash
pip install requests geopy
```

### Step 2: Get API Key

**Option A: OpenCage Geocoding (Recommended - Free tier: 2,500 requests/day)**
1. Sign up at https://opencagedata.com/
2. Get your API key
3. Add to `.env` file:
```
OPENCAGE_API_KEY=your_api_key_here
```

**Option B: Google Geocoding API**
```
GOOGLE_MAPS_API_KEY=your_api_key_here
```

### Step 3: Register Location Blueprint

Add to `app.py`:

```python
from routes.location import location_bp

app.register_blueprint(location_bp, url_prefix="/location")
```

### Step 4: Update Database Initialization

Add to `init_db()` function in `app.py`:

```python
# Add location columns if they don't exist
cursor.execute("PRAGMA table_info(users)")
existing_columns = {row[1] for row in cursor.fetchall()}

location_columns = {
    "latitude": "REAL",
    "longitude": "REAL",
    "district": "TEXT",
    "state": "TEXT",
    "city": "TEXT",
    "formatted_address": "TEXT",
    "location_updated_at": "DATETIME"
}

for column_name, column_type in location_columns.items():
    if column_name not in existing_columns:
        cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
```

---

## 🎨 3. Frontend Setup

### Step 1: Import LocationDetector Component

In your Dashboard or Analysis page:

```javascript
import LocationDetector from '../LocationDetector';

function Dashboard() {
  const [userLocation, setUserLocation] = useState(null);

  const handleLocationDetected = (location) => {
    setUserLocation(location);
    console.log('User location:', location);
    // Use location for weather/crop recommendations
  };

  return (
    <div>
      <LocationDetector onLocationDetected={handleLocationDetected} />
      {/* Rest of your dashboard */}
    </div>
  );
}
```

### Step 2: Use Location in Predictions

Update your prediction API call to include location:

```javascript
const handleAutoPredict = async () => {
  const token = localStorage.getItem("token");
  
  const response = await axios.post(
    "http://127.0.0.1:5000/predict",
    { 
      location: {
        lat: userLocation?.latitude,
        lon: userLocation?.longitude,
        city: userLocation?.city
      }
    },
    { headers: { Authorization: `Bearer ${token}` } }
  );
};
```

---

## 🔐 4. Privacy & Security Best Practices

### User Consent
```javascript
// Always ask for permission before accessing location
const requestLocationPermission = () => {
  if (navigator.geolocation) {
    // Show consent dialog
    const userConsent = window.confirm(
      "This app needs your location to provide personalized crop recommendations. Allow?"
    );
    
    if (userConsent) {
      detectLocation();
    }
  }
};
```

### Privacy Policy Points
1. **Transparency**: Clearly state why location is needed
2. **Control**: Allow users to update/remove location anytime
3. **Security**: Store coordinates encrypted in production
4. **Minimal Data**: Only store necessary location data
5. **Retention**: Delete location data on account deletion

### HTTPS Requirement
```
⚠️ Geolocation API only works on HTTPS (or localhost)
```

---

## 🌐 5. API Endpoints

### POST /location/detect
Detect and save user location from coordinates

**Request:**
```json
{
  "latitude": 28.6139,
  "longitude": 77.2090
}
```

**Response:**
```json
{
  "success": true,
  "message": "Location saved successfully",
  "location": {
    "latitude": 28.6139,
    "longitude": 77.2090,
    "district": "New Delhi",
    "state": "Delhi",
    "city": "New Delhi",
    "formatted_address": "New Delhi, Delhi, India",
    "agricultural_zone": "Northern Plains"
  }
}
```

### PUT /location/update
Manually update user's preferred location

**Request:**
```json
{
  "latitude": 19.0760,
  "longitude": 72.8777,
  "district": "Mumbai",
  "state": "Maharashtra"
}
```

### GET /location/current
Get user's saved location

**Response:**
```json
{
  "success": true,
  "location": {
    "latitude": 28.6139,
    "longitude": 77.2090,
    "district": "New Delhi",
    "state": "Delhi",
    "city": "New Delhi",
    "formatted_address": "New Delhi, Delhi, India",
    "updated_at": "2024-01-15 10:30:00"
  }
}
```

### POST /location/geocode
Convert address to coordinates

**Request:**
```json
{
  "address": "Mumbai, Maharashtra"
}
```

---

## 🚀 6. AWS Deployment (Optional)

### Using AWS Location Service

```python
import boto3

# Initialize AWS Location Service
location_client = boto3.client('location', region_name='ap-south-1')

def reverse_geocode_aws(latitude, longitude):
    response = location_client.search_place_index_for_position(
        IndexName='YourPlaceIndex',
        Position=[longitude, latitude]
    )
    
    place = response['Results'][0]['Place']
    return {
        'district': place.get('Municipality'),
        'state': place.get('Region'),
        'country': place.get('Country')
    }
```

### AWS Services Setup
1. **AWS Location Service**: Reverse geocoding
2. **Amazon RDS**: Store user data
3. **AWS Secrets Manager**: Store API keys
4. **Amazon CloudFront**: HTTPS for geolocation API

---

## 📱 7. Mobile Considerations

### React Native (Future)
```javascript
import Geolocation from '@react-native-community/geolocation';

Geolocation.getCurrentPosition(
  position => {
    const { latitude, longitude } = position.coords;
    saveLocation(latitude, longitude);
  },
  error => console.error(error),
  { enableHighAccuracy: true, timeout: 20000, maximumAge: 1000 }
);
```

---

## 🧪 8. Testing

### Test Location Detection
```javascript
// Mock location for testing
const mockLocation = {
  latitude: 28.6139,
  longitude: 77.2090
};

// Test reverse geocoding
fetch('http://127.0.0.1:5000/location/detect', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_TOKEN'
  },
  body: JSON.stringify(mockLocation)
});
```

---

## 🎯 9. Integration with Crop Prediction

### Update Prediction Service

```python
@predict_bp.route("", methods=["POST"])
@jwt_required()
def predict():
    user_email = get_jwt_identity()
    
    # Get user's saved location
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT latitude, longitude, district, state FROM users WHERE email = ?",
        (user_email,)
    )
    user_data = cursor.fetchone()
    
    if user_data and user_data[0]:
        # Use user's location for weather data
        location = {
            'lat': user_data[0],
            'lon': user_data[1],
            'district': user_data[2],
            'state': user_data[3]
        }
        
        # Fetch weather for user's location
        weather_data = weather_service.get_weather(location)
        
        # Make prediction with location-specific data
        # ...
```

---

## ✅ 10. Checklist

- [ ] Database schema updated with location columns
- [ ] Location service created
- [ ] Location routes registered
- [ ] Frontend component integrated
- [ ] API key configured in .env
- [ ] HTTPS enabled (production)
- [ ] Privacy policy updated
- [ ] User consent implemented
- [ ] Error handling added
- [ ] Testing completed

---

## 🔍 11. Troubleshooting

### Issue: "Geolocation not supported"
**Solution**: Ensure HTTPS or use localhost

### Issue: "Permission denied"
**Solution**: Guide user to enable location in browser settings

### Issue: "Geocoding API limit exceeded"
**Solution**: Implement caching or upgrade API plan

### Issue: "Inaccurate location"
**Solution**: Use `enableHighAccuracy: true` option

---

## 📊 12. Performance Optimization

1. **Cache geocoding results** (24 hours)
2. **Lazy load** location component
3. **Debounce** location updates
4. **Use CDN** for static assets
5. **Compress** API responses

---

## 🎉 Done!

Your Crop Advisory System now has automatic location detection with:
- ✅ Auto-detect user location
- ✅ Reverse geocoding (coordinates → address)
- ✅ Manual location update
- ✅ Persistent storage
- ✅ Privacy-compliant
- ✅ Location-based recommendations

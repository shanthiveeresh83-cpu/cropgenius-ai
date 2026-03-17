# Crop Advisory System - Implementation Plan

## Task Summary
Modify the Flask project to automatically fetch temperature via Weather API and estimate N/P values using ML, while keeping the code modular and production-ready.

## Information Gathered

### Existing Components:
1. **backend/app.py** - Main Flask app with blueprints registered
2. **backend/routes/predict.py** - Already has `/predict/auto` endpoint with automatic weather + nutrient estimation
3. **backend/services/weather_service.py** - OpenWeatherMap integration with fallback
4. **backend/services/nutrient_estimator.py** - ML model for N/P estimation with fallback
5. **backend/REQUIREMENTS.txt** - All required dependencies listed

### Key Features Already Implemented:
- Weather API integration with OpenWeatherMap
- ML-based nutrient (N, P) estimation
- Fallback data when API/model unavailable
- Blueprint structure for modular routes

## Plan

### Phase 1: Environment Configuration
- [ ] Create `.env.example` file with all required environment variables

### Phase 2: Update predict.py Route
- [ ] Modify `/predict` route to support hybrid mode (auto-fetch when N/P/temperature not provided)
- [ ] Add clear documentation and comments
- [ ] Ensure proper error handling

### Phase 3: Create Example Files
- [ ] Create `.env` configuration example
- [ ] Update REQUIREMENTS.txt if needed
- [ ] Add usage examples in code comments

### Phase 4: Testing & Validation
- [ ] Verify route works with manual input
- [ ] Verify auto-fetch works when values missing

## Files to Modify
1. `backend/routes/predict.py` - Main route updates
2. Create `backend/.env.example` - Environment configuration template

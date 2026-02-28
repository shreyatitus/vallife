# LifeLink - Blood Donation Platform with AI Assistant

## 🚀 Quick Start

### 1. Start Backend Server
Double-click `START_BACKEND.bat` or run:
```bash
cd valkyire\lifelink_backend\lifelink_backend
python app_firebase.py
```

### 2. Start Frontend Server
Double-click `START_FRONTEND.bat` or run:
```bash
cd valkyire\lifelink_frontend\lifelink_frontend
python -m http.server 8000
```

### 3. Access the Application
- **Frontend**: http://localhost:8000
- **Backend API**: http://localhost:5000
- **Admin Panel**: http://localhost:8000/admin-login.html
  - Username: `admin`
  - Password: `admin123`

## 📋 Features

### ✅ Implemented Features
1. **User Registration with Verification**
   - Age validation (18-65 years)
   - Weight validation (≥50 kg)
   - Height validation (≥150 cm)
   - Blood test report validation (within 90 days)
   - Admin approval required

2. **AI-Powered Blood Request System**
   - Conversational AI collects patient details
   - Automatic location geocoding (text → coordinates)
   - Smart donor matching by blood type
   - Distance calculation using Haversine formula
   - 90-day cooldown period checking
   - Automatic email notifications to matched donors

3. **Admin Dashboard**
   - View pending registrations
   - Approve/reject users
   - View blood test report dates

4. **Email Notifications**
   - Registration approval emails
   - Blood donation request emails to matched donors

## 🔧 System Requirements

### Required Python Packages
```bash
pip install flask flask-cors firebase-admin groq requests
```

### Firebase Setup
- Project: `lifelink-a1172`
- Firestore API must be enabled
- Service account key: `firebase-key.json`

### API Keys
- **Groq API**: `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`
- **Email SMTP**: maryreshma777@gmail.com

## 📁 Project Structure

```
vallife/
├── START_BACKEND.bat          # Quick start backend
├── START_FRONTEND.bat         # Quick start frontend
├── SETUP_GUIDE.md            # This file
└── valkyire/
    ├── lifelink_backend/
    │   └── lifelink_backend/
    │       ├── app_firebase.py           # Main backend
    │       ├── firebase-key.json         # Firebase credentials
    │       └── services/
    │           ├── groq_assistant.py     # AI chat
    │           ├── ai_donor_matcher.py   # Donor matching
    │           ├── email_service.py      # Email sender
    │           └── geocoding_service.py  # Location → coordinates
    └── lifelink_frontend/
        └── lifelink_frontend/
            ├── index.html                # Landing page
            ├── register.html             # User registration
            ├── login.html                # User login
            ├── chat.html                 # AI assistant
            ├── admin-login.html          # Admin login
            └── admin-verify-users.html   # Admin panel
```

## 🤖 AI Assistant Workflow

1. User opens chat at http://localhost:8000/chat.html
2. AI asks for:
   - Patient name
   - Blood type (A+, A-, B+, B-, O+, O-, AB+, AB-)
   - Hospital name
   - Location (city/area)
3. System automatically:
   - Geocodes location to coordinates
   - Finds donors with matching blood type
   - Checks 90-day cooldown eligibility
   - Calculates distance to each donor
   - Ranks by nearest distance
   - Sends email to closest eligible donor
4. User sees confirmation with donor details

## 📧 Email Configuration

Current SMTP settings (Gmail):
- Server: smtp.gmail.com:587
- Email: maryreshma777@gmail.com
- App Password: wqxp nfye ilqj fexj

## 🔍 Troubleshooting

### Backend won't start
- Check if port 5000 is available
- Verify firebase-key.json exists
- Check Firebase credentials

### CORS errors
- Ensure backend is running on port 5000
- Access frontend via http://localhost:8000 (not file://)
- Check browser console for specific errors

### Geocoding returns (0, 0)
- Check backend console for geocoding logs
- Verify internet connection
- OpenStreetMap API may be rate-limited

### Email not sending
- Check SMTP credentials
- Verify email service logs in backend console
- Gmail may block less secure apps

### No donors found
- Ensure Firestore API is enabled in Firebase Console
- Add sample donors using add_sample_data.py
- Check donor blood type matches request

## 📊 Database Collections

### users
- name, email, phone, age, weight, height
- blood, password, latitude, longitude
- reportData, reportName, reportDate
- status (pending/approved), donations, points

### requests
- patientName, blood, hospital, location
- latitude, longitude, status, created_at

### notifications
- donor_id, request_id, patient_name
- blood_type, hospital, status, created_at

## 🎯 Testing the System

1. **Register a donor**:
   - Go to http://localhost:8000/register.html
   - Fill form with valid data
   - Upload blood test report (within 90 days)

2. **Approve donor (Admin)**:
   - Go to http://localhost:8000/admin-login.html
   - Login: admin/admin123
   - Approve pending user

3. **Create blood request**:
   - Go to http://localhost:8000/chat.html
   - Chat with AI: "I need blood"
   - Provide details when asked
   - Check backend console for geocoding
   - Verify email sent to donor

## 🔐 Security Notes

- Passwords stored in plain text (use hashing in production)
- API keys exposed (use environment variables in production)
- CORS allows all origins (restrict in production)
- No rate limiting (add in production)

## 📝 Admin Credentials

- Username: `admin`
- Password: `admin123`

## 🌐 Ports

- Backend: 5000
- Frontend: 8000

## ✨ Key Technologies

- **Backend**: Flask, Firebase Firestore
- **AI**: Groq (Llama 3.3 70B)
- **Geocoding**: OpenStreetMap Nominatim
- **Email**: SMTP (Gmail)
- **Frontend**: Vanilla HTML/CSS/JavaScript

## 📞 Support

Check backend console for detailed logs including:
- Firebase connection status
- AI responses
- Geocoding results
- Email sending status
- Donor matching results

# 🔐 OTP Email Verification System (Python)

A beautiful, production-ready OTP (One-Time Password) email verification system with a premium dark theme UI and robust Python backend.

## ✨ Features

- **Email Registration**: Users can register their email addresses
- **OTP Generation**: Automatic 6-digit OTP generation
- **Email Delivery**: OTP sent via Gmail SMTP using Python's smtplib
- **Secure Verification**: Time-based OTP validation (5-minute expiry)
- **Premium UI**: Modern dark theme with glassmorphism and smooth animations
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Error Handling**: Comprehensive error messages and validation

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Gmail account with App Password enabled

### Installation

1. **Clone or download the project**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Gmail credentials:
   ```env
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASS=your-app-password-here
   PORT=3000
   ```

### Gmail App Password Setup

> [!IMPORTANT]
> You **cannot** use your regular Gmail password. You must create an App Password.

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** (if not already enabled)
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Select **Mail** as the app and **Other** as the device
5. Enter "OTP System" as the name
6. Click **Generate**
7. Copy the 16-character password (remove spaces)
8. Paste it in your `.env` file as `EMAIL_PASS`

### Running the Application

1. **Start the backend server**
   ```bash
   python app.py
   ```
   
   You should see:
   ```
   🚀 OTP Verification Server running on http://localhost:3000
   📧 Email service: your-email@gmail.com
   ✅ Email server is ready to send messages
   ```

2. **Open the frontend**
   
   The Flask server serves the frontend automatically. Just open your browser and go to:
   ```
   http://localhost:3000
   ```

## 📖 How It Works

### User Flow

1. **Email Registration**
   - User enters their email address
   - Clicks "Send OTP"

2. **OTP Delivery**
   - System generates a 6-digit OTP
   - OTP is sent to the user's email
   - OTP expires after 5 minutes

3. **Verification**
   - User enters the OTP received in email
   - Clicks "Verify OTP"
   - System validates the OTP
   - Success message displayed on verification

4. **Error Handling**
   - Invalid email format
   - OTP expiration
   - Incorrect OTP
   - Network errors

### Technical Flow

```
Frontend (HTML/CSS/JS)
    ↓
POST /api/send-otp { email }
    ↓
Backend generates OTP
    ↓
Nodemailer sends email via Gmail SMTP
    ↓
User receives OTP
    ↓
POST /api/verify-otp { email, otp }
    ↓
Backend validates OTP
    ↓
Success/Error response
```

## 🛠️ API Documentation

### Base URL
```
http://localhost:3000/api
```

### Endpoints

#### 1. Send OTP
```http
POST /api/send-otp
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Success Response (200)**
```json
{
  "success": true,
  "message": "OTP sent successfully to your email",
  "expiresIn": 300
}
```

**Error Response (400/500)**
```json
{
  "success": false,
  "message": "Error message here"
}
```

#### 2. Verify OTP
```http
POST /api/verify-otp
Content-Type: application/json

{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Success Response (200)**
```json
{
  "success": true,
  "message": "Email verified successfully!"
}
```

**Error Response (400/500)**
```json
{
  "success": false,
  "message": "Invalid OTP. Please check and try again."
}
```

#### 3. Health Check
```http
GET /api/health
```

**Response (200)**
```json
{
  "status": "ok",
  "timestamp": "2026-02-04T01:58:57.000Z",
  "activeOTPs": 2
}
```

## 🎨 Project Structure

```
otp/
├── index.html          # Main HTML file
├── style.css           # Styling with dark theme
├── script.js           # Frontend JavaScript
├── app.py              # Flask backend server (Python)
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .env                # Your actual credentials (create this)
└── README.md           # Documentation
```

## 🔒 Security Features

- ✅ OTP expiration (5 minutes)
- ✅ Automatic cleanup of expired OTPs
- ✅ Email validation
- ✅ Input sanitization
- ✅ CORS protection
- ✅ Secure Gmail App Password usage

## 🐛 Troubleshooting

### "Email configuration error"
- Verify your `.env` file exists
- Check that `EMAIL_USER` and `EMAIL_PASS` are set correctly
- Ensure you're using an App Password, not your regular Gmail password

### "Failed to send OTP"
- Check your internet connection
- Verify Gmail credentials
- Check if 2-Step Verification is enabled
- Ensure the App Password is correct (16 characters, no spaces)
- Check Python console for detailed error messages

### "OTP has expired"
- Request a new OTP
- OTPs are valid for 5 minutes only

### Frontend not connecting to backend
- Ensure Flask server is running on port 3000
- Navigate to `http://localhost:3000` (not `file:///...`)
- Check browser console for error messages

### Python/pip issues
- Ensure Python 3.7+ is installed: `python --version`
- Update pip: `python -m pip install --upgrade pip`
- Use virtual environment (recommended):
  ```bash
  python -m venv venv
  venv\Scripts\activate  # Windows
  source venv/bin/activate  # Linux/Mac
  pip install -r requirements.txt
  ```

## 🚀 Production Deployment

### For Production Use:

1. **Use a database** (MongoDB, PostgreSQL, Redis) instead of in-memory storage
2. **Add rate limiting** to prevent abuse
3. **Use environment-specific configs**
4. **Add logging** (Winston, Morgan)
5. **Use HTTPS** for secure communication
6. **Add user authentication** system
7. **Implement email templates** with branding
8. **Add analytics** for monitoring

## 📝 License

ISC

## 💡 Support

If you encounter any issues, please check:
1. Node.js version (v14+)
2. Gmail App Password setup
3. `.env` file configuration
4. Console logs for errors

---

Made with ❤️ for secure email verification

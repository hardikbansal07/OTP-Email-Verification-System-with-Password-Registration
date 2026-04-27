import os
import random
import smtplib
import time
import sqlite3
import bcrypt
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Thread, Lock
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='.')
CORS(app)

# Configuration
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')
PORT = int(os.getenv('PORT', 3000))

# In-memory OTP storage (in production, use Redis or database)
otp_store = {}
otp_lock = Lock()

# Database setup
DB_NAME = 'users.db'

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            verified INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print('✅ Database initialized')

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, password_hash):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def get_user_by_email(email):
    """Get user from database by email"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(email, password):
    """Create new user in database"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        password_hash = hash_password(password)
        cursor.execute(
            'INSERT INTO users (email, password_hash) VALUES (?, ?)',
            (email, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        return None  # User already exists

def generate_otp():
    """Generate a random 6-digit OTP"""
    return str(random.randint(100000, 999999))

def cleanup_expired_otps():
    """Remove expired OTPs from storage"""
    with otp_lock:
        current_time = time.time()
        expired_emails = [
            email for email, data in otp_store.items()
            if current_time > data['expiry']
        ]
        for email in expired_emails:
            del otp_store[email]
            print(f"🗑️  Cleaned up expired OTP for {email}")

def cleanup_loop():
    """Background thread to cleanup expired OTPs every minute"""
    while True:
        time.sleep(60)  # Run every minute
        cleanup_expired_otps()

def send_email(to_email, otp):
    """Send OTP email using Gmail SMTP"""
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f'"OTP Verification System" <{EMAIL_USER}>'
        msg['To'] = to_email
        msg['Subject'] = 'Your OTP Verification Code'

        # HTML email content
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{
      font-family: 'Arial', sans-serif;
      background-color: #f4f4f4;
      margin: 0;
      padding: 20px;
    }}
    .container {{
      max-width: 600px;
      margin: 0 auto;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 20px;
      padding: 40px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }}
    .content {{
      background: rgba(255, 255, 255, 0.95);
      border-radius: 15px;
      padding: 30px;
      text-align: center;
    }}
    h1 {{
      color: #667eea;
      margin: 0 0 20px 0;
      font-size: 28px;
    }}
    .otp-box {{
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      font-size: 42px;
      font-weight: bold;
      letter-spacing: 8px;
      padding: 20px;
      border-radius: 10px;
      margin: 30px 0;
      font-family: 'Courier New', monospace;
    }}
    p {{
      color: #555;
      font-size: 16px;
      line-height: 1.6;
      margin: 15px 0;
    }}
    .warning {{
      color: #e74c3c;
      font-size: 14px;
      margin-top: 20px;
    }}
    .footer {{
      color: rgba(255, 255, 255, 0.8);
      font-size: 12px;
      margin-top: 30px;
      text-align: center;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="content">
      <h1>🔐 Email Verification</h1>
      <p>Your One-Time Password (OTP) is:</p>
      <div class="otp-box">{otp}</div>
      <p>This OTP is valid for <strong>5 minutes</strong>.</p>
      <p>Please enter this code to complete your verification.</p>
      <p class="warning">⚠️ Do not share this code with anyone!</p>
    </div>
    <div class="footer">
      <p>If you didn't request this code, please ignore this email.</p>
    </div>
  </div>
</body>
</html>
"""
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        # Connect to GoDaddy SMTP server (Professional Email)
        with smtplib.SMTP('smtpout.secureserver.net', 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        raise e

# API Routes
@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    """Generate and send OTP to email"""
    try:
        data = request.get_json()
        email = data.get('email')

        if not email or '@' not in email:
            return jsonify({
                'success': False,
                'message': 'Please provide a valid email address'
            }), 400

        # Check if user already exists in database
        existing_user = get_user_by_email(email)
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'This email is already registered. Please login instead.',
                'userExists': True
            }), 400

        # Generate OTP
        otp = generate_otp()
        expiry = time.time() + (5 * 60)  # 5 minutes from now

        # Store OTP
        with otp_lock:
            otp_store[email] = {
                'otp': otp,
                'expiry': expiry
            }
        
        print(f"📨 Generated OTP {otp} for {email} (expires in 5 minutes)")

        # Send email
        send_email(email, otp)
        print(f"✅ OTP email sent successfully to {email}")

        return jsonify({
            'success': True,
            'message': 'OTP sent successfully to your email',
            'expiresIn': 300  # 5 minutes in seconds
        })

    except Exception as e:
        print(f"❌ Error in send_otp: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to send OTP. Please try again.',
            'error': str(e)
        }), 500

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP entered by user"""
    try:
        data = request.get_json()
        email = data.get('email')
        otp = data.get('otp')

        if not email or not otp:
            return jsonify({
                'success': False,
                'message': 'Email and OTP are required'
            }), 400

        # Get stored OTP
        with otp_lock:
            stored_data = otp_store.get(email)

        if not stored_data:
            return jsonify({
                'success': False,
                'message': 'No OTP found for this email. Please request a new one.'
            }), 400

        # Check if OTP is expired
        if time.time() > stored_data['expiry']:
            with otp_lock:
                del otp_store[email]
            return jsonify({
                'success': False,
                'message': 'OTP has expired. Please request a new one.'
            }), 400

        # Verify OTP
        if stored_data['otp'] == otp.strip():
            with otp_lock:
                del otp_store[email]  # Remove OTP after successful verification
            print(f"✅ OTP verified successfully for {email}")
            
            return jsonify({
                'success': True,
                'message': 'Email verified successfully!'
            })
        else:
            print(f"❌ Invalid OTP attempt for {email}")
            return jsonify({
                'success': False,
                'message': 'Invalid OTP. Please check and try again.'
            }), 400

    except Exception as e:
        print(f"❌ Error in verify_otp: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Verification failed. Please try again.'
        }), 500

@app.route('/api/register', methods=['POST'])
def register():
    """Register new user with email and password"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400

        # Validate password strength
        if len(password) < 8:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 8 characters long'
            }), 400

        # Check if user already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'User with this email already exists'
            }), 400

        # Create user
        user_id = create_user(email, password)
        if user_id:
            print(f"✅ User registered successfully: {email}")
            return jsonify({
                'success': True,
                'message': 'Registration successful! You can now login.'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Registration failed. Please try again.'
            }), 500

    except Exception as e:
        print(f"❌ Error in register: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Registration failed. Please try again.'
        }), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login with email and password"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400

        # Get user from database
        user = get_user_by_email(email)
        if not user:
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401

        # user tuple: (id, email, password_hash, verified, created_at)
        user_id, user_email, password_hash, verified, created_at = user

        # Verify password
        if verify_password(password, password_hash):
            print(f"✅ User logged in successfully: {email}")
            return jsonify({
                'success': True,
                'message': 'Login successful!',
                'user': {
                    'id': user_id,
                    'email': user_email,
                    'created_at': created_at
                }
            })
        else:
            print(f"❌ Invalid password attempt for {email}")
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401

    except Exception as e:
        print(f"❌ Error in login: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Login failed. Please try again.'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    conn.close()
    
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'activeOTPs': len(otp_store),
        'totalUsers': user_count
    })

# Serve static files
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Verify email configuration
    if not EMAIL_USER or not EMAIL_PASS:
        print('❌ Email configuration error: EMAIL_USER or EMAIL_PASS not set')
        print('\n📧 Please configure your .env file with valid Gmail credentials')
        print('Copy .env.example to .env and add your credentials\n')
    else:
        print('✅ Email server is ready to send messages')
    
    # Start cleanup thread
    cleanup_thread = Thread(target=cleanup_loop, daemon=True)
    cleanup_thread.start()
    
    # Start Flask server
    print(f'\n🚀 OTP Verification Server running on http://localhost:{PORT}')
    print(f'📧 Email service: {EMAIL_USER or "Not configured"}\n')
    
    app.run(host='0.0.0.0', port=PORT, debug=True)

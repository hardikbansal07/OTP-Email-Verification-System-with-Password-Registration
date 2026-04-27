import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

EMAIL = os.getenv('EMAIL_USER')
PASSWORD = os.getenv('EMAIL_PASS')

print("=" * 70)
print("Simple SMTP SSL Test")
print("=" * 70)
print(f"Email: {EMAIL}")
print(f"Password: {'*' * len(PASSWORD)}")
print(f"Server: smtpout.secureserver.net:465")
print("=" * 70)

try:
    msg = MIMEText("SMTP SSL test working")
    msg["Subject"] = "GoDaddy SMTP SSL Test"
    msg["From"] = EMAIL
    msg["To"] = EMAIL

    print("\nConnecting to SMTP server...")
    server = smtplib.SMTP_SSL("smtpout.secureserver.net", 465)
    print("✅ Connected!")
    
    print("Logging in...")
    server.login(EMAIL, PASSWORD)
    print("✅ Login successful!")
    
    print("Sending email...")
    server.send_message(msg)
    print("✅ Email sent!")
    
    server.quit()

    print("\n" + "=" * 70)
    print("🎉 Email Sent Successfully!")
    print("=" * 70)
    
    # Write success to file
    with open('email_test_result.txt', 'w') as f:
        f.write("✅ SUCCESS! SMTP Working!\n")
        f.write("=" * 70 + "\n")
        f.write(f"Email: {EMAIL}\n")
        f.write("Server: smtpout.secureserver.net:465\n")
        f.write("\nTest email sent successfully!\n")

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print(f"Error Type: {type(e).__name__}")
    
    # Write error to file
    with open('email_test_result.txt', 'w') as f:
        f.write(f"❌ FAILED\n")
        f.write("=" * 70 + "\n")
        f.write(f"Error: {str(e)}\n")
        f.write(f"Error Type: {type(e).__name__}\n")
    
    print("\n" + "=" * 70)
    print("Test Failed!")
    print("=" * 70)

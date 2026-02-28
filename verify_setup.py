import os
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("LifeLink System Verification")
print("=" * 60)

# Check Python version
print(f"\n[OK] Python version: {sys.version.split()[0]}")

# Check required files
files_to_check = [
    "valkyire/lifelink_backend/lifelink_backend/app_firebase.py",
    "valkyire/lifelink_backend/lifelink_backend/firebase-key.json",
    "valkyire/lifelink_backend/lifelink_backend/services/groq_assistant.py",
    "valkyire/lifelink_backend/lifelink_backend/services/ai_donor_matcher.py",
    "valkyire/lifelink_backend/lifelink_backend/services/email_service.py",
    "valkyire/lifelink_backend/lifelink_backend/services/geocoding_service.py",
    "valkyire/lifelink_frontend/lifelink_frontend/chat.html",
    "valkyire/lifelink_frontend/lifelink_frontend/register.html",
    "START_BACKEND.bat",
    "START_FRONTEND.bat"
]

print("\nChecking required files:")
all_files_exist = True
for file in files_to_check:
    if os.path.exists(file):
        print(f"  [OK] {file}")
    else:
        print(f"  [MISSING] {file}")
        all_files_exist = False

# Check required packages
print("\nChecking required packages:")
required_packages = ["flask", "flask_cors", "firebase_admin", "groq", "requests"]
missing_packages = []

for package in required_packages:
    try:
        __import__(package)
        print(f"  [OK] {package}")
    except ImportError:
        print(f"  [MISSING] {package}")
        missing_packages.append(package)

# Summary
print("\n" + "=" * 60)
if all_files_exist and not missing_packages:
    print("[SUCCESS] ALL CHECKS PASSED!")
    print("\nYou can now start the application:")
    print("  1. Double-click START_BACKEND.bat")
    print("  2. Double-click START_FRONTEND.bat")
    print("  3. Open http://localhost:8000")
else:
    print("[WARNING] ISSUES FOUND!")
    if not all_files_exist:
        print("\n  Some files are missing. Check the file paths.")
    if missing_packages:
        print(f"\n  Install missing packages:")
        print(f"  pip install {' '.join(missing_packages)}")

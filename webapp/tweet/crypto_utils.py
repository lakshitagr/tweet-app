from cryptography.fernet import Fernet

# Hardcoded key – safe for development
SECRET_KEY = b'yYguT3HuW7DpPfzYoBvLbGeO6MDlyFKQKDmXNtt1ZAI='

fernet = Fernet(SECRET_KEY)

def encrypt_text(text):
    return fernet.encrypt(text.encode())  # ✅ return bytes

def decrypt_text(token):
    return fernet.decrypt(token).decode()  # ✅ takes bytes, returns string

def encrypt_image(image_file):
    return fernet.encrypt(image_file.read())  # returns bytes

def decrypt_image(binary_data):
    return fernet.decrypt(binary_data)  # returns bytes


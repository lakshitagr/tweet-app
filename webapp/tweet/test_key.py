from cryptography.fernet import Fernet

# Load encrypted image
with open('db.sqlite3-x-tweet_tweet-5-encrypted_photo.bin', 'rb') as f:
    encrypted_image = f.read()

#WRONG_KEY
#WRONG_SECRET_KEY = 'ZT47tiF8XeUl9ClgDxx-rz3KciZh3pGcpn2ChPFg9gk='

# Correct key
SECRET_KEY = 'yYguT3HuW7DpPfzYoBvLbGeO6MDlyFKQKDmXNtt1ZAI='

fernet = Fernet(SECRET_KEY)

try:
    # Decrypt the image
    decrypted_image = fernet.decrypt(encrypted_image)

    # Save the decrypted binary data to a file
    with open('decrypted_image.jpg', 'wb') as img_file:
        img_file.write(decrypted_image)

    print("✅ Image decrypted and saved as 'decrypted_image.jpg'. You can now open it.")

except Exception as e: 
    print("❌ Failed to decrypt the image:", e)

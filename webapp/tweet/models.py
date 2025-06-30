from django.db import models
from django.contrib.auth.models import User
from .crypto_utils import encrypt_text, decrypt_text, encrypt_image, decrypt_image


class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    encrypted_text = models.BinaryField(default=b'')
    encrypted_photo = models.BinaryField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   

    def __str__(self):
        try:
            return f'{self.user.username} - {self.text[:20]}'
        except Exception:
            return f'{self.user.username} - <decryption failed>'

    # 🔐 Access encrypted text as a property
    @property
    def text(self):
        if self.encrypted_text:
            return decrypt_text(self.encrypted_text)
        return ""

    @text.setter
    def text(self, value):
        if value:
            self.encrypted_text = encrypt_text(value)

    # 🔐 Set encrypted image manually
    def set_photo(self, image):
        if image:
            self.encrypted_photo = encrypt_image(image)

    # 🔐 Decrypt image for view or display
    def get_photo_bytes(self):
        if self.encrypted_photo:
            return decrypt_image(self.encrypted_photo)
        return None



class WebAuthnCredential(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    credential_id = models.CharField(max_length=255, unique=True)
    public_key = models.TextField()
    sign_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

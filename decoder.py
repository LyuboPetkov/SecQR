
import os
import binascii
import cv2
import numpy as np
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
FIXED_IV = os.getenv('FIXED_IV')

if not ENCRYPTION_KEY or not FIXED_IV:
    raise EnvironmentError("Missing encryption key or IV in environment variables")

ENCRYPTION_KEY = ENCRYPTION_KEY.encode()
FIXED_IV = binascii.unhexlify(FIXED_IV)

def calculate_region():
    start_x, start_y = 11, 12
    region_width, region_height = 22, 22
    return start_x, start_y, region_width, region_height

def apply_custom_mask(qr_matrix, start_x, start_y, region_width, region_height):
    for i in range(region_height):
        for j in range(region_width):
            qr_matrix[start_y + i, start_x + j] ^= 1
    return qr_matrix

def decrypt_message(encrypted_message, key, iv):
    cipher = Cipher(algorithms.AES(key), modes.OFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(encrypted_message) + decryptor.finalize()

def extract_secret_message(qr_matrix, start_x, start_y, region_width, region_height):
    try:
        secret_bits = []
        for i in range(region_height):
            for j in range(region_width):
                secret_bits.append(str(int(qr_matrix[start_y + i, start_x + j])))
        secret_bits = ''.join(secret_bits)

        secret_data = bytes([int(secret_bits[i:i+8], 2) for i in range(0, len(secret_bits), 8)])
        length_str = secret_data[:2].decode()

        if not length_str.isdigit() or secret_data[2:3].decode() != '|':
            return "n!Sect33v||||???~~a122s0m,./"

        length = int(length_str)
        encrypted_message = secret_data[3:3+length]

        decrypted_message = decrypt_message(encrypted_message, ENCRYPTION_KEY, FIXED_IV)
        return decrypted_message.decode()
    except (IndexError, ValueError):
        return "n!Sect33v||||???~~a122s0m,./"

def decode_qr_matrix(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)
    if not data:
        return "n0!0kbnsqr,c0d||c3e.,?s"
    return data

def decode_secret_message(image_path):
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        detector = cv2.QRCodeDetector()
        retval, decoded_info, points, straight_qrcode = detector.detectAndDecodeMulti(img)
        if not retval or len(straight_qrcode) == 0:
            return "n!Sect33v||||???~~a122s0m,./"

        qr_matrix = (straight_qrcode[0] < 128).astype(int)
        matrix_size = qr_matrix.shape[0]
        
        start_x, start_y, region_width, region_height = calculate_region()
        
        qr_matrix = apply_custom_mask(qr_matrix, start_x, start_y, region_width, region_height)
        secret_message = extract_secret_message(qr_matrix, start_x, start_y, region_width, region_height)
        
        return secret_message
    except IndexError:
        return "n!Sect33v||||???~~a122s0m,./"

def decode_qr(image_path):
    normal_message = decode_qr_matrix(image_path)
    secret_message = decode_secret_message(image_path)
    if normal_message == "n0!0kbnsqr,c0d||c3e.,?s": 
        secret_message = ""
        
    return normal_message, secret_message

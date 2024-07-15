import os
import binascii
import qrcode
import numpy as np
from PIL import Image
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

# Load environment variables from .env file
load_dotenv()

ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
FIXED_IV = os.getenv('FIXED_IV')

if not ENCRYPTION_KEY or not FIXED_IV:
    raise EnvironmentError("Missing encryption key or IV in environment variables")

ENCRYPTION_KEY = ENCRYPTION_KEY.encode()
FIXED_IV = binascii.unhexlify(FIXED_IV)

def create_qr_v8(data):
    qr = qrcode.QRCode(
        version=8,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=False)
    return qr

def get_qr_matrix(qr):
    return np.array(qr.get_matrix())

def calculate_region():
    start_x, start_y = 15, 16
    region_width, region_height = 22, 22
    return start_x, start_y, region_width, region_height

def encrypt_message(message, key, iv):
    cipher = Cipher(algorithms.AES(key), modes.OFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(message.encode()) + encryptor.finalize()

def embed_secret_message(qr_matrix, secret_message, start_x, start_y, region_width, region_height):
    if len(secret_message) > 57:
        raise ValueError("Secret message is too long. Maximum length is 57 characters.")
    
    encrypted_message = encrypt_message(secret_message, ENCRYPTION_KEY, FIXED_IV)
    length_info = f"{len(encrypted_message):02}|"
    full_message = length_info.encode() + encrypted_message
    bit_data = ''.join(format(byte, '08b') for byte in full_message)
    index = 0
    for i in range(region_height):
        for j in range(region_width):
            if index < len(bit_data):
                qr_matrix[start_y + i, start_x + j] = int(bit_data[index])
                index += 1
    return qr_matrix

def apply_custom_mask(qr_matrix, start_x, start_y, region_width, region_height):
    for i in range(region_height):
        for j in range(region_width):
            qr_matrix[start_y + i, start_x + j] ^= 1
    return qr_matrix

def save_qr_matrix_as_png(qr_matrix, path, box_size=10, border=4):
    matrix_size = len(qr_matrix)
    size = (matrix_size + border * 2) * box_size
    img = Image.new('1', (size, size), 1)
    pixels = img.load()

    for r in range(matrix_size):
        for c in range(matrix_size):
            if qr_matrix[r, c] == 1:
                for i in range(box_size):
                    for j in range(box_size):
                        pixels[(c + border) * box_size + i, (r + border) * box_size + j] = 0

    img.save(path)

def save_qr_matrix_as_svg(qr_matrix, path, box_size=10, border=4):
    matrix_size = len(qr_matrix)
    size = (matrix_size + border * 2) * box_size

    # Create the SVG root element
    svg = Element('svg', width=str(size), height=str(size), xmlns="http://www.w3.org/2000/svg")
    
    # Create a white background
    background = SubElement(svg, 'rect', width='100%', height='100%', fill='white')
    
    # Draw the QR matrix
    for r in range(matrix_size):
        for c in range(matrix_size):
            if qr_matrix[r, c] == 1:
                rect = SubElement(svg, 'rect', x=str((c + border) * box_size), y=str((r + border) * box_size), width=str(box_size), height=str(box_size), fill='black')
    
    # Convert the ElementTree to a string
    svg_string = tostring(svg)
    
    # Save SVG to file
    with open(path, 'wb') as f:
        f.write(svg_string)
    
    # Optionally, pretty-print the SVG
    dom = parseString(svg_string)
    pretty_svg = dom.toprettyxml()
    with open(path, 'w') as f:
        f.write(pretty_svg)

def create_custom_qr(normal_message, secret_message, format='png'):
    qr = create_qr_v8(normal_message)
    qr_matrix = get_qr_matrix(qr)

    start_x, start_y, region_width, region_height = calculate_region()

    try:
        qr_matrix = embed_secret_message(qr_matrix, secret_message, start_x, start_y, region_width, region_height)
    except ValueError as e:
        print(e)
        return None

    qr_matrix = apply_custom_mask(qr_matrix, start_x, start_y, region_width, region_height)

    if format == 'png':
        path = "./static/images/modified_qr.png"
        save_qr_matrix_as_png(qr_matrix, path)
    elif format == 'svg':
        path = "./static/images/modified_qr.svg"
        save_qr_matrix_as_svg(qr_matrix, path)
    print(f"Modified QR code saved to {path}")
    return path

if __name__ == "__main__":
    normal_message = "This is a normal message."
    secret_message = "This is a secret message."
    format = "png"  # or "svg"

    result = create_custom_qr(normal_message, secret_message, format)
    if result:
        print("QR code created successfully!")
    else:
        print("Failed to create QR code.")

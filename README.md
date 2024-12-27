# SecQR

SecQR is a web-based application designed to check QR codes for dangerous URLs and send secret messages through QR codes. It supports both image uploads and direct QR code scanning.

To send a secret message, encode your QR code with both a normal and a secret message. The recipient can then use SecQR to decode both messages.

The secret message remains hidden from standard scanners and is encrypted before encoding, ensuring data confidentiality. Note that the normal message can be up to 84 characters long, and the secret message can be up to 57 characters long.

## Features

- **QR Code Generation**: Create QR codes from user-inputted data with enhanced security measures.
- **QR Code Decoding**: Upload and decode QR codes to retrieve the embedded information safely.
- **URL Validation**: Automatically checks URLs encoded in QR codes to prevent malicious link access.

## Technologies Used

- **Backend**: Python with Flask framework
- **Frontend**: HTML, CSS, JavaScript
- **QR Code Processing**: `qrcode` and `OpenCV` libraries
- **Security**: Implementation of data validation and sanitization techniques

## Getting Started

Use the application at this link: https://secqr-vsp0.onrender.com/

or

Follow these steps to set up and run the application locally:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/LyuboPetkov/SecQR.git
   ```

2. **Navigate to the Project Directory:**
   ```bash
   cd SecQR
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application:**
   ```bash
   python server.py
   ```

5. **Access via Web Browser:**
   Open your browser and go to `http://localhost:5000` to use the application.

## Project Structure

- `server.py`: Main application script
- `encoder.py` and `decoder.py`: Modules for QR code generation and decoding
- `templates/`: HTML templates
- `static/`: CSS and JavaScript files

## Contributions

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License.


from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from waitress import serve
from encoder import create_custom_qr
from upload_image import upload_image, allowed_file
from url_check import check_qr_url, check_url_safety
from config import init_app
import os
from decoder import decode_qr

app = Flask(__name__)
init_app(app)

########## HOME PAGE ##########

@app.route('/')
@app.route('/index')
def index():
    print("Rendering index page")
    return render_template('home-page/index.html')

@app.route('/redirect-to-home')
def redirect_to_home():
    return redirect(url_for('index'))

########## ABOUT PAGE ##########

@app.route('/about')
def about():
    print("Rendering about page")
    return render_template('about.html')

########## CHECK URL ##########

@app.route('/check-url')
def check_url():
    print("Rendering check-qr-url page")
    return render_template('check-qr-url/check-url.html')

@app.route('/check-url/scan')
def scan_qr():
    print("Rendering scanning for URL check page")
    return render_template('check-qr-url/check-scan.html')

@app.route('/check-url/upload')
def upload_qr():
    print("Rendering check-upload-image page")
    return render_template('check-qr-url/check-upload.html')

@app.route('/uploaded-image-check', methods=['GET', 'POST'])
def uploaded_image_check():
    if request.method == 'POST':
        file_path = upload_image('check-url')
        if file_path:
            status, url = check_qr_url(file_path)
            os.remove(file_path)
            session['url'] = url
            session['decoded_data'] = url
            if status == "QR not found":
                return redirect(url_for('qr_not_found'))
            elif status == "URL not found":
                return redirect(url_for('url_not_found'))
            elif status == "URL is not dangerous":
                return redirect(url_for('not_dangerous'))
            elif status == "URL is dangerous":
                return redirect(url_for('dangerous'))
    return render_template('check-qr-url/check-upload.html')

@app.route('/check-url/not-dangerous')
def not_dangerous():
    url = session.get('url', '')
    print("Rendering not-dangerous page")
    return render_template('check-qr-url/not-dangerous.html', url=url)

@app.route('/check-url/dangerous')
def dangerous():
    url = session.get('url', '')
    print("Rendering dangerous page")
    return render_template('check-qr-url/dangerous.html', url=url)

@app.route('/check-url/no-qr-code')
def qr_not_found():
    print("Rendering QR not found page")
    return render_template('check-qr-url/qr-not-found.html')

@app.route('/check-url/no-url')
def url_not_found():
    decoded_data = session.get('decoded_data', '')
    print("Rendering URL not found page")
    return render_template('check-qr-url/url-not-found.html', decoded_data=decoded_data)

@app.route('/process-check', methods=['POST'])
def process_qr_check():
    data = request.json
    url = data.get('data')
    status, checked_url = check_url_safety(url)
    session['url'] = checked_url
    session['decoded_data'] = url

    if status == "QR not found":
        response = jsonify({'message': 'QR not found', 'redirect': url_for('qr_not_found')})
    elif status == "URL not found":
        response = jsonify({'message': 'URL not found', 'redirect': url_for('url_not_found')})
    elif status == "URL is not dangerous":
        response = jsonify({'message': 'URL is not dangerous', 'redirect': url_for('not_dangerous')})
    elif status == "URL is dangerous":
        response = jsonify({'message': 'URL is dangerous', 'redirect': url_for('dangerous')})
    else:
        response = jsonify({'message': 'Successful scan', 'redirect': url_for('scan_qr')})

    return response

########## SECRET MESSAGE ##########

@app.route('/secret-message')
def secret_message():
    print("Rendering secret-message page")
    return render_template('secret-message/secret-message.html')

@app.route('/secret-message/encode')
def encode_qr():
    print("Rendering encode page")
    return render_template('secret-message/encode.html')

@app.route('/secret-message/encode/custom-qr', methods=['POST'])
def encode_data():
    normal_message = request.form.get('normal-message')
    secret_message = request.form.get('secret-message')
    format = request.form.get('format', 'png')  # Default to 'png' if no format is selected

    status_normal, _ = check_url_safety(normal_message)
    status_secret, _ = check_url_safety(secret_message)

    if status_normal == "URL is dangerous" or status_secret == "URL is dangerous":
        return redirect(url_for('dangerous_data'))

    file_path = create_custom_qr(normal_message, secret_message, format)
    if file_path:
        session['file_path'] = file_path
        session['format'] = format  # Save the format to the session
        return redirect(url_for('custom_qr'))
    else:
        return "Failed to create QR code", 500



@app.route('/secret-message/encode/dangerous-data')
def dangerous_data():
    print("Rendering dangerous data page")
    return render_template('secret-message/encoded-dangerous.html')

@app.route('/secret-message/encode/custom-qr')
def custom_qr():
    print("Rendering custom QR page")
    return render_template('secret-message/custom-qr.html')

@app.route('/secret-message/decode')
def decode_qr_page():
    print("Rendering decode page")
    return render_template('secret-message/decode.html')

@app.route('/secret-message/decode/upload')
def decode_upload_image():
    print("Rendering decode upload image page")
    return render_template('secret-message/secret-message-upload.html')

@app.route('/secret-message/decode/scan')
def scan_secret_message():
    return render_template('secret-message/secret-message-scan.html')

@app.route('/secret-message/decode/result', methods=['POST'])
def decode_qr_image():
    if request.method == 'POST':
        file_path = upload_image('secret-message')
        if file_path:
            normal_message, secret_message = decode_qr(file_path)
            os.remove(file_path)
            session['normal_message'] = normal_message
            session['secret_message'] = secret_message
            if secret_message == "n!Sect33v||||???~~a122s0m,./":
                return redirect(url_for('result_no_secret'))
            if normal_message == "n0!0kbnsqr,c0d||c3e.,?s":
                return redirect(url_for('result_no_qr'))
            return redirect(url_for('result_secret'))
    return render_template('secret-message/secret-message-upload.html')

@app.route('/secret-message/decode/result/secret')
def result_secret():
    normal_message = session.get('normal_message', '')
    secret_message = session.get('secret_message', '')
    print("Rendering result secret message page")
    return render_template('secret-message/result-secret.html', normal_message=normal_message, secret_message=secret_message)

@app.route('/secret-message/decode/result/no-secret')
def result_no_secret():
    normal_message = session.get('normal_message', '')
    print("Rendering result no secret message page")
    return render_template('secret-message/result-no-secret.html', normal_message=normal_message)

@app.route('/secret-message/decode/result/no-qr')
def result_no_qr():
    normal_message = session.get('normal_message', '')
    print("Rendering result no QR code page")
    return render_template('secret-message/result-no-qr.html', normal_message=normal_message)

@app.route('/process-secret-scan', methods=['POST'])
def process_secret_scan():
    file_path = upload_image('secret-message')
    if file_path:
        print(f"Saved file to {file_path}")
        normal_message, secret_message = decode_qr(file_path)
        print(f"Decoded normal message: {normal_message}")
        print(f"Decoded secret message: {secret_message}")
        os.remove(file_path)
        session['normal_message'] = normal_message
        session['secret_message'] = secret_message
        if normal_message == "n0!0kbnsqr,c0d||c3e.,?s":
            response = jsonify({'message': 'no-qr-code', 'continueScanning': True})
        elif secret_message == "n!Sect33v||||???~~a122s0m,./":
            response = jsonify({'message': 'no-secret-message', 'redirect': url_for('result_no_secret')})
        else:
            response = jsonify({'message': 'secret-message', 'redirect': url_for('result_secret')})
        print(f"Response: {response.get_json()}")
        return response
    return jsonify({'message': 'Error processing the file', 'redirect': url_for('decode_qr_page')})

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    port = 5000    
    print(f"Starting Flask server on port: {port}")
    serve(app, host="0.0.0.0", port=5000)

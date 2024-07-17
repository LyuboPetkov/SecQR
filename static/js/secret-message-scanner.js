console.log('JavaScript file loaded');

const html5QrCode = new Html5Qrcode("reader");

function onScanSuccess(decodedText, decodedResult) {
    console.log(`Decoded text: ${decodedText}`);

    // Capture the image first
    captureImage();
}

function captureImage() {
    const videoElement = document.querySelector('#reader video');

    if (videoElement) {
        const canvas = document.createElement('canvas');
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        const context = canvas.getContext('2d');
        context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

        // Convert canvas to blob
        canvas.toBlob((blob) => {
            console.log('Image captured, converting to blob.');
            const formData = new FormData();
            formData.append('file', blob, 'qr-code.png');
            
            // Stop the QR code scanner after the image is captured
            html5QrCode.stop().then(() => {
                console.log('Scanner stopped.');
                sendToBackend(formData);
            }).catch((err) => {
                console.error("Failed to stop scanning:", err);
            });
        }, 'image/png');
    } else {
        console.error('Video element not found.');
    }
}

function sendToBackend(formData) {
    console.log('Sending image to the backend.');
    fetch('/process-secret-scan', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        console.log('Backend response:', data);
        if (data.continueScanning) {
            // Restart the QR code scanner if there is no QR code
            restartScanner();
        } else if (data.redirect) {
            window.location.href = data.redirect;
        } else {
            // Restart the QR code scanner after the response is processed
            restartScanner();
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        // Restart the QR code scanner in case of error
        restartScanner();
    });
}

function restartScanner() {
    html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess)
        .catch(err => {
            console.error(`Unable to start scanning, error: ${err}`);
        });
}

const config = { fps: 10, qrbox: { width: 150, height: 150 } };

html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess)
    .catch(err => {
        console.error(`Unable to start scanning, error: ${err}`);
    });

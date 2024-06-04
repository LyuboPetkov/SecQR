const html5QrCode = new Html5Qrcode("reader");

function onScanSuccess(decodedText, decodedResult) {
    console.log(`Decoded text: ${decodedText}`);
    
    html5QrCode.stop().then((ignore) => {
        sendToBackend(decodedText);
    }).catch((err) => {
        console.error("Failed to stop scanning:", err);
    });
}

function sendToBackend(decodedText) {
    fetch('/process-check', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ data: decodedText }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data.message);
        if (data.redirect) {
            window.location.href = data.redirect;
        } else {
            html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess)
                .catch(err => {
                    console.error(`Unable to start scanning, error: ${err}`);
                });
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess)
            .catch(err => {
                console.error(`Unable to start scanning, error: ${err}`);
            });
    });
}

const config = { fps: 10, qrbox: { width: 230, height: 230 } };

html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess)
    .catch(err => {
        console.error(`Unable to start scanning, error: ${err}`);
    });

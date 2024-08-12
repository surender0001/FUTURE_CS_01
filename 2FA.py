from flask import Flask, request, render_template, redirect, url_for, session, flash, send_file
import pyotp
import qrcode
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Updated in-memory user storage with the default user
users = {
    "john": "passwd_john"
}

# Store TOTP secrets for users
totp_store = {}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Authenticate user
        if username in users and users[username] == password:
            # Generate a TOTP secret if not already generated
            if username not in totp_store:
                totp_store[username] = pyotp.TOTP(pyotp.random_base32())
            session['username'] = username
            return redirect(url_for('generate_qr'))
        else:
            flash("Invalid username or password", "danger")

    return render_template('login.html')

@app.route('/generate-qr')
def generate_qr():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    totp = totp_store[username]
    # Create a provisioning URI for the TOTP
    provisioning_uri = totp.provisioning_uri(name=username, issuer_name="YourAppName")

    # Generate the QR code
    qr = qrcode.make(provisioning_uri)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    buf.seek(0)
    
    return send_file(buf, mimetype='image/png')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        otp_input = request.form['otp']
        username = session['username']
        totp = totp_store[username]

        if totp.verify(otp_input):
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid OTP. Please try again.", "danger")

    return render_template('verify_otp.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return f"Welcome to your dashboard, {session['username']}!"
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

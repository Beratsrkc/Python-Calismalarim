from tkinter import *
from tkinter import ttk
from tkinter.ttk import Combobox
from tkinter import messagebox, filedialog
import tkinter as tk
import PyPDF2
import pyttsx3
import os
import googletrans
from googletrans import Translator
import threading
import pyaudio
import wave
import speech_recognition as sr

# Renkler
framebg = "#1a237e"
bodybg = "#e8eaf6"
textbg = "#ffffff"
buttonbg = "#e8eaf6"
hoverbg = "#5c6bc0"

# Global değişkenler
engine = None
is_speaking = False
speaking_thread = None
stop_speaking_flag = False

def translate_text():
    try:
        text = text_area.get("1.0", "end-1c")
        if not text.strip():
            messagebox.showwarning("Uyarı", "Çeviri için metin girin")
            return
            
        lang1 = combo1.get()
        lang2 = combo.get()
        
        lang1_code = [k for k, v in googletrans.LANGUAGES.items() if v == lang1][0]
        lang2_code = [k for k, v in googletrans.LANGUAGES.items() if v == lang2][0]
        
        translated = translator.translate(text, src=lang1_code, dest=lang2_code)
        text_area2.delete("1.0", "end")
        text_area2.insert("1.0", translated.text)
    except Exception as e:
        messagebox.showerror("Hata", f"Çeviri yapılamadı: {str(e)}")

def speak_text():
    global engine, is_speaking, speaking_thread, stop_speaking_flag
    
    def _speak():
        global is_speaking, stop_speaking_flag
        try:
            text = text_area2.get("1.0", "end-1c")
            if not text.strip():
                messagebox.showwarning("Uyarı", "Seslendirme için metin girin")
                return

            engine = pyttsx3.init()
            engine.setProperty('rate', current_value.get())
            
            voices = engine.getProperty('voices')
            if gender_combobox.get() == 'Kadın' and len(voices) > 1:
                engine.setProperty('voice', voices[1].id)
            else:
                engine.setProperty('voice', voices[0].id)
            
            is_speaking = True
            engine.say(text)
            engine.startLoop(False)
            
            while engine.isBusy() and not stop_speaking_flag:
                engine.iterate()
                root.update()
                
            engine.endLoop()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Seslendirme hatası: {str(e)}")
        finally:
            is_speaking = False
            stop_speaking_flag = False
            voice_btn.config(state=NORMAL)
            stop_btn.config(state=DISABLED)
            if engine:
                try:
                    engine.stop()
                except:
                    pass
    
    if is_speaking:
        return
        
    voice_btn.config(state=DISABLED)
    stop_btn.config(state=NORMAL)
    stop_speaking_flag = False
    speaking_thread = threading.Thread(target=_speak, daemon=True)
    speaking_thread.start()

def stop_speaking():
    global stop_speaking_flag
    stop_speaking_flag = True
    stop_btn.config(state=DISABLED)

def record_audio():
    try:
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        RECORD_SECONDS = 5
        WAVE_OUTPUT_FILENAME = "output.wav"
        
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        
        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        r = sr.Recognizer()
        with sr.AudioFile(WAVE_OUTPUT_FILENAME) as source:
            audio = r.record(source)
            text = r.recognize_google(audio, language='tr-TR')
            text_area.insert("end", text)
            
    except Exception as e:
        messagebox.showerror("Hata", f"Ses tanıma başarısız: {str(e)}")

def upload_pdf():
    try:
        filepath = filedialog.askopenfilename(filetypes=[("PDF Dosyaları", "*.pdf")])
        if filepath:
            with open(filepath, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = "\n".join([page.extract_text() for page in reader.pages])
                text_area.delete("1.0", "end")
                text_area.insert("1.0", text)
    except Exception as e:
        messagebox.showerror("Hata", f"PDF okunamadı: {str(e)}")

def upload_audio_file():
    try:
        filepath = filedialog.askopenfilename(filetypes=[("Ses Dosyaları", "*.wav *.mp3")])
        if filepath:
            r = sr.Recognizer()
            with sr.AudioFile(filepath) as source:
                audio = r.record(source)
                text = r.recognize_google(audio, language='tr-TR')
                text_area.insert("end", text)
    except Exception as e:
        messagebox.showerror("Hata", f"Ses dosyası işlenemedi: {str(e)}")

def save_translation():
    try:
        text = text_area2.get("1.0", "end-1c")
        if not text.strip():
            messagebox.showwarning("Uyarı", "Kaydedilecek metin yok")
            return
            
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Metin Dosyaları", "*.txt"), ("Tüm Dosyalar", "*.*")]
        )
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(text)
            messagebox.showinfo("Başarılı", "Çeviri başarıyla kaydedildi!")
    except Exception as e:
        messagebox.showerror("Hata", f"Dosya kaydedilemedi: {str(e)}")

# ANA PENCERE VE ARAYÜZ ELEMANLARI
root = Tk()
root.title("Çeviri Uygulaması")
root.geometry("900x700+200+100")
root.config(bg=bodybg)
root.minsize(700, 500)

# Çevirici nesnesi
translator = Translator()

# İkon
try:
    image_icon = PhotoImage(file="Çeviri Uygulaması/Images/icon.png")
    root.iconphoto(False, image_icon)
except:
    print("İkon dosyası bulunamadı")

# Stil Ayarları
style = ttk.Style()
style.configure("TFrame", background=bodybg)
style.configure("TButton", background=buttonbg, foreground="white", font=('Arial', 10))
style.map("TButton", background=[('active', hoverbg)])

# Üst Çerçeve
Top_frame = ttk.Frame(root, style="TFrame", height=80)
Top_frame.pack(fill=X, padx=10, pady=10)

try:
    logo_icon = PhotoImage(file="Çeviri Uygulaması/Images/icon.png").subsample(2, 2)
    ttk.Label(Top_frame, image=logo_icon, background=framebg).pack(side=LEFT, padx=10, pady=5)
except:
    ttk.Label(Top_frame, text="LOGO", background=framebg, foreground="white", 
             font=('Arial', 12)).pack(side=LEFT, padx=10, pady=5)

ttk.Label(Top_frame, text="ÇEVİRİ UYGULAMASI", font=('Arial', 16, 'bold'), 
         background=framebg, foreground="white").pack(side=LEFT, padx=10)

# Ana Çerçeve - Grid sistemi
main_frame = ttk.Frame(root, style="TFrame")
main_frame.pack(fill=BOTH, expand=True, padx=10, pady=(0,10))

# Grid yapılandırması
main_frame.columnconfigure(0, weight=3)
main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(0, weight=1)

# Sol Çerçeve (Metin Alanları)
left_frame = ttk.Frame(main_frame, style="TFrame")
left_frame.grid(row=0, column=0, sticky="nsew", padx=5)
left_frame.columnconfigure(0, weight=1)
left_frame.rowconfigure(0, weight=1)
left_frame.rowconfigure(1, weight=1)

# Üst Metin Alanı
text1_frame = ttk.Frame(left_frame, style="TFrame")
text1_frame.grid(row=0, column=0, sticky="nsew", pady=(0,5))

ttk.Label(text1_frame, text="ORİJİNAL METİN", font=('Arial', 10)).pack(anchor=W)
text_area = Text(text1_frame, font=('Arial', 12), bg=textbg, relief=GROOVE, wrap=WORD,
                padx=10, pady=10, selectbackground=hoverbg)
text_area.pack(fill=BOTH, expand=True)

# Alt Metin Alanı
text2_frame = ttk.Frame(left_frame, style="TFrame")
text2_frame.grid(row=1, column=0, sticky="nsew", pady=(5,0))

ttk.Label(text2_frame, text="ÇEVİRİ SONUCU", font=('Arial', 10)).pack(anchor=W)
text_area2 = Text(text2_frame, font=('Arial', 12), bg=textbg, relief=GROOVE, wrap=WORD,
                 padx=10, pady=10, selectbackground=hoverbg)
text_area2.pack(fill=BOTH, expand=True)

# Sağ Çerçeve (Kontroller)
right_frame = ttk.Frame(main_frame, style="TFrame", width=250)
right_frame.grid(row=0, column=1, sticky="nsew", padx=(5,0))
right_frame.columnconfigure(0, weight=1)

# Dil Seçimleri
lang_frame = ttk.Frame(right_frame, style="TFrame")
lang_frame.pack(fill=X, pady=10, padx=5)

ttk.Label(lang_frame, text="Kaynak Dil:", font=('Arial', 10)).pack(anchor=W)
combo1 = ttk.Combobox(lang_frame, values=list(googletrans.LANGUAGES.values()), 
                     font=('Arial', 10), state='readonly')
combo1.pack(fill=X, pady=(0,10))
combo1.set("turkish")  

ttk.Label(lang_frame, text="Hedef Dil:", font=('Arial', 10)).pack(anchor=W)
combo = ttk.Combobox(lang_frame, values=list(googletrans.LANGUAGES.values()), 
                    font=('Arial', 10), state='readonly')
combo.pack(fill=X)
combo.set("english")  

# Ses Ayarları
voice_frame = ttk.Frame(right_frame, style="TFrame")
voice_frame.pack(fill=X, pady=10, padx=5)

ttk.Label(voice_frame, text="Ses Ayarları", font=('Arial', 10, 'bold')).pack(anchor=W)

ttk.Label(voice_frame, text="Ses Türü:", font=('Arial', 10)).pack(anchor=W)
gender_combobox = ttk.Combobox(voice_frame, values=['Erkek', 'Kadın'], 
                             font=('Arial', 10), state='readonly')
gender_combobox.pack(fill=X, pady=(0,10))
gender_combobox.set("Kadın")

ttk.Label(voice_frame, text="Ses Hızı:", font=('Arial', 10)).pack(anchor=W)
current_value = tk.DoubleVar(value=150)

speed_frame = ttk.Frame(voice_frame, style="TFrame")
speed_frame.pack(fill=X)

slider = ttk.Scale(speed_frame, from_=30, to=250, variable=current_value,
                  orient=HORIZONTAL)
slider.pack(side=LEFT, expand=True, fill=X)

value_label = ttk.Label(speed_frame, text="150", font=('Arial', 9))
value_label.pack(side=RIGHT, padx=5)

def update_speed_label(*args):
    value_label.config(text=f"{int(current_value.get())}")

current_value.trace_add("write", update_speed_label)

# Butonlar (Resimli Butonlar)
button_frame = ttk.Frame(right_frame, style="TFrame", width=150)  # Sabit genişlik eklendi
button_frame.pack(fill=Y, pady=10, padx=5)  # Dikeyde genişlesin

# Buton oluşturma fonksiyonu
def create_image_button(parent, image_path, command, text):
    try:
        img = PhotoImage(file=image_path)
        btn = Button(parent, image=img, command=command, bd=0, bg=buttonbg, activebackground=hoverbg)
        btn.image = img
        return btn
    except:
        btn = Button(parent, text=text, command=command, bd=0, bg=buttonbg, 
                   activebackground=hoverbg, fg="white", font=('Arial', 10))
        return btn

# Butonları oluştur
translate_btn = create_image_button(button_frame, "Çeviri Uygulaması/Images/trans.png", translate_text, "Çevir")
translate_btn.pack(fill=X, pady=5)

voice_btn = create_image_button(button_frame, "Çeviri Uygulaması/Images/speak.png", speak_text, "Seslendir")
voice_btn.pack(fill=X, pady=5)

stop_btn = Button(
    button_frame,
    text="Durdur",
    command=stop_speaking,
    bd=0,                      # Kenarlık yok
    bg="#ff4444",              # Kırmızı arkaplan
    activebackground="#ff6666", # Basılı halde açık kırmızı
    fg="white",                # Beyaz yazı
    activeforeground="white",   # Basılı halde de beyaz yazı
    font=('Arial', 10),        # Yazı tipi
    state=DISABLED,            # Başlangıçta pasif
    width=6,                   # Daha dar genişlik (6 karakter)
    padx=3,                    # Yatay iç boşluk az
    pady=1,                    # Dikey iç boşluk az
    relief="flat"              # Düz görünüm
)
stop_btn.pack(fill=X, pady=2, ipadx=2)  # Daha az boşluk

record_btn = create_image_button(button_frame, "Çeviri Uygulaması/Images/mic.png", record_audio, "Ses Kaydet")
record_btn.pack(fill=X, pady=5)

file_btn = create_image_button(button_frame, "Çeviri Uygulaması/Images/pdfimage.png", upload_pdf, "PDF Yükle")
file_btn.pack(fill=X, pady=5)

audio_btn = create_image_button(button_frame, "Çeviri Uygulaması/Images/music.png", upload_audio_file, "Ses Dosyası")
audio_btn.pack(fill=X, pady=5)

save_btn = create_image_button(button_frame, "Çeviri Uygulaması/Images/download.png", save_translation, "Kaydet")
save_btn.pack(fill=X, pady=5)

# Pencere boyutlandırma ayarları
def on_resize(event):
    right_frame.config(width=250)
    
root.bind('<Configure>', on_resize)

# Pencere kapatılırken motoru durdur
def on_closing():
    stop_speaking()
    if speaking_thread and speaking_thread.is_alive():
        speaking_thread.join(0.5)
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
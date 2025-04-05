from tkinter import *
import tkinter as tk
from geopy.geocoders import Nominatim
from tkinter import ttk, messagebox
from timezonefinder import TimezoneFinder
from datetime import datetime
import requests
import pytz
import os
from dotenv import load_dotenv

# Environment variables yükle
load_dotenv()

# Ana pencere oluşturma
root = Tk()
root.title("Hava Durumu Uygulaması")
root.geometry("900x500+300+200")
root.resizable(False, False)
root.configure(bg="#f5f7fa")

def getWeather():
    try:
        city = textfield.get()
        if not city:
            messagebox.showerror("Hata", "Lütfen bir şehir adı giriniz")
            return

        geolocator = Nominatim(user_agent="hava_durumu_uygulamasi")
        location = geolocator.geocode(city, timeout=10)
        
        if not location:
            messagebox.showerror("Hata", "Şehir bulunamadı")
            return
            
        obj = TimezoneFinder()
        result = obj.timezone_at(lng=location.longitude, lat=location.latitude)
        
        home = pytz.timezone(result)
        local_time = datetime.now(home)
        current_time = local_time.strftime("%H:%M")
        clock.config(text=f"📍 {city.upper()} | 🕒 {current_time}")
        
        # API key'i environment variable'dan al
        api_key = os.getenv("API_KEY")
        if not api_key:
            messagebox.showerror("Hata", "API anahtarı bulunamadı")
            return
            
        api = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&lang=tr"
        json_data = requests.get(api).json()
        
        condition = json_data['weather'][0]['main']
        description = json_data['weather'][0]['description']
        temp = int(json_data['main']['temp']-273.15)
        pressure = json_data['main']['pressure']
        humidity = json_data['main']['humidity']
        wind = json_data['wind']['speed']
        feels_like = int(json_data['main']['feels_like']-273.15)

        # Güncellemeler
        t.config(text=f"{temp}°C")
        c.config(text=f"{description.capitalize()}\nHissedilen: {feels_like}°C")
        
        w.config(text=f"{wind} m/s")
        h.config(text=f"%{humidity}")
        d.config(text=description.capitalize())
        p.config(text=f"{pressure} hPa")

    except Exception as e:
        messagebox.showerror("Hata", f"Bir hata oluştu: {str(e)}")

# Arama çubuğu tasarımı
search_frame = Frame(root, bg="#ffffff", bd=2, relief=tk.SOLID, highlightthickness=0)
search_frame.place(x=50, y=30, width=400, height=50)

# Arama ikonu
try:
    search_icon = PhotoImage(file="Images/search_icon.png").subsample(2,2)
except:
    search_icon = PhotoImage(file="Images/search_icon.png")

search_btn = Button(search_frame, image=search_icon, bg="#ffffff", 
                   activebackground="#ffffff", borderwidth=0,
                   command=getWeather)
search_btn.place(x=350, y=5)

# Metin giriş alanı
textfield = tk.Entry(search_frame, font=("Arial", 14), 
                    bg="#ffffff", fg="#2d3436", borderwidth=0,
                    highlightthickness=0)
textfield.place(x=10, y=10, width=330)
textfield.focus()

# Logo
try:
    logo_img = PhotoImage(file="Images/logo.png").subsample(2,2)
except:
    logo_img = PhotoImage(file="Images/logo.png")
logo_label = Label(root, image=logo_img, bg="#f5f7fa")
logo_label.place(x=730, y=20)

# Ana bilgi alanı
main_frame = Frame(root, bg="#ffffff", bd=0, highlightthickness=0, 
                 relief=tk.FLAT)
main_frame.place( y=200, width=900, height=250)

# Sıcaklık bilgisi
t = Label(main_frame, font=("Arial", 48, "bold"), fg="#2d3436", bg="#ffffff")
t.place(x=70, y=20)

# Hava durumu açıklaması
c = Label(main_frame, font=("Arial", 14), fg="#636e72", bg="#ffffff",
         justify=tk.LEFT)
c.place(x=70, y=100)

# Bilgi kartları
def create_info_card(parent, x, y, title):
    card = Frame(parent, bg="#f5f7fa", bd=0, highlightthickness=0,
                relief=tk.RAISED, padx=10, pady=10)
    card.place(x=x, y=y, width=190, height=100)
    
    Label(card, text=title, font=("Arial", 12, 'bold'), 
         fg="#2d3436", bg="#f5f7fa").pack(anchor=tk.W)
    
    value_label = Label(card, text="...", font=("Arial", 14, 'bold'), 
                     fg="#0984e3", bg="#f5f7fa", justify=tk.LEFT)
    value_label.pack(anchor=tk.W)
    
    return value_label

# Kartları oluştur
w = create_info_card(root, 50, 370, "RÜZGAR")
h = create_info_card(root, 250, 370, "NEM")
d = create_info_card(root, 450, 370, "DURUM")
p = create_info_card(root, 650, 370, "BASINÇ")

# Saat ve konum bilgisi
clock = Label(root, font=("Arial", 14, "bold"), fg="#636e72", bg="#f5f7fa")
clock.place(x=50, y=160)
clock.config(text="Şehir adı girin...")

root.mainloop()
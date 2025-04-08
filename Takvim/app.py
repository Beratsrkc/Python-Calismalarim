from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)


events = {}

@app.route('/')
def index():
    # Şu anki ay ve yıl
    now = datetime.now()
    year = now.year
    month = now.month
    
    if 'year' in request.args and 'month' in request.args:
        year = int(request.args['year'])
        month = int(request.args['month'])
    
    # Takvim verilerini oluştur
    calendar_data = generate_calendar(year, month)
    
    return render_template('index.html', 
                         year=year, 
                         month=month, 
                         month_name=month_name(month),
                         calendar_data=calendar_data,
                         events=events)

@app.route('/add_event', methods=['POST'])
def add_event():
    date_str = request.form['date']
    title = request.form['title']
    description = request.form['description']
    
    if date_str not in events:
        events[date_str] = []
    
    events[date_str].append({
        'title': title,
        'description': description
    })
    
    return redirect(url_for('index'))

@app.route('/event/<date>')
def event_detail(date):
    return render_template('event.html', date=date, events=events.get(date, []))

def generate_calendar(year, month):
    # İlk günü bul
    first_day = datetime(year, month, 1)
    # Ayın kaç gün çektiğini bul
    if month == 12:
        next_month = datetime(year+1, 1, 1)
    else:
        next_month = datetime(year, month+1, 1)
    last_day = next_month - timedelta(days=1)
    
    # Takvim verilerini oluştur
    calendar_data = []
    week = []
    
    # İlk günden önceki boşlukları ekle
    for _ in range(first_day.weekday()):
        week.append({'day': '', 'date': None})
    
    # Günleri ekle
    for day in range(1, last_day.day + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        week.append({
            'day': day,
            'date': date_str,
            'has_event': date_str in events
        })
        
        if len(week) == 7:
            calendar_data.append(week)
            week = []
    
    # Son haftayı tamamla
    if week:
        for _ in range(7 - len(week)):
            week.append({'day': '', 'date': None})
        calendar_data.append(week)
    
    return calendar_data

def month_name(month):
    months = [
        'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
        'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'
    ]
    return months[month - 1]

if __name__ == '__main__':
    app.run(debug=True)
import sqlite3
from datetime import datetime, timedelta
import re
import time
import threading

# Veritabanı kurulumu
conn = sqlite3.connect('calendar_app.db', check_same_thread=False)

cursor = conn.cursor()

# Veritabanı tabloları kurulumu
cursor.execute('''
CREATE TABLE IF NOT EXISTS users(
    name TEXT,
    surname TEXT,
    username TEXT PRIMARY KEY,
    password TEXT,
    tckn TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    userType TEXT CHECK(userType IN ('Admin', 'Kullanıcılar')))
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS events(
    eventTime TEXT,
    eventType TEXT,
    eventDescription TEXT,
    username TEXT,
    reminder INTEGER,
    FOREIGN KEY(username) REFERENCES users(username))
''')

#doğrulama bölümü
def is_valid_email(email):
    # Email adresini doğrulama
    regex = '^[a-z0-9]+[\._-]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if (re.search(regex, email)):
        return True
    else:
        return False


def is_valid_phone(phone):
    # Telefon numarasını doğrulama
    if phone[0] != "0" or len(phone) != 11 or not phone.isdigit():
        return False
    return True


def is_strong_password(password):
    # Şifrenin güçlü olup olmadığını kontrol etme
    if len(password) < 8:
        return False
    elif not re.search("[a-z]", password):
        return False
    elif not re.search("[A-Z]", password):
        return False
    elif not re.search("[0-9]", password):
        return False
    elif re.search("\s", password):
        return False
    else:
        return True


def add_user():

    name = input("Ad: ")
    surname = input("Soyad: ")

    while True:
        username = input("Kullanıcı adı: ")
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            print("Bu kullanıcı adı zaten var. Farklı bir kullanıcı adı deneyin.")
        else:
            break

    while True:
        password = input("Şifre: ")
        if not is_strong_password(password):
            print("Şifreniz en az 8 karakter uzunluğunda olmalı ve en az bir büyük harf, bir küçük harf, bir sayı içermelidir. Boşluk içermemelidir.")
        else:
            break

    while True:
        tckn = input("TC Kimlik No: ")
        if len(tckn) != 11 or not tckn.isdigit():
            print("Geçerli bir TC Kimlik Numarası girilmelidir.")
        else:
            cursor.execute('SELECT * FROM users WHERE tckn = ?', (tckn,))
            if cursor.fetchone():
                print("Bu TC Kimlik Numarası zaten kullanılıyor. Farklı bir TC Kimlik Numarası girin.")
            else:
                break

    while True:
        phone = input("Telefon: ")
        if not is_valid_phone(phone):
            print("Geçerli bir telefon numarası girin. Telefon numarası 0 ile başlamalıdır.")
        else:
            cursor.execute('SELECT * FROM users WHERE phone = ?', (phone,))
            if cursor.fetchone():
                print("Bu telefon numarası zaten kullanılıyor. Farklı bir telefon numarası girin.")
            else:
                break

    while True:
        email = input("Email: ")
        if not is_valid_email(email):
            print("Geçersiz bir email adresi girdiniz. Lütfen geçerli bir email adresi girin.")
        else:
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                print("Bu email adresi zaten kullanılıyor. Farklı bir email adresi girin.")
            else:
                break

    address = input("Adres: ")
#admin kaydı için ek şifre (212803052) istenecek
    while True:
        print("Kayıt tipi:\n\t1.Kullanıcı\n\t2.Admin")
        userTypeInput = input("Seçiminiz: ")

        if userTypeInput == '1':
            userType = 'Kullanıcılar'
            break
        elif userTypeInput == '2':
            while True:
                admin_code = input("Admin kaydı için Şifre: ")
                if admin_code == '212803052':
                    userType = 'Admin'
                    break
                else:
                    print("Hatalı kod. Kayıt tipine dönmek için 'r' ye basın veya tekrar deneyin.")
                    if input().lower() == 'r':
                        break
            if admin_code == '212803052':
                break
        else:
            print("Hatalı giriş. Lütfen geçerli bir seçenek girin.")

    cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (name, surname, username, password, tckn, phone, email, address, userType))
    conn.commit()
    print("Kullanıcı başarıyla oluşturuldu.\n")


def user_login():

    username = input("Kullanıcı adı: ")
    password = input("Şifre: ")
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    if cursor.fetchone():
        return username
    else:
        print("Hatalı kullanıcı adı veya şifre.\n")
        return None


def add_event(username):
    # yeni etkinlik ekleme
    while True:
        print("Etkinlik tarihini giriniz (YYYY-MM-DD formatında): ")
        year = input("Yıl: ")
        month = input("Ay: ")
        day = input("Gün: ")

        # Tarih hata kontrolü
        try:
            datetime(int(year), int(month), int(day))
        except ValueError:
            print("Geçersiz tarih. Lütfen tekrar deneyin.")
            continue

        print("Etkinlik saatini giriniz (HH:MM formatında): ")
        hour = input("Saat: ")
        minute = input("Dakika: ")

        # Saat hata kontrolü
        try:
            assert 0 <= int(hour) < 24
            assert 0 <= int(minute) < 60
        except (ValueError, AssertionError):
            print("Geçersiz saat. Lütfen tekrar deneyin.")
            continue

        eventTime = year + "-" + month + "-" + day + " " + hour + ":" + minute
        break

    eventType = input("Etkinlik tipi: ")
    eventDescription = input("Etkinlik açıklaması: ")
    while True:
        try:
            reminder = int(input("Hatırlatma süresi (gün olarak): "))
            break
        except ValueError:
            print("Geçerli bir sayı girin.")
    cursor.execute('INSERT INTO events VALUES (?, ?, ?, ?, ?)',
                   (eventTime, eventType, eventDescription, username, reminder))
    conn.commit()
    print("Etkinlik başarıyla eklendi.\n")

def list_events(username):
    # Etkinlikleri liste şeklinde gösterir
    cursor.execute('SELECT * FROM events WHERE username = ?', (username,))
    rows = cursor.fetchall()
    if rows:
        print("Etkinlikler:")
        for row in rows:
            print(row)
    else:
        print("Mevcut etkinlik bulunmuyor.")
    print()


def update_event(username):
    # seçilen etkinliği güncellemek için kullanılır
    cursor.execute('SELECT * FROM events WHERE username = ?', (username,))
    events = cursor.fetchall()
    if not events:
        print("Hiçbir etkinlik bulunamadı.\n")
        return

    for i, event in enumerate(events, start=1):
        print(f"{i}. {event[1]} - {event[0]}")

    while True:
        try:
            event_number = int(input("Güncellenecek etkinlik numarası: "))
            if 1 <= event_number <= len(events):
                break
            else:
                print("Geçersiz etkinlik numarası. Lütfen tekrar deneyin.")
        except ValueError:
            print("Geçerli bir sayı girin.")

    event = events[event_number - 1]

    while True:
        print("1. Etkinlik zamanı")
        print("2. Etkinlik tipi")
        print("3. Etkinlik açıklaması")
        print("4. Hatırlatma süresi")
        print("5. Ana menüye dön")
        choice = input("Güncellenecek bilgiyi seçin: ")

        if choice == '1':
            newEventTime = input("Yeni etkinlik zamanı [" + event[0] + "]: ")
            cursor.execute('UPDATE events SET eventTime = ? WHERE eventTime = ? AND username = ?',
                           (newEventTime, event[0], username))
        elif choice == '2':
            newEventType = input("Yeni etkinlik tipi [" + event[1] + "]: ")
            cursor.execute('UPDATE events SET eventType = ? WHERE eventTime = ? AND username = ?',
                           (newEventType, event[0], username))
        elif choice == '3':
            newEventDescription = input("Yeni etkinlik açıklaması [" + event[2] + "]: ")
            cursor.execute('UPDATE events SET eventDescription = ? WHERE eventTime = ? AND username = ?',
                           (newEventDescription, event[0], username))
        elif choice == '4':
            newReminder = int(input("Yeni hatırlatma süresi [" + str(event[4]) + "]: "))
            cursor.execute('UPDATE events SET reminder = ? WHERE eventTime = ? AND username = ?',
                           (newReminder, event[0], username))
        elif choice == '5':
            break
        else:
            print("Geçersiz seçim. Lütfen tekrar deneyin.")

        conn.commit()
        print("Etkinlik başarıyla güncellendi.\n")


def event_reminder(username):
    #hatırlatıcı bölümü
    cursor_reminder = conn.cursor()
    while True:
        cursor_reminder.execute('SELECT eventTime, eventType, reminder FROM events WHERE username = ?', (username,))
        now = datetime.now()
        events = cursor_reminder.fetchall()
        for event in events:
            event_time = datetime.strptime(event[0], '%Y-%m-%d %H:%M')
            reminder = timedelta(days=event[2])
            if event_time - reminder <= now < event_time:
                print(f"\n-----------------------------------------")
                print(f"Hatırlatma: {event[1]} etkinliğiniz {event_time} tarihinde başlıyor.")
                print(f"\n-----------------------------------------")
                print((f"Seçiminiz: "))
                time.sleep(60*60)
            elif now >= event_time:
                print(f"\n-----------------------------------------")
                print(f"\n{event[1]} etkinliği başladı.")
                print(f"\n-----------------------------------------")
                print((f"Seçiminiz: "))

                time.sleep(60*60)
        time.sleep(60)

def get_user_type(username):

    cursor.execute('SELECT userType FROM users WHERE username = ?', (username,))
    user_type = cursor.fetchone()
    if user_type:
        return user_type[0]
    else:
        return None

def get_upcoming_event(username):
    # en yakın etkinliği bulur
    cursor.execute('SELECT * FROM events WHERE username = ? ORDER BY eventTime ASC', (username,))
    events = cursor.fetchall()
    if events:
        return events[0]
    else:
        return None

def view_events_on_date(username):
    # Kullanıcının seçilen bir tarih için etkinliklerini görüntüler ve yönetir
    year = input("Yıl: ")
    month = input("Ay: ")
    day = input("Gün: ")
    date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    cursor.execute('SELECT * FROM events WHERE username = ? AND DATE(eventTime) = ?', (username, date))
    events = cursor.fetchall()
    if events:
        for i, event in enumerate(events, start=1):
            print(f"{i}. {event[1]} - {event[0]}")
        # İşlem menüsü
        print("1. Etkinlik Düzenle")
        print("2. Etkinlik Sil")
        print("3. Ana Menüye Dön")
        choice = input("Seçiminiz: ")
        if choice == '1':
            update_event(username)
        elif choice == '2':
            delete_event(username)
    else:
        print(f"{date} tarihinde herhangi bir etkinlik bulunamadı.")



def delete_event(username):
    # etkinlik silmek için kullanılır
    cursor.execute('SELECT * FROM events WHERE username = ?', (username,))
    events = cursor.fetchall()
    if not events:
        print("Hiçbir etkinlik bulunamadı.\n")
        return

    for i, event in enumerate(events, start=1):
        print(f"{i}. {event[1]} - {event[0]}")

    while True:
        event_number = input("Silinecek etkinlik numarası (geri dönmek için 'q'): ")
        if event_number.lower() == 'q':
            print("Etkinlik silme işlemi iptal edildi.\n")
            return
        try:
            event_number = int(event_number)
            if 1 <= event_number <= len(events):
                break
            else:
                print("Geçersiz etkinlik numarası. Lütfen tekrar deneyin.")
        except ValueError:
            print("Geçerli bir sayı girin.")

    event = events[event_number - 1]

    cursor.execute('DELETE FROM events WHERE eventTime = ? AND username = ?', (event[0], username))
    conn.commit()
    print("Etkinlik başarıyla silindi.\n")


# Admin fonksiyonları
def admin_functions(username):
    user_type = get_user_type(username)
    if user_type == 'Admin':
        while True:
            print("\n1. Tüm Kullanıcıları Listele")
            print("2. Kullanıcı Bilgilerini Düzenle")
            print("3. Kullanıcı Sil")
            print("4. Kullanıcıya Ait Etkinlik Düzenle")
            print("5. Ana Menüye Dön")
            choice = input("Seçiminiz: ")

            if choice == '1':
                get_all_users()
            elif choice == '2':
                edit_user_info(username)
            elif choice == '3':
                delete_user(username)
            elif choice == '4':
                edit_user_events(username)
            elif choice == '5':
                break
            else:
                print("Geçersiz seçim. Lütfen tekrar deneyin.\n")
    else:
        print("Geçersiz seçim. Lütfen tekrar deneyin.")


def get_all_users():
    # Tüm kullanıcıları getirme
    cursor.execute('SELECT * FROM users')
    print("Kullanıcılar:")
    for row in cursor.fetchall():
        print(row)
    print()

def edit_user_events(admin_username):
    # Kullanıcının etkinliklerini düzenleme
    username = input("Etkinliklerini düzenlemek istediğiniz kullanıcının kullanıcı adı: ")
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    if user:
        while True:
            print("\n1. Kullanıcının tüm etkinliklerini listele")
            print("2. Kullanıcının etkinlik bilgilerini güncelle")
            print("3. Kullanıcının bir etkinliğini sil")
            print("4. Ana Menüye Dön")
            choice = input("Seçiminiz: ")

            if choice == '1':
                list_events(username)
            elif choice == '2':
                update_event(username)
            elif choice == '3':
                delete_event(username)
            elif choice == '4':
                break
            else:
                print("Geçersiz seçim. Lütfen tekrar deneyin.\n")
    else:
        print("Böyle bir kullanıcı bulunamadı.\n")


def edit_user_info(admin_username):
    # Kullanıcı bilgilerini düzenleme
    username = input("Bilgilerini düzenlemek istediğiniz kullanıcının kullanıcı adı: ")
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    if user:
        name = input("Ad [" + user[0] + "]: ") or user[0]
        surname = input("Soyad [" + user[1] + "]: ") or user[1]
        password = input("Şifre [" + user[3] + "]: ") or user[3]
        tckn = input("TC Kimlik No [" + user[4] + "]: ") or user[4]
        phone = input("Telefon [" + user[5] + "]: ") or user[5]
        email = input("Email [" + user[6] + "]: ") or user[6]
        address = input("Adres [" + user[7] + "]: ") or user[7]
        userType = input("Kullanıcı tipi (Admin, Kullanıcılar) [" + user[8] + "]: ") or user[8]
        cursor.execute(
            'UPDATE users SET name = ?, surname = ?, password = ?, tckn = ?, phone = ?, email = ?, address = ?, userType = ? WHERE username = ?',
            (name, surname, password, tckn, phone, email, address, userType, username))
        conn.commit()
        print("Kullanıcı bilgileri başarıyla güncellendi.\n")
    else:
        print("Böyle bir kullanıcı bulunamadı.\n")


def delete_user(admin_username):
    # Kullanıcı silme
    username = input("Silmek istediğiniz kullanıcının kullanıcı adı: ")
    cursor.execute('DELETE FROM users WHERE username = ?', (username,))
    conn.commit()
    print("Kullanıcı başarıyla silindi.\n")


current_user = None

while True:
    print("\n--- MENÜ ---\n")
    if current_user:
        print(f"Bugünün Tarihi ve Saati: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        upcoming_event = get_upcoming_event(current_user)
        if upcoming_event:
            print(f"En Yakın Etkinlik: {upcoming_event[1]} - {upcoming_event[0]}")
        else:
            print("Yaklaşan bir etkinlik yok.")
    if not current_user:

        print("\n1. Kayıt Ol")
        print("2. Giriş Yap")
        print("3. Çıkış")

    if current_user:
        print("1. Etkinlik Ekle")
        print("2. Etkinlikleri Listele")
        print("3. Etkinlik Güncelle")
        print("4. Belirli bir tarihteki etkinlikleri görüntüle ve yönet")
        print("5. Etkinlik Sil")
        if get_user_type(current_user) == "Admin":
            print("6. Admin İşlemleri")
        print("7. Çıkış")

    choice = input("Seçiminiz: ")
    if not current_user:
        if choice == '1':
            add_user()
        elif choice == '2':
            username = input("Kullanıcı adı: ")
            password = input("Şifre: ")
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            if cursor.fetchone():
                current_user = username
                print("Giriş başarılı.\n")
                threading.Thread(target=event_reminder, args=(username,)).start()
            else:
                print("Hatalı kullanıcı adı veya şifre.\n")
        elif choice == '3':
            break
        else:
            print("Geçersiz seçim. Lütfen tekrar deneyin.\n")
    else:
        if choice == '1':
            if current_user:
                add_event(current_user)
            else:
                print("Geçersiz seçim. Lütfen tekrar deneyin.\n")
        elif choice == '2':
            if current_user:
                list_events(current_user)
            else:
                print("Geçersiz seçim. Lütfen tekrar deneyin.\n")
        elif choice == '3':
            if current_user:
                update_event(current_user)
            else:
                print("Geçersiz seçim. Lütfen tekrar deneyin.\n")
        elif choice == '4':
            if current_user:
                view_events_on_date(current_user)
            else:
                print("Geçersiz seçim. Lütfen tekrar deneyin.\n")
        elif choice == '5':
            if current_user:
                delete_event(current_user)
            else:
                print("Geçersiz seçim. Lütfen tekrar deneyin.\n")
        elif choice == '6':
            if current_user:
                admin_functions(current_user)
            else:
                print("Geçersiz seçim. Lütfen tekrar deneyin.\n")
        elif choice == '7':
            break
        else:
            print("Geçersiz seçim. Lütfen tekrar deneyin.\n")

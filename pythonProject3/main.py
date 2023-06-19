import sqlite3
from datetime import datetime, timedelta
import re
import time
import threading

# Veritabanı bağlantısını kuruyoruz.
conn = sqlite3.connect('calendar_app.db')
cursor = conn.cursor()

# Kullanıcılar ve etkinlikler için tabloları oluşturuyoruz.
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
    FOREIGN KEY(username) REFERENCES users(username))
''')


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
    # Kullanıcı ekleme
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
    # Kullanıcı girişi
    username = input("Kullanıcı adı: ")
    password = input("Şifre: ")
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    if cursor.fetchone():
        return username
    else:
        print("Hatalı kullanıcı adı veya şifre.\n")
        return None


def add_event(username):
    # Etkinlik ekleme
    eventTime = input("Etkinlik zamanı (YYYY-MM-DD HH:MM formatında): ")
    eventType = input("Etkinlik tipi: ")
    eventDescription = input("Etkinlik açıklaması: ")
    cursor.execute('INSERT INTO events VALUES (?, ?, ?, ?)', (eventTime, eventType, eventDescription, username))
    conn.commit()
    print("Etkinlik başarıyla eklendi.\n")


def list_events(username):
    # Etkinlikleri listeleme
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
    # Etkinlik güncelleme
    eventTime = input("Güncellenecek etkinliğin zamanı: ")
    cursor.execute('SELECT * FROM events WHERE eventTime = ? AND username = ?', (eventTime, username))
    event = cursor.fetchone()
    if event:
        newEventTime = input("Yeni olay zamanı [" + event[0] + "]: ") or event[0]
        newEventType = input("Yeni olay tipi [" + event[1] + "]: ") or event[1]
        newEventDescription = input("Yeni olay açıklaması [" + event[2] + "]: ") or event[2]
        cursor.execute(
            'UPDATE events SET eventTime = ?, eventType = ?, eventDescription = ? WHERE eventTime = ? AND username = ?',
            (newEventTime, newEventType, newEventDescription, eventTime, username))
        conn.commit()
        print("Olay başarıyla güncellendi.\n")
    else:
        print("Böyle bir etkinlik bulunamadı.\n")

def get_user_type(username):
    cursor.execute('SELECT userType FROM users WHERE username = ?', (username,))
    user_type = cursor.fetchone()
    if user_type:
        return user_type[0]
    else:
        return None



def delete_event(username):
    # Etkinlik silme
    eventTime = input("Silinecek etkinliğin zamanı: ")
    cursor.execute('DELETE FROM events WHERE eventTime = ? AND username = ?', (eventTime, username))
    conn.commit()
    print("Etkinlik başarıyla silindi.\n")


def event_reminder(username):
    # Etkinlik hatırlatıcı
    while True:
        # Her thread için yeni bir bağlantı ve cursor oluşturuluyor.
        conn_thread = sqlite3.connect('calendar_app.db')
        cursor_thread = conn_thread.cursor()

        cursor_thread.execute('SELECT * FROM events WHERE username = ?', (username,))
        for row in cursor_thread.fetchall():
            event_time = datetime.strptime(row[0], "%Y-%m-%d %H:%M")
            if event_time - timedelta(minutes=30) <= datetime.now() <= event_time:
                print(f"Hatırlatıcı: {username}, {row[1]} etkinliğiniz 30 dakika içinde başlayacak!")

            # Thread'in yüksek CPU kullanımını önlemek için bekleme süresi ekleniyor.
        time.sleep(60)

        # Yeni bir thread oluşturuyoruz ve event_reminder fonksiyonunu bu thread'de çalıştırıyoruz.
        reminder_thread = threading.Thread(target=event_reminder, args=(username,))
        reminder_thread.start()


# Admin fonksiyonları
def admin_functions(username):
    # Admin işlemleri
    user_type = get_user_type(username)
    if user_type == 'Admin':
        while True:
            print("\n1. Tüm Kullanıcıları Listele")
            print("2. Kullanıcı Bilgilerini Düzenle")
            print("3. Kullanıcı Sil")
            print("4. Ana Menüye Dön")
            choice = input("Seçiminiz: ")

            if choice == '1':
                get_all_users()
            elif choice == '2':
                edit_user_info(username)
            elif choice == '3':
                delete_user(username)
            elif choice == '4':
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
    print("1. Kayıt Ol")
    print("2. Giriş Yap")
    if current_user:
        print("3. Olay Ekle")
        print("4. Olayları Listele")
        print("5. Olay Güncelle")
        print("6. Olay Sil")
        if get_user_type(current_user) == "Admin":
            print("7. Admin İşlemleri")
    print("8. Çıkış")
    choice = input("Seçiminiz: ")


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
        if current_user:
            add_event(current_user)
        else:
            print("Lütfen önce giriş yapın.\n")
    elif choice == '4':
        if current_user:
            list_events(current_user)
        else:
            print("Lütfen önce giriş yapın.\n")
    elif choice == '5':
        if current_user:
            update_event(current_user)
        else:
            print("Lütfen önce giriş yapın.\n")
    elif choice == '6':
        if current_user:
            delete_event(current_user)
        else:
            print("Lütfen önce giriş yapın.\n")
    elif choice == '7':
        if current_user:
            admin_functions(current_user)
        else:
            print("Lütfen önce giriş yapın.\n")
    elif choice == '8':
        break
    else:
        print("Geçersiz seçim. Lütfen tekrar deneyin.\n")

# zPass Frontend - Masaüstü Uygulaması

zPass için güvenli masaüstü şifre yöneticisi uygulaması. PyQt6 ile geliştirilmiş, client-side şifreleme destekli modern arayüz.

## 🌟 Özellikler

- 🖥️ **Modern Masaüstü Arayüzü** - PyQt6 ile geliştirilmiş kullanıcı dostu arayüz
- 🔐 **Client-Side Şifreleme** - Verileriniz sunucuya gönderilmeden önce şifrelenir
- 🌐 **Esnek Sunucu Desteği** - Kendi sunucunuz, resmi sunucu veya localhost
- 🔑 **Gelişmiş Şifre Yönetimi** - Şifre ekleme, düzenleme, silme ve arama
- ⚡ **Güçlü Şifre Üretici** - Özelleştirileb ilir şifre üretimi
- 🎨 **Tema Desteği** - Açık/Koyu tema seçenekleri
- 📂 **Kategori Yönetimi** - Şifrelerinizi düzenli tutun
- ⚙️ **Kapsamlı Ayarlar** - Güvenlik, görünüm ve senkronizasyon ayarları

## 📋 Sistem Gereksinimleri

- Windows 10/11, macOS 10.14+, veya Linux
- Python 3.8 veya üzeri
- 100 MB disk alanı (minimum)
- İnternet bağlantısı (sunucu senkronizasyonu için)

## 🚀 Kurulum

### 1. Proje Dosyalarını İndirin
```bash
git clone <proje-url>
cd zPass/frontend
```

### 2. Sanal Ortam Oluşturun
```bash
# Sanal ortam oluştur
python -m venv venv

# Windows'ta aktif et
venv\Scripts\activate

# Linux/macOS'ta aktif et
source venv/bin/activate
```

### 3. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 4. Uygulamayı Başlatın
```bash
python main.py
```

## 🏠 Sunucu Bağlantı Seçenekleri

zPass frontend uygulaması farklı sunucu türlerine bağlanabilir:

### 1. Localhost (Yerel Geliştirme)
- **Adres:** `http://127.0.0.1:5000`
- **Kullanım:** Backend'i kendi makinenizde çalıştırırken
- **Kurulum:** Backend README'sini takip ederek yerel sunucuyu başlatın

### 2. Kendi Sunucunuz (Self-Hosted)
- **Adres örnek:** `https://password.benimsite.com`
- **Kullanım:** Kendi VPS/cloud sunucunuzda barındırdığınız backend

#### Özel Sunucuya Bağlanma Adımları:
1. Login ekranında **"Özel Sunucu"** seçeneğini seçin
2. Sunucu URL'nizi girin (örn: `https://password.benimsite.com`)
3. **"Sunucuyu Test Et"** butonuna tıklayarak bağlantıyı doğrulayın
4. Normal şekilde giriş yapin veya kayıt olun

#### Kendi Sunucunuzu Kurma:
1. Bir VPS sağlayıcısından sunucu kiralayın (DigitalOcean, Linode, AWS, vb.)
2. Backend README'sindeki kurulum adımlarını takip edin
3. HTTPS sertifikası kurarak güvenli bağlantı sağlayın
4. Frontend'de sunucu URL'nizi kaydedin

### 3. Resmi Sunucu
- **Adres:** `https://api.zpass.app` (örnek)
- **Kullanım:** Resmi barındırılan hizmet
- **Not:** Şu anda mevcut değil - kendi sunucunuzu kullanın

## ⚙️ Yapılandırma

### Sunucu Ayarları
Login ekranından **"Ayarlar"** → **"Sunucu"** bölümünden:
- Varsayılan sunucu tipini seçin
- Özel sunucu URL'leri ekleyin/kaldırın
- Bağlantı zaman aşımını ayarlayın

### Güvenlik Ayarları
**"Ayarlar"** → **"Güvenlik"** bölümünden:
- Otomatik kilit süresini ayarlayın
- Şifre üretici varsayılanlarını belirleyin
- Clipboard otomatik temizleme süresi

### Görünüm Ayarları
**"Ayarlar"** → **"Görünüm"** bölümünden:
- Açık/Koyu tema seçimi
- Font boyutu ve ailesi
- Pencere davranışları

### Senkronizasyon Ayarları
**"Ayarlar"** → **"Senkronizasyon"** bölümünden:
- Otomatik senkronizasyon etkinleştirme
- Senkronizasyon aralığı ayarlama
- Başlangıçta senkronizasyon

## 🔐 Güvenlik Özellikleri

### Client-Side Şifreleme
- Tüm verileriniz cihazınızda şifrelenir
- Ana şifreniz asla sunucuya gönderilmez
- AES-256 şifreleme kullanılır
- PBKDF2 ile anahtar türetimi

### Güvenli Veri Aktarımı
- HTTPS/TLS ile şifrelenmiş iletişim
- JWT token tabanlı kimlik doğrulama
- Session yönetimi ve otomatik kilit

## 🛠️ Kullanım Kılavuzu

### İlk Kullanım
1. Uygulamayı başlatın
2. Sunucu tipini seçin (Localhost/Özel/Resmi)
3. Yeni hesap oluşturun veya mevcut hesabınızla giriş yapın
4. Ana şifrenizi belirleyin (güçlü bir şifre seçin!)

### Şifre Ekleme
1. **"Şifre Ekle"** butonuna tıklayın
2. Gerekli alanları doldurun:
   - Başlık (örn: "Gmail Hesabım")
   - Kullanıcı adı/Email
   - Şifre
   - Website URL'si
   - Kategori (isteğe bağlı)
   - Notlar (isteğe bağlı)
3. **"Kaydet"** butonuna tıklayın

### Şifre Üretme
1. **"Şifre Üret"** butonuna tıklayın veya şifre ekleme ekranındaki **"Üret"** sekmesini kullanın
2. Şifre uzunluğunu ayarlayın (8-64 karakter)
3. Karakter tiplerini seçin:
   - Büyük harfler (A-Z)
   - Küçük harfler (a-z)
   - Sayılar (0-9)
   - Semboller (!@#$%^&*)
4. **"Şifre Üret"** butonuna tıklayın
5. **"Bu Şifreyi Kullan"** ile şifreyi form alanına kopyalayın

### Arama ve Filtreleme
- Üst kısımdaki arama kutusunu kullanın
- Kategorilere göre filtreleyin
- Başlık, kullanıcı adı veya website'e göre arama yapın

## 🔒 Güvenlik İpuçları

1. **Güçlü Ana Şifre:** En az 12 karakter, büyük/küçük harf, sayı ve sembol içeren bir ana şifre seçin
2. **Şifre Çeşitliliği:** Her hesap için farklı şifre kullanın
3. **Düzenli Güncelleme:** Önemli hesaplarınızın şifrelerini düzenli olarak güncelleyin
4. **Güvenli Bağlantı:** HTTPS kullanan sunuculara bağlanın
5. **Güvenilir Ağ:** Güvenilir internet bağlantıları kullanın

## 🐛 Sorun Giderme

### Bağlantı Sorunları
- Sunucu URL'sinin doğru olduğundan emin olun
- İnternet bağlantınızı kontrol edin
- Güvenlik duvarı ayarlarınızı gözden geçirin

### Ana Şifre Sorunları
- Ana şifrenizi doğru girdiğinizden emin olun
- Caps Lock tuşunun durumunu kontrol edin

### Performans Sorunları
- Uygulamayı yeniden başlatın
- Ayarlardan tema değiştirmeyi deneyin

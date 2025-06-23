# zPass - Güvenli Şifre Yöneticisi

Modern, güvenli ve self-hostable (kendi sunucunuzda barındırılabilir) şifre yöneticisi. Client-side şifreleme ile verileriniz her zaman güvende kalır.

## 🌟 Temel Özellikler

- 🔐 **Client-Side Şifreleme** - Verileriniz cihazınızda şifrelenir, sunucuya şifreli gönderilir
- 🖥️ **Modern Masaüstü Arayüzü** - PyQt6 ile geliştirilmiş kullanıcı dostu arayüz
- 🏠 **Self-Hostable** - Kendi sunucunuzda barındırabilirsiniz
- 🌐 **Esnek Sunucu Desteği** - Localhost, özel sunucu veya resmi sunucu seçenekleri
- 🔑 **Gelişmiş Şifre Yönetimi** - Şifre ekleme, düzenleme, silme ve arama
- ⚡ **Güçlü Şifre Üretici** - Özelleştirilebilir şifre üretimi
- 🎨 **Tema Desteği** - Açık/Koyu tema seçenekleri
- 📂 **Kategori Yönetimi** - Şifrelerinizi düzenli tutun
- ⚙️ **Kapsamlı Ayarlar** - Güvenlik, görünüm ve senkronizasyon ayarları
- 🔄 **Otomatik Senkronizasyon** - Verilerinizi otomatik olarak senkronize edin

## 🏗️ Proje Yapısı

```
zPass/
├── backend/          # Flask API sunucusu
│   ├── app/         # Flask uygulama kodu
│   ├── instance/    # SQLite veritabanı
│   └── README.md    # Backend kurulum kılavuzu
├── frontend/        # PyQt6 masaüstü uygulaması
│   ├── src/         # Uygulama kaynak kodu
│   ├── assets/      # Uygulama kaynakları
│   └── README.md    # Frontend kurulum kılavuzu
└── README.md        # Bu dosya
```

## 🚀 Hızlı Başlangıç

### Seçenek 1: Otomatik Başlatma (Önerilen)

**Windows için:**
```cmd
# Backend başlatma
backend\start.bat

# Frontend başlatma (yeni terminal penceresi)
frontend\start.bat
```

**Linux/macOS için:**
```bash
# Backend başlatma
./backend/start.sh

# Frontend başlatma (yeni terminal penceresi)
./frontend/start.sh
```

### Seçenek 2: Manuel Kurulum

1. **Backend'i başlatın:**
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/macOS
   pip install -r requirements.txt
   python run.py
   ```

2. **Frontend'i başlatın:**
   ```bash
   cd frontend
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/macOS
   pip install -r requirements.txt
   python main.py
   ```

3. **Kullanmaya başlayın:**
   - Frontend açıldığında "Localhost" seçeneğini seçin
   - Yeni hesap oluşturun veya giriş yapın
   - Şifrelerinizi eklemeye başlayın!

### Seçenek 3: Kendi Sunucunuzda Barındırma

1. **VPS/Cloud sunucu kiralayın** (DigitalOcean, Linode, AWS, vb.)
2. **Backend kurulumu için** `backend/README.md` dosyasını takip edin
3. **Domain ve SSL sertifikası** alın
4. **Frontend'de özel sunucu** olarak kendi domain'inizi ekleyin

## 📋 Sistem Gereksinimleri

### Backend
- Python 3.8+
- 50 MB disk alanı
- 512 MB RAM (minimum)

### Frontend
- Python 3.8+
- Windows 10/11, macOS 10.14+, veya Linux
- 100 MB disk alanı
- 256 MB RAM (minimum)

## 🔐 Güvenlik

### Client-Side Şifreleme
- **AES-256** şifreleme kullanılır
- **PBKDF2** ile anahtar türetimi (100,000 iterasyon)
- Ana şifreniz asla sunucuya gönderilmez
- Verileriniz cihazınızda şifrelenir

### Sunucu Güvenliği
- **JWT** token tabanlı kimlik doğrulama
- **bcrypt** ile şifre hashleme
- **HTTPS/TLS** şifrelenmiş iletişim
- **CORS** yapılandırması

## 📚 Detaylı Kurulum Kılavuzları

Her bileşen için detaylı kurulum kılavuzları mevcuttur:

- **[Backend Kurulum Kılavuzu](backend/README.md)** - Sunucu kurulumu, self-hosting, SSL yapılandırması
- **[Frontend Kurulum Kılavuzu](frontend/README.md)** - Masaüstü uygulaması, özel sunucu bağlantısı

## 🌐 Self-Hosting Seçenekleri

### 1. Yerel Ağ (Ev/Ofis)
- Ev/ofis ağınızda bir bilgisayarda çalıştırın
- Yerel IP ile erişim: `http://192.168.1.100:5000`
- Port forwarding ile internetten erişim

### 2. VPS/Cloud Sunucu
- **DigitalOcean** - $5/ay başlangıç
- **Linode** - $5/ay başlangıç  
- **AWS EC2** - Ücretsiz katman mevcut
- **Hetzner** - $3/ay başlangıç

### 3. Raspberry Pi
- Raspberry Pi 3/4 ile ev sunucusu
- 24/7 çalışan düşük güç tüketimi
- DynDNS ile dinamik IP çözümü

## 🛠️ Geliştirme

### Teknoloji Stack'i

**Backend:**
- Python 3.8+
- Flask (Web framework)
- SQLAlchemy (ORM)
- JWT (Authentication)
- SQLite (Database)

**Frontend:**
- Python 3.8+
- PyQt6 (GUI framework)
- PyCryptodome (Encryption)
- Requests (HTTP client)

### Katkıda Bulunma

1. Projeyi fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 🚨 Güvenlik Uyarıları

- ⚠️ **Ana şifrenizi unutmayın** - Kurtarma seçeneği yoktur
- 🔒 **Güçlü ana şifre** kullanın (en az 12 karakter)
- 🌐 **HTTPS kullanın** (üretim ortamında)
- 🔄 **Güncel tutun** - Güvenlik güncellemelerini kaçırmayın

## 📞 Destek ve İletişim

- **Dokümantasyon:** README dosyalarını inceleyin
- **Sorun Bildirimi:** GitHub Issues kullanın
- **Güvenlik Sorunları:** Güvenlik açıklarını sorumlu bir şekilde bildirin

## 📄 Lisans

[Lisans bilgisi buraya eklenecek]

---

**🔒 Güvenlik ve Gizlilik İlk Önceliğimizdir**

zPass, verilerinizin güvenliğini en üst düzeyde tutmak için tasarlanmıştır. Client-side şifreleme sayesinde verileriniz sadece sizin kontrolünüzdedir.

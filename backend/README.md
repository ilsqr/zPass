# zPass Backend - Sunucu Uygulaması

zPass için güvenli, self-hostable (kendi sunucunuzda barındırılabilir) şifre yöneticisi backend uygulaması.

## 🌟 Özellikler

- 🔐 **JWT Kimlik Doğrulama** - Güvenli token tabanlı kimlik doğrulama
- 🛡️ **Şifrelenmiş Vault Depolama** - İstemci tarafı şifreleme ile güvenli depolama
- 🗄️ **SQLite Veritabanı** - Hafif, dosya tabanlı veritabanı
- 🔑 **Güvenli Şifre Hashleme** - bcrypt ile güvenli şifre saklama
- 📡 **RESTful API** - Temiz ve düzenli API uç noktaları
- 🌐 **CORS Desteği** - Cross-origin kaynak paylaşımı etkin
- ⚡ **Yüksek Performans** - Hızlı ve hafif Flask backend

## 📋 Sistem Gereksinimleri

- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)
- 50 MB disk alanı (minimum)

## 🚀 Kurulum

### 1. Proje Dosyalarını İndirin
```bash
git clone <proje-url>
cd zPass/backend
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

### 4. Ortam Yapılandırması
Backend klasöründe `.env` dosyası oluşturun:

```env
# JWT token'ları için gizli anahtar (güvenli bir rastgele string oluşturun)
SECRET_KEY=burayı-çok-güvenli-bir-anahtarla-değiştirin

# Veritabanı yapılandırması
DATABASE_URL=sqlite:///instance/zpass.db

# JWT yapılandırması
JWT_ACCESS_TOKEN_EXPIRES=86400

# Sunucu yapılandırması
FLASK_ENV=production
DEBUG=False
```

**🔒 Güvenlik Notu:** Mutlaka güçlü ve benzersiz bir `SECRET_KEY` oluşturun:
```python
import secrets
print(secrets.token_hex(32))
```

### 5. Sunucuyu Başlatın
```bash
python run.py
```
Veritabanı ilk çalıştırmada otomatik olarak oluşturulacaktır.

## 🏠 Self-Hosting (Kendi Sunucunuzda Barındırma)

### Seçenek 1: Yerel Geliştirme
```bash
python run.py
```
- Sunucu adresi: `http://127.0.0.1:5000`
- Geliştirme ve test için idealdir

### Seçenek 2: Docker ile Dağıtım
`Dockerfile` oluşturun:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

Oluşturun ve çalıştırın:
```bash
docker build -t zpass-backend .
docker run -p 5000:5000 -v $(pwd)/instance:/app/instance zpass-backend
```

## 📊 API Uç Noktaları

### Kimlik Doğrulama
- `POST /api/auth/register` - Yeni kullanıcı kaydı
- `POST /api/auth/login` - Kullanıcı girişi
- `GET /api/auth/verify` - JWT token doğrulama

### Vault Yönetimi
- `GET /api/vault` - Kullanıcının şifrelenmiş vault'unu getir
- `PUT /api/vault` - Vault güncelle

## 🔧 Veritabanı Yönetimi

### Yedekleme
Veritabanınızı düzenli olarak yedeklemenizi öneririz:
```bash
# SQLite yedekleme
cp instance/zpass.db yedek/zpass_$(date +%Y%m%d_%H%M%S).db
```

### Geri Yükleme
```bash
cp yedek/zpass_YYYYMMDD_HHMMSS.db instance/zpass.db
```

## 🛡️ Güvenlik Önerileri

1. **Gizli Anahtarı Değiştirin** - Varsayılan SECRET_KEY'i mutlaka değiştirin
2. **HTTPS Kullanın** - Üretimde SSL/TLS olmadan çalıştırmayın
3. **Güvenlik Duvarı** - Sadece gerekli portlara erişim verin
4. **Düzenli Güncellemeler** - Bağımlılıkları güncel tutun
5. **Yedekleme Stratejisi** - Düzenli veritabanı yedeklemeleri yapın
6. **Log İzleme** - Şüpheli aktiviteler için logları izleyin

**🔒 Hatırlatma: Bu self-hosted bir çözümdür. Dağıtımınızın güvenliği ve bakımından siz sorumlusunuz.**
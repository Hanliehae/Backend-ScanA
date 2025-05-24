# ScanA Backend

Backend untuk aplikasi ScanA - Sistem Absensi dengan Pemindaian Telapak Tangan.

## Setup

1. Buat virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Pastikan model CNN sudah ada di `src/ml_models/hand_recognition_model.h5`

4. Jalankan aplikasi:
```bash
python app.py
```

## Struktur Direktori

```
backendnew-ScanA/
├── app.py                 # Entry point aplikasi
├── requirements.txt       # Daftar dependensi
├── src/
│   ├── database/         # Konfigurasi dan model database
│   │   ├── api/         # API endpoints
│   │   ├── models/      # Model database
│   │   └── migrations/  # Migrasi database
│   ├── ml_models/       # Model machine learning
│   ├── storage/         # Penyimpanan file
│   └── utils/           # Utility functions
```

## API Endpoints

### Hand Scan
- `POST /api/scan-hand`: Memindai telapak tangan dan mencatat kehadiran
  - Body: `multipart/form-data`
    - `image`: File gambar telapak tangan
    - `course_id`: ID mata kuliah

### Auth
- `POST /api/auth/login`: Login user
- `POST /api/auth/register`: Register user baru

### Courses
- `GET /api/courses`: Daftar mata kuliah
- `POST /api/courses`: Tambah mata kuliah baru

### Classes
- `GET /api/classes`: Daftar kelas
- `POST /api/classes`: Tambah kelas baru

### Meetings
- `GET /api/meetings`: Daftar pertemuan
- `POST /api/meetings`: Tambah pertemuan baru

### Attendance
- `GET /api/attendance`: Daftar kehadiran
- `POST /api/attendance`: Catat kehadiran

## Catatan

1. Pastikan model CNN sudah ada di direktori yang benar
2. Pastikan direktori storage sudah ada dan memiliki permission yang benar
3. Pastikan database SQLite sudah dibuat dan dimigrasi
4. Pastikan semua dependensi sudah terinstall dengan benar 
# Data Analysis Project

Proyek ini berisi:
- Notebook analisis data: `Proyek_Analisis_Data.ipynb`
- Dashboard Streamlit: `dashboard/dashboard.py`

## 1) Setup environment

Disarankan menggunakan virtual environment.

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## 2) Install dependencies

Dari root project (`data-analysis`), jalankan:

```bash
pip install -r requirements.txt
```

## 3) Menjalankan dashboard Streamlit

Tetap dari root project (`data-analysis`):

```bash
streamlit run dashboard/dashboard.py
```

Setelah jalan, buka URL yang muncul di terminal (biasanya `http://localhost:8501`).

## 4) Menjalankan notebook (opsional)

```bash
jupyter notebook
```

Lalu buka file `Proyek_Analisis_Data.ipynb`.

---

## Troubleshooting singkat

- Jika `streamlit: command not found`, pastikan virtual environment aktif.
- Jika port 8501 sudah dipakai:
  ```bash
  streamlit run dashboard/dashboard.py --server.port 8502
  ```
- Jika ada error dependency, update installer lalu install ulang:
  ```bash
  python -m pip install --upgrade pip
  pip install -r requirements.txt
  ```

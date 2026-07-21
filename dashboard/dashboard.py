from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

WIND_ICON_URL = "https://cdn-icons-png.flaticon.com/512/72/72579.png"

st.set_page_config(
    page_title="Beijing Air Quality Dashboard",
    page_icon=WIND_ICON_URL,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set gaya umum seaborn
sns.set_theme(style="whitegrid")

BASE_DIR = Path(__file__).resolve().parent

@st.cache_data
def load_data(filepath):
    """Load CSV data and parse datetime. Cached for performance."""
    df = pd.read_csv(filepath)

    # Memastikan kolom datetime dikonversi dengan benar
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
    else:
        # Fallback jika datetime menjadi index saat di-export
        df['datetime'] = pd.to_datetime(df.iloc[:, 0])

    return df

def bin_wind_speed(speed):
    """Group wind speed (WSPM) into categories."""
    if speed < 2.0:
        return '1. Lemah (< 2 m/s)'
    elif speed <= 4.0:
        return '2. Sedang (2 - 4 m/s)'
    else:
        return '3. Kencang (> 4 m/s)'

# Memuat dataset berdasarkan lokasi file dashboard.py (aman walau cwd berubah)
DATA_PATH = BASE_DIR / "air_quality_data.csv"
data = load_data(DATA_PATH)

# Menambahkan kolom kategorikal untuk analisis Streamlit
data['wind_category'] = data['WSPM'].apply(bin_wind_speed)
data['month'] = data['datetime'].dt.month
data['year'] = data['datetime'].dt.year

st.sidebar.image(WIND_ICON_URL, width=80)
st.sidebar.title("Filter Data")

# Filter 1: Rentang Tahun
min_year = int(data['year'].min())
max_year = int(data['year'].max())
selected_years = st.sidebar.slider(
    "Pilih Rentang Tahun:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Filter 2: Multiselect Stasiun
all_stations = data['station'].unique().tolist()
selected_stations = st.sidebar.multiselect(
    "Pilih Stasiun Pemantauan:",
    options=all_stations,
    default=all_stations
)

# Mengaplikasikan Filter ke Data Mainframe
filtered_df = data[
    (data['year'] >= selected_years[0]) &
    (data['year'] <= selected_years[1]) &
    (data['station'].isin(selected_stations))
]

# Validasi jika filter menghasilkan DataFrame kosong
if filtered_df.empty:
    st.warning("Data tidak ditemukan untuk kombinasi filter ini. Silakan sesuaikan filter di sidebar.")
    st.stop()

st.title("Beijing Air Quality Interactive Dashboard")
st.markdown("""
Dashboard ini menyajikan analisis interaktif tren kualitas udara (**PM2.5**) dan hubungannya dengan faktor meteorologi (kecepatan angin) di Beijing berdasarkan data pemantauan berkala.
""")

st.divider()

# --- METRIC CARDS OVERVIEW ---
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

avg_pm25 = filtered_df['PM2.5'].mean()
max_pm25 = filtered_df['PM2.5'].max()
avg_wspm = filtered_df['WSPM'].mean()
total_records = len(filtered_df)

col_m1.metric("Rata-rata PM2.5", f"{avg_pm25:.2f} µg/m³")
col_m2.metric("PM2.5 Tertinggi", f"{max_pm25:.1f} µg/m³")
col_m3.metric("Rata-rata Kecepatan Angin", f"{avg_wspm:.2f} m/s")
col_m4.metric("Total Observasi Data", f"{total_records:,}")

st.divider()

st.subheader("Analisis & Visualisasi Data")

tab1, tab2 = st.tabs(["Pertanyaan 1: Tren Musiman Bulanan", "Pertanyaan 2: Pengaruh Kecepatan Angin"])

# ------------------------------------------------------------------------------
# TAB 1: Tren Bulanan PM2.5
# ------------------------------------------------------------------------------
with tab1:
    st.markdown("### Pola Fluktuasi Bulanan Konsentrasi PM2.5")

    # Agregasi data bulanan berdasarkan hasil filter
    monthly_trend = filtered_df.groupby('month')['PM2.5'].mean().reset_index()

    fig1, ax1 = plt.subplots(figsize=(11, 5.5))
    sns.lineplot(
        data=monthly_trend,
        x='month',
        y='PM2.5',
        marker='o',
        color='#d9534f',
        linewidth=2.5,
        ax=ax1
    )

    ax1.set_title('Rata-rata Konsentrasi PM2.5 Per Bulan', fontsize=13, fontweight='bold', pad=12)
    ax1.set_xlabel('Bulan', fontsize=11)
    ax1.set_ylabel('Konsentrasi PM2.5 (µg/m³)', fontsize=11)
    ax1.set_xticks(range(1, 13))
    ax1.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'])
    ax1.set_ylim(40, max(monthly_trend['PM2.5'].max() + 15, 110))

    # Dynamic Annotation berdasarkan data terfilter
    max_row = monthly_trend.loc[monthly_trend['PM2.5'].idxmax()]
    min_row = monthly_trend.loc[monthly_trend['PM2.5'].idxmin()]

    ax1.annotate(
        f"Puncak Tertinggi\n({max_row['PM2.5']:.2f} µg/m³)",
        xy=(max_row['month'], max_row['PM2.5']),
        xytext=(max_row['month'] - 2.5 if max_row['month'] > 3 else max_row['month'] + 1, max_row['PM2.5'] + 5),
        arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
        fontsize=10, fontweight='semibold'
    )

    ax1.annotate(
        f"Titik Terendah\n({min_row['PM2.5']:.2f} µg/m³)",
        xy=(min_row['month'], min_row['PM2.5']),
        xytext=(min_row['month'] - 2, min_row['PM2.5'] + 10),
        arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
        fontsize=10, fontweight='semibold'
    )

    st.pyplot(fig1)

# ------------------------------------------------------------------------------
# TAB 2: Pengaruh Kecepatan Angin
# ------------------------------------------------------------------------------
with tab2:
    st.markdown("### Hubungan Kecepatan Angin (WSPM) Terhadap Dispersi PM2.5")

    # Agregasi data angin berdasarkan hasil filter
    wind_impact = filtered_df.groupby('wind_category', observed=False)['PM2.5'].mean().reset_index()

    fig2, ax2 = plt.subplots(figsize=(9, 5))
    sns.barplot(
        data=wind_impact,
        x='wind_category',
        y='PM2.5',
        palette='viridis_r',
        ax=ax2
    )

    ax2.set_title('Rata-Rata PM2.5 Berdasarkan Kategori Kecepatan Angin', fontsize=13, fontweight='bold', pad=12)
    ax2.set_xlabel('Kategori Kecepatan Angin', fontsize=11)
    ax2.set_ylabel('Rata-rata PM2.5 (µg/m³)', fontsize=11)

    # Direct Labeling
    for p in ax2.patches:
        height = p.get_height()
        if not pd.isna(height) and height > 0:
            ax2.annotate(
                f"{height:.2f} µg/m³",
                (p.get_x() + p.get_width() / 2., height - 6),
                ha='center', va='center', color='white', fontweight='bold', fontsize=10
            )

    st.pyplot(fig2)

st.divider()

st.subheader("Kesimpulan & Rekomendasi Bisnis")

col_c1, col_c2 = st.columns(2)

with col_c1:
    st.info("### Kesimpulan")
    st.markdown("""
    1. **Pola Musiman (Pertanyaan 1):** Konsentrasi `PM2.5` memiliki tren puncak pada musim dingin (Desember–Januari) dan titik terendah pada musim panas (Agustus).
    2. **Faktor Dispersi Angin (Pertanyaan 2):** Terdapat korelasi negatif yang kuat antara kecepatan angin dan kadar polusi. Angin kencang ($>4$ m/s) terbukti efektif menurunkan akumulasi partikulat hingga di bawah $30$ µg/m³.
    """)

with col_c2:
    st.success("### Rekomendasi Action Item")
    st.markdown("""
    * **Sistem Peringatan Dini Dinamis:** Integrasikan pemantauan cuaca dengan regulasi emisi.
    * **Intervensi Musim Dingin:** Perketat kuota emisi industri dan terapkan tarif transportasi publik bersubsidi pada bulan Oktober–Februari saat kecepatan angin terprediksi di bawah $2$ m/s.
    """)

# Opsi Opsional: Menampilkan Raw Data
with st.expander("Lihat Raw Data Terfilter"):
    st.dataframe(filtered_df)

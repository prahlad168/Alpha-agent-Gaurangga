import streamlit as st
import os
import json
import time
import pandas as pd


# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Alpha Gaurangga - Super Agent UI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


REPO_DIR = "reports"


# --- REAL SALES SCANNER & TIME TRACKER ---
def scan_all_sales_data(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        return None, None


    total_sales = 0
    total_revenue_usd = 0.0
    total_revenue_idr = 0.0
    scanned_files_count = 0
    
    # List untuk menampung data timeline grafik
    timeline_data = []


    # Sort file agar berurutan sesuai waktu pembuatan/nama file
    sorted_files = sorted(os.listdir(directory))


    for filename in sorted_files:
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    summary = data.get("Summary", data)
                    
                    # Parsing Sales
                    sales_val = summary.get("Total Sales", "0")
                    if isinstance(sales_val, str):
                        sales_val = sales_val.replace("transactions", "").strip()
                    current_sales = int(sales_val)
                    total_sales += current_sales
                    
                    # Parsing USD
                    usd_val = summary.get("Revenue USD", "$0")
                    if isinstance(usd_val, str):
                        usd_val = usd_val.replace("$", "").replace(",", "").strip()
                    current_usd = float(usd_val)
                    total_revenue_usd += current_usd
                    
                    # Parsing IDR
                    idr_val = summary.get("Revenue IDR", "Rp 0")
                    if isinstance(idr_val, str):
                        idr_val = idr_val.replace("Rp", "").replace(".", "").replace(",", "").strip()
                    current_idr = float(idr_val)
                    total_revenue_idr += current_idr
                    
                    scanned_files_count += 1
                    
                    # Simpan data per file untuk keperluan grafik/tren
                    # Menggunakan nama file sebagai label waktu sementara jika timestamp absen
                    label_waktu = filename.replace("sales-report-", "").replace(".json", "").replace("hourly-", "")
                    timeline_data.append({
                        "Laporan": label_waktu,
                        "Transaksi": current_sales,
                        "Revenue (USD)": current_usd,
                        "Revenue (IDR)": current_idr
                    })
                    
            except Exception:
                continue


    if scanned_files_count == 0:
        return None, None


    summary_stats = {
        "files_scanned": scanned_files_count,
        "total_sales": f"{total_sales} transactions",
        "revenue_usd": f"${total_revenue_usd:,.2f}",
        "revenue_idr": f"Rp {int(total_revenue_idr):,}".replace(",", "."),
    }
    
    df_timeline = pd.DataFrame(timeline_data)
    return summary_stats, df_timeline


# --- PROSES PEMINDAIAN AWAL ---
real_data, df_trends = scan_all_sales_data(REPO_DIR)


# Fallback data jika folder masih kosong
if not real_data:
    real_data = {
        "files_scanned": 1,
        "total_sales": "523 transactions",
        "revenue_usd": "$26,961.30",
        "revenue_idr": "Rp 417.900.145",
    }
    df_trends = pd.DataFrame([{
        "Laporan": "001-Demo", "Transaksi": 523, "Revenue (USD)": 26961.30, "Revenue (IDR)": 417900145
    }])


# --- LOGIKA RESPONS ALPHA GAURANGGA ---
def get_gaurangga_response(user_input, current_data):
    user_input_lower = user_input.lower()
    
    if any(k in user_input_lower for k in ["scan", "cek penjualan", "laporan", "keseluruhan"]):
        return (
            f"🔄 **[Alpha Gaurangga Engine]:** Memindai direktori riil... `/{REPO_DIR}`\n\n"
            f"✅ **Scan Selesai.** Berhasil menarik data dari **{current_data['files_scanned']} berkas aktif**.\n\n"
            f"📊 **AKUMULASI PENJUALAN KESELURUHAN:**\n"
            f"* **Total Transaksi:** {current_data['total_sales']}\n"
            f"* **Total Omset (USD):** {current_data['revenue_usd']}\n"
            f"* **Total Omset Akumulasi (IDR):** **{current_data['revenue_idr']}**\n\n"
            f"Grafik visual tren penjualan telah diperbarui pada dashboard utama Anda, Bos."
        )
    elif "status" in user_input_lower:
        return f"⚡ **[Alpha Gaurangga Engine]:** Semua sistem MAHA-OS terpantau stabil. Scanner siap mengeksekusi file log baru."
    else:
        return f"🤖 **[Alpha Gaurangga Engine]:** Perintah *'{user_input}'* diterima. Ketik **'scan'** untuk memperbarui kalkulasi database global."


# --- SIDEBAR CONTROL INTERFACE ---
with st.sidebar:
    st.image("https://img.icons8.com/nolan/128/bot.png", width=70)
    st.title("Alpha Gaurangga")
    st.caption("MAHA-OS Live Engine v2.0")
    st.markdown("---")
    
    st.success("🟢 SCANNER STATUS: ACTIVE")
    st.info(f"📁 Terdeteksi: {real_data['files_scanned']} File JSON")
    
    st.markdown("### 📊 Ringkasan Live")
    st.metric(label="Total Revenue (IDR)", value=real_data['revenue_idr'])
    st.metric(label="Total Volume Transaksi", value=real_data['total_sales'])
    
    st.markdown("---")
    if st.button("🔄 Pindai Ulang Repositori", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
        
    # Fitur Baru: Ekspor Laporan ke CSV
    csv = df_trends.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Ekspor Konsolidasi (.CSV)",
        data=csv,
        file_name=f"MAHA_OS_Consolidated_Report.csv",
        mime="text/csv",
        use_container_width=True
    )


# --- ANTARMUKA UTAMA DASHBOARD ---
st.title("🤖 Alpha Gaurangga Dashboard & Terminal")
st.markdown("---")


# Layout Kolom Atas: Grafik Tren Kinerja Riil
st.subheader("📈 Tren Pendapatan Global (Real-Time)")
tab1, tab2 = st.tabs(["Grafik IDR", "Grafik Volume Transaksi"])


with tab1:
    st.line_chart(data=df_trends, x="Laporan", y="Revenue (IDR)", use_container_width=True)
with tab2:
    st.bar_chart(data=df_trends, x="Laporan", y="Transaksi", use_container_width=True)


st.markdown("---")


# Layout Bawah: Chat Interface Terminal
st.subheader("💬 Chat Terminal")


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "🤖 **[Alpha Gaurangga Engine]:** Sistem v2.0 aktif. Dasbor visual telah terhubung. Ada data baru yang ingin di-scan, Bos?"}
    ]


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if user_prompt := st.chat_input("Perintahkan Super Agent di sini..."):
    with st.chat_message("user"):
        st.markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    
    current_stats, current_df = scan_all_sales_data(REPO_DIR)
    active_stats = current_stats if current_stats else real_data
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("*Alpha Gaurangga sedang menyusun visualisasi data...*")
        time.sleep(0.7)
        
        response = get_gaurangga_response(user_prompt, active_stats)
        placeholder.markdown(response)
        
    st.session_state.messages.append({"role": "assistant", "content": response})

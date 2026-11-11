import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

st.set_page_config(page_title="Bütçe Takip Sistemi", page_icon="💰", layout="wide")

DOSYA_ADI = "harcamalar.json"
AYAR_DOSYASI = "ayarlar.json"
KATEGORILER = ["Yemek", "Ulaşım", "Fatura", "Eğlence", "Alışveriş", "Diğer"]

def verileri_yukle():
    if os.path.exists(DOSYA_ADI):
        with open(DOSYA_ADI, "r", encoding="utf-8") as dosya:
            return json.load(dosya)
    return []

def verileri_kaydet(harcamalar):
    with open(DOSYA_ADI, "w", encoding="utf-8") as dosya:
        json.dump(harcamalar, dosya, ensure_ascii=False, indent=4)

def limiti_yukle():
    if os.path.exists(AYAR_DOSYASI):
        with open(AYAR_DOSYASI, "r", encoding="utf-8") as dosya:
            return json.load(dosya).get("limit", 10000.0)
    return 10000.0

def limiti_kaydet(yeni_limit):
    with open(AYAR_DOSYASI, "w", encoding="utf-8") as dosya:
        json.dump({"limit": yeni_limit}, dosya)

harcamalar = verileri_yukle()
butce_limiti = limiti_yukle()

with st.sidebar:
    st.header("⚙️ Ayarlar ve Filtreler")
    yeni_limit = st.number_input("Hedef Bütçe Limiti (TL)", min_value=100.0, step=500.0, value=float(butce_limiti))
    if yeni_limit != butce_limiti:
        limiti_kaydet(yeni_limit)
        st.rerun()

    st.divider()
    secilen_kategoriler = st.multiselect(
        "Kategorilere Göre Filtrele",
        options=KATEGORILER,
        default=KATEGORILER
    )

st.title("💰 Gelişmiş Kişisel Bütçe Takip Sistemi")

with st.expander("➕ Yeni Harcama Ekle", expanded=True):
    with st.form("harcama_formu", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            tutar = st.number_input("Tutar (TL)", min_value=0.01, step=10.0)
        with col2:
            kategori = st.selectbox("Kategori", KATEGORILER)
        with col3:
            aciklama = st.text_input("Açıklama")
        
        gonder = st.form_submit_button("Harcamayı Kaydet", use_container_width=True)
        
        if gonder:
            yeni_kayit = {
                "Tarih": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "Kategori": kategori,
                "Açıklama": aciklama if aciklama else "-",
                "Tutar (TL)": tutar
            }
            harcamalar.append(yeni_kayit)
            verileri_kaydet(harcamalar)
            st.success("Harcama başarıyla kaydedildi!")
            st.rerun()

st.divider()

if harcamalar:
    df = pd.DataFrame(harcamalar)
    filtrelenmis_df = df[df["Kategori"].isin(secilen_kategoriler)]
    genel_toplam = df["Tutar (TL)"].sum()
    filtreli_toplam = filtrelenmis_df["Tutar (TL)"].sum()
    kalan_butce = butce_limiti - genel_toplam

    m1, m2, m3 = st.columns(3)
    m1.metric("Genel Toplam Harcama", f"{genel_toplam:,.2f} TL")
    m2.metric("Filtrelenen Harcama", f"{filtreli_toplam:,.2f} TL")
    m3.metric("Kalan Bütçe", f"{kalan_butce:,.2f} TL", delta=f"{kalan_butce:,.2f} TL")

    oran = min(genel_toplam / butce_limiti, 1.0)
    st.progress(oran, text=f"Bütçe Kullanım Oranı: %{(genel_toplam / butce_limiti) * 100:.1f}")
    
    if genel_toplam > butce_limiti:
        st.error(f"⚠️ Dikkat! Belirlediğiniz {butce_limiti:,.2f} TL bütçe limitini aştınız!")
    elif genel_toplam >= butce_limiti * 0.8:
        st.warning("⚠️ Bütçe limitinizin %80'ine ulaştınız, harcamalara dikkat!")

    st.divider()

    sol_alan, sag_alan = st.columns(2)

    with sol_alan:
        st.subheader("📋 Harcama Listesi")
        st.dataframe(filtrelenmis_df, use_container_width=True)
        
        csv_verisi = filtrelenmis_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 Tabloyu Excel (CSV) Olarak İndir",
            data=csv_verisi,
            file_name=f"harcamalar_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with sag_alan:
        st.subheader("📊 Kategori Dağılımı")
        if not filtrelenmis_df.empty:
            kategori_ozeti = filtrelenmis_df.groupby("Kategori")["Tutar (TL)"].sum()
            st.bar_chart(kategori_ozeti)
        else:
            st.info("Grafik için en az bir kategori seçin.")

    st.divider()
    with st.expander("✏️ Kayıt Düzenle veya Sil"):
        secenekler = [
            f"{i + 1}. [{h['Tarih']}] {h['Kategori']} - {h['Açıklama']} ({h['Tutar (TL)']:.2f} TL)"
            for i, h in enumerate(harcamalar)
        ]
        
        secilen_metin = st.selectbox("İşlem yapmak istediğiniz harcamayı seçin:", secenekler)
        secilen_index = secenekler.index(secilen_metin)
        secilen_kayit = harcamalar[secilen_index]

        with st.form("duzenle_formu"):
            c1, c2, c3 = st.columns(3)
            with c1:
                yeni_tutar = st.number_input("Tutar (TL)", min_value=0.01, step=10.0, value=float(secilen_kayit["Tutar (TL)"]))
            with c2:
                mevcut_kat_index = KATEGORILER.index(secilen_kayit["Kategori"]) if secilen_kayit["Kategori"] in KATEGORILER else 0
                yeni_kategori = st.selectbox("Kategori", KATEGORILER, index=mevcut_kat_index)
            with c3:
                yeni_aciklama = st.text_input("Açıklama", value=secilen_kayit["Açıklama"])

            b1, b2 = st.columns(2)
            with b1:
                guncelle_butonu = st.form_submit_button("💾 Değişiklikleri Kaydet", use_container_width=True)
            with b2:
                sil_butonu = st.form_submit_button("🗑️ Bu Kaydı Sil", type="primary", use_container_width=True)

            if guncelle_butonu:
                harcamalar[secilen_index]["Tutar (TL)"] = yeni_tutar
                harcamalar[secilen_index]["Kategori"] = yeni_kategori
                harcamalar[secilen_index]["Açıklama"] = yeni_aciklama if yeni_aciklama else "-"
                verileri_kaydet(harcamalar)
                st.success("Kayıt başarıyla güncellendi!")
                st.rerun()

            if sil_butonu:
                harcamalar.pop(secilen_index)
                verileri_kaydet(harcamalar)
                st.warning("Kayıt silindi!")
                st.rerun()
else:
    st.info("Henüz kayıtlı bir harcama bulunmuyor. Yukarıdaki formu kullanarak ilk harcamanızı ekleyebilirsiniz.")


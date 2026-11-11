import streamlit as st
import json
import os
from datetime import datetime

DOSYA_ADI = "harcamalar.json"
KATEGORILER = ["Yemek", "Ulaşım", "Fatura", "Eğlence", "Alışveriş", "Diğer"]


def verileri_yukle():
    if os.path.exists(DOSYA_ADI):
        with open(DOSYA_ADI, "r", encoding="utf-8") as dosya:
            return json.load(dosya)
    return []


def verileri_kaydet(harcamalar):
    with open(DOSYA_ADI, "w", encoding="utf-8") as dosya:
        json.dump(harcamalar, dosya, ensure_ascii=False, indent=4)


st.title("💰 Kişisel Bütçe Takip Sistemi")

harcamalar = verileri_yukle()

# 1. BÖLÜM: YENİ HARCAMA EKLEME
with st.form("harcama_formu", clear_on_submit=True):
    st.subheader("➕ Yeni Harcama Ekle")
    tutar = st.number_input("Tutar (TL)", min_value=0.01, step=10.0)
    kategori = st.selectbox("Kategori", KATEGORILER)
    aciklama = st.text_input("Açıklama")

    gonder = st.form_submit_button("Harcamayı Kaydet")

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

# 2. BÖLÜM: LİSTELEME VE ÖZET
st.divider()
st.subheader("📊 Harcama Özeti ve Liste")

if harcamalar:
    toplam = sum(h["Tutar (TL)"] for h in harcamalar)
    st.metric(label="Genel Toplam Harcama", value=f"{toplam:.2f} TL")
    st.dataframe(harcamalar, use_container_width=True)

    # 3. BÖLÜM: KAYIT DÜZENLEME VE SİLME
    st.divider()
    st.subheader("✏️ Kayıt Düzenle veya Sil")

    # Kullanıcının kolay seçebilmesi için her kayda sıra numarası ve özet metin oluşturuyoruz
    secenekler = [
        f"{i + 1}. [{h['Tarih']}] {h['Kategori']} - {h['Açıklama']} ({h['Tutar (TL)']:.2f} TL)"
        for i, h in enumerate(harcamalar)
    ]

    secilen_metin = st.selectbox("İşlem yapmak istediğiniz harcamayı seçin:", secenekler)
    secilen_index = secenekler.index(secilen_metin)
    secilen_kayit = harcamalar[secilen_index]

    with st.form("duzenle_formu"):
        yeni_tutar = st.number_input("Tutar (TL)", min_value=0.01, step=10.0, value=float(secilen_kayit["Tutar (TL)"]))

        mevcut_kat_index = KATEGORILER.index(secilen_kayit["Kategori"]) if secilen_kayit[
                                                                               "Kategori"] in KATEGORILER else 0
        yeni_kategori = st.selectbox("Kategori", KATEGORILER, index=mevcut_kat_index)
        yeni_aciklama = st.text_input("Açıklama", value=secilen_kayit["Açıklama"])

        col1, col2 = st.columns(2)
        with col1:
            guncelle_butonu = st.form_submit_button("💾 Değişiklikleri Kaydet", use_container_width=True)
        with col2:
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
    st.info("Henüz kayıtlı bir harcama bulunmuyor.")


import streamlit as st
import pandas as pd 
import joblib

# import stałych i fukncji pomocniczych z pozostałych modułów
from config import DZIELNICE_COORDS, FEATURE_NAMES, PALAC_LAT, PALAC_LON
from utils import haversine, oblicz_rate_kredytu, create_pdf_report

# konfugiracja strony
st.set_page_config(page_title="System Analizy Rynku Nieruchomości", layout="wide")


# CSS
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
        display: none !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 16px;
    }
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
    }
    h1 {
        color: #1f2937;
        font-weight: 300;
        margin-bottom: 30px;    
    }
    </style>
    """, unsafe_allow_html=True)

# Używamy cache, aby modele ładowały się do pamięci RAM tylko raz.
@st.cache_resource
def load_models():
    model_sprzedaz = joblib.load('notebooks/najlepszy_model_sprzedaz.pkl')
    model_wynajem = joblib.load('notebooks/najlepszy_model_wynajem.pkl')
    return model_sprzedaz, model_wynajem

# Próba wczytania modeli
try:
    model_sprzedaz, model_wynajem = load_models()
except FileNotFoundError:
    st.error("Nie odnaleziono wymaganych plików")
    st.stop()


# Panel boczny
# Parametry wejściowe
st.sidebar.markdown("### Parametry wejściowe")
st.sidebar.write("Zmiana wartości automatycznie przelicza wyniki na wszystkich modułach.")
st.sidebar.markdown("---")

# Zebranie danych
metraz = st.sidebar.number_input("Powierzchnia (m²)", min_value=15.0, max_value=300.0, value=50.0, step=1.0)
pokoje = st.sidebar.slider("Liczba pokoi", 1, 10, 2)
pietro = st.sidebar.number_input("Piętro", min_value=0, max_value=30, value=1)
rok_budowy= st.sidebar.number_input("Rok budowy", min_value=1900, max_value=2025, value=2015)
wybrana_dzielnica = st.sidebar.selectbox("Lokalizacja", list(DZIELNICE_COORDS.keys()))

# Wyciągamy współrzędne dla wybranej dzielnicy i liczymy dystans do pałacu kultury i nauki w centrum Warszawy
lat, lon = DZIELNICE_COORDS[wybrana_dzielnica]
dist = haversine(lat, lon, PALAC_LAT, PALAC_LON)

# Pakujemy dane w DataFrame
dane_wejsciowe = pd.DataFrame([[metraz, pokoje, pietro, rok_budowy, dist]],
                              columns=['squareMeters', 'rooms', 'floor', 'buildYear', 'dist_to_center'])

# Predykcja cen
cena_zakupu = model_sprzedaz.predict(dane_wejsciowe)[0]
czyns_msc = model_wynajem.predict(dane_wejsciowe)[0]

# Podstawowy zwrot z inwestycji w skalii roku
roi_brutto = ((czyns_msc *12) / cena_zakupu) * 100


# Główny widok aplikacji - zakładki
st.title("System Analizy Rynku Nieruchomości")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Rynek Sprzedaży",
    "Rynek Najmu",
    "Symulacja Inwestycyjna (ROI)",
    "Ewaluacja Modeli",
    "Lokalizator"
])

# Zakładka sprzedaż
with tab1:
    st.markdown("#### Estymacja wartości rynkowej")
    st.metric(label="Prognozowana cena transakcyjna", value=f"{int(cena_zakupu):,} PLN".replace(',',' '))
    st.write(f"Średni koszt za m²: **{int(cena_zakupu/metraz):,} PLN**".replace(',',' '))
    st.markdown("---")
    st.markdown("**Rozkład istotniości parametrów modelu**")
    # wykres z feature_importances_ 
    chart_sprzedaz = pd.DataFrame({'Parametr': FEATURE_NAMES, 'Istotność': model_sprzedaz.feature_importances_}).set_index('Parametr')
    st.bar_chart(chart_sprzedaz)

# Zakładka wynajem
with tab2:
    st.markdown("#### Estymacja stawek najmu")
    st.metric(label="Prognozowany miesięczny czynsz", value=f"{int(czyns_msc):,} PLN".replace(',',' '))
    st.markdown("---")
    st.markdown("**Rozkład istotności parametrów modelu**")
    chart_wynajem = pd.DataFrame({'Parametr': FEATURE_NAMES, 'Istotność': model_wynajem.feature_importances_}).set_index('Parametr')
    st.bar_chart(chart_wynajem)

# Zakładka kalkulator finansowy
with tab3:
    st.markdown("#### Podsumowanie wskaźników inwestycyjnych")
    # bazowe wskaźniki bez uwzględnienia kosztów dodatkowych
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Szacowany nakład inwestycyjny", f"{int(cena_zakupu):,} PLN".replace(',',' '))
    col_b.metric("Prognozowany przychód roczny", f"{int(czyns_msc * 12):,} PLN".replace(',',' '))
    col_c.metric("Wskaźnik  ROI (Brutto bazowy)", f"{roi_brutto:.2f} %")

    st.markdown("---")
    st.markdown("#### Analiza wraźliwości i koszty operacyjne")
    # dodatkowe parametry urealmiające zysk z najmu
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        mies_najmu = st.slider("Liczba miesięcy najmu w roku", min_value=6, max_value=12, value=12, step=1)
    with col_s2:
        koszty_dodatkowe = st.number_input("Koszty początkowe (remont, notariusz) PLN", min_value=0.0, max_value=300000.0, value=25000.0, step=5000.0)

    calkowity_kapital = cena_zakupu + koszty_dodatkowe
    roczny_przychod_realny = czyns_msc * mies_najmu
    roi_skorygowane = (roczny_przychod_realny / calkowity_kapital) * 100

    st.markdown("---")
    st.markdown("#### Kalkulator kredytowy i dźwignia finansowa")
    uzyj_kredytu = st.checkbox("Symulacja zakupy na kredyt hipoteczny", value=False)

    # Zmienne potrzebne do raportu PDF
    rata_msc = 0.0
    wklad_wlasny_kwota = calkowity_kapital
    kwota_kredytu = 0.0
    cash_on_cash = roi_skorygowane

    # Ścieżka alternatywna - inwestor wspomaga się kredytem
    if uzyj_kredytu:
        col_k1, col_k2, col_k3 = st.columns(3)
        with col_k1:
            wklad_wlasny_proc = st.slider("Wkład własny (%)", 10, 90, 20, 5)
        with col_k2:
            oprocentowanie = st.number_input("Oprocentowanie roczne (%)", min_value=1.0, max_value=20.0, value=7.5, step=0.1)
        with col_k3:
            okres_kredytu = st.selectbox("Okres kredytowania (lata)", [10, 15, 20, 25, 30], index=3)

        #Obliczenie raty i stopy zwrotu z wkładu własnego
        wklad_wlasny_kwota = cena_zakupu * (wklad_wlasny_proc / 100.0) + koszty_dodatkowe     
        kwota_kredytu = cena_zakupu - (cena_zakupu * (wklad_wlasny_proc / 100.0))
        rata_msc = oblicz_rate_kredytu(kwota_kredytu, oprocentowanie, okres_kredytu)
        roczna_rata = rata_msc * 12
        roczny_zysk_netto = roczny_przychod_realny - roczna_rata

        # Zabezpieczenie przed dzieleniem przez zero w przypadku zerowego wkładu
        cash_on_cash = (roczny_zysk_netto / wklad_wlasny_kwota) * 100 if wklad_wlasny_kwota > 0 else 0

        res_k1, res_k2, res_k3, res_k4 = st.columns(4)
        res_k1.metric("Wkład właśny + koszty", f"{int(wklad_wlasny_kwota):,} PLN".replace(',',' '))
        res_k2.metric("Miesięczna rata kredytu", f"{int(rata_msc):,} PLN".replace(',',' '))
        res_k3.metric("Roczny zysk po spłacie rat", f"{int(roczny_zysk_netto):,} PLN".replace(',',' '))
        res_k4.metric("Zwrot Cash-on-Cash", f"{cash_on_cash:.2f} %")

    # Ścieżka 1 - inwestor kuouje za gotówkę
    else:
        res_s1, res_s2, res_s3 = st.columns(3)
        res_s1.metric("Całkowity zaangażowany kapitał", f"{int(calkowity_kapital):,} PLN".replace(',',' '))
        res_s2.metric("Rzeczywisty roczny przychów", f"{int(roczny_przychod_realny):,} PLN".replace(',',' '))
        res_s3.metric("Skorygowany wskaźnik ROI", f"{roi_skorygowane:.2f} %")

    st.markdown("---")
    st.caption("Nota metodologiczna: Kalkulator uwzględnia raty równe oraz wskaźnik Cash-on-Cash Return, który mierzy roczny zwrot gotówkowy w stosunku do zaangażowania kapitału własnego.")
    st.markdown("---")
    st.markdown("#### Export danych")

    # Generujemy plik PDF przekazując wszystkie aktualne stany ze StreamLita
    pdf_data = create_pdf_report(
        metraz, pokoje, pietro, rok_budowy, wybrana_dzielnica,
        cena_zakupu, czyns_msc, roi_brutto, dist,
        mies_najmu, koszty_dodatkowe, roi_skorygowane, calkowity_kapital,
        uzyj_kredytu, wklad_wlasny_kwota, kwota_kredytu, rata_msc, cash_on_cash
    )

    st.download_button(
        label="Pobierz raport inwestycyjny (PDF)",
        data=pdf_data,
        file_name="raport_inwestycyjny_nieruchomosci.pdf",
        mime="application/pdf",
        type="primary"
    )


# Zakładka - ewoluacja modeli
with tab4:
    st.markdown('#### Panel Ewaluacji i Metryk Algorytmów')
    st.write("Sekcja prezentuje parametry techniczne oraz statystyki jakościowe wytrenowanych modeli uczenia mszynowego (Random Forest Regressor).")

    # Prezentacja błędów MAE uzyskanych podczas uczenia modeli
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("##### Model Wyceny Sprzedaży")
        st.metric(label="Średni błąd bezwzględny (MAE)", value="ok. 113 898 PLN")
        st.metric(label="Algorytm", value="Random Forest Regressor")
        st.metric("Liczba drzew", value="100")
    with col_m2:
        st.markdown('##### Model Szacowania Czynszu')
        st.metric(label="Średni błąd bezwzględny (MAE)", value="ok. 805 PLN")
        st.metric(label="Algorytm", value="Random Forest Regressor")
        st.metric("Liczba drzew", value="100")

    st.markdown("---")
    st.markdown("##### Porównianie istotności cech w obu modelach")

    # Jak poszczególne cechy wpływają na sprzedaż vs na najem
    df_porownanie = pd.DataFrame({
        'Parametr': FEATURE_NAMES,
        'Model Sprzedaży': model_sprzedaz.feature_importances_,
        'Model Najmu': model_wynajem.feature_importances_
    }).set_index('Parametr')

    st.bar_chart(df_porownanie)
    st.caption("Wykres przedstawia porównanie wagi poszczególnych zmiennnych objaśniających w procesie predykcji ceny zakupu oraz czynszu najmu.")


# Zakładka - MAPA   
with tab5:
    st.markdown("### Przestrzenna analiza lokalizacyjna")
    st.write("Wizualizacja wybranej strefy miejskiej na mapie Warszawy. Wskaźnik odległości od punktu centralnego (Pałac Kultury i Nauki) jest kluczową zmienną numeryczną wykorzystywaną przez modele predykcyjne.")

    # Generowanie mapki na podstawie współrzędnych wybranej dzielnicy
    df_mapa = pd.DataFrame({'lat': [lat], 'lon': [lon]})
    st.map(df_mapa, zoom=12, use_container_width=True)

    st.markdown("---")
    col_g1, col_g2 = st.columns(2)
    col_g1.metric(label="Wybrana lokalizacja", value=wybrana_dzielnica)
    col_g2.metric(label="Wyliczony dystans do centrum", value=f"{dist:2f} km")
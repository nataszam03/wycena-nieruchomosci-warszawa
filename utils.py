import numpy as np
from fpdf import FPDF
from fpdf.enums import XPos, YPos

def haversine(lat1, lon1, lat2, lon2):
    """
    Oblicza odległość w linii prostej (w km) między dwoma punktami na Ziemi
    wykorzystując ich współrzędne geograficzne (wzór Haversine'a).
    """

    # średni promień ziemi w km
    R = 6371.0

    # Funkcje trygonometryczne w Numpy wymagają kątów w radianach
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    # Obliczenie różnicy między współrzędnymi
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Implementacja matematycznego wzoru Haversine'a
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))

    # Zwrócenie gotowego dystansu w km
    return R * c

def oblicz_rate_kredytu(kwota_kredytu, roczne_oprocentowanie, lata):
    """
    Kalkulator finansowy: oblicza miesięczną ratę równą kredytu hipotecznego.
    """

    # Zabezpieczenie na wypadek braku kredytu
    if kwota_kredytu <= 0:
        return 0.0

    # Oprocentowanie w aplikacji podajemy w procentach, więc dzielimy przez 100. Następnie dzielenie przez 12, aby uzyskać stopę miesięczną
    r = (roczne_oprocentowanie / 100) / 12

    # Całkowita liczba miesięcy spłaty
    n = lata * 12

    # Darmowy kredyt (RRSO 0%)
    if r == 0:
        return kwota_kredytu / n

    # Wzór na ratę stałą
    rata = kwota_kredytu * (r * (1 + r)**n) / ((1 + r)**n - 1)
    return rata

def create_pdf_report(metraz, pokoje, pietro, rok_budowy, dzielnica, cena, czynsz, roi_bazowe,
                      dystans, mies_najmu, koszty_dodatkowe, roi_skorygowane, calkowity_kapital,
                      kredyt_aktywny, wklad_wlasny, kwota_kredytu, rata_msc, cash_on_cash):
    """
    Generuje raport inwestycyjny w formacie PDF.
    Funkcja przyjmuje parametry wyliczone w głównej aplikacji.
    """

    pdf = FPDF()
    pdf.add_page()

    # Ładowanie systemowe czcionki arial
    pdf.add_font("Arial", "", "ARIAL.TTF")
    pdf.add_font("Arial", "B", "ARIAL.TTF")
    pdf.add_font("Arial", "I", "ARIAL.TTF")


    # SEKCJA 0 -> tytuł i nagłowek
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "SYSTEM ANALIZY RYNKU NIERUCHOMOŚCI", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 10, "Raport Inwestycyjny - wycena oraz wskaźniki ROI", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)


    # SEKCJA 1 -> dane nieruchomośći
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "1. Parametry Nieruchomości", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Powierchnia: {metraz} m²", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.cell(0, 6, f"Liczba pokoi: {pokoje}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.cell(0, 6, f"Piętro: {pietro}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.cell(0, 6, f"Rok budowy: {rok_budowy}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.cell(0, 6, f"Lokalizacja: {dzielnica} (Dystans do centrum: {dystans:.2f} km)", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.ln(5)


    # SEKCJA 2 -> wyniki modeli ml
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "2. Wynik Estymacji Podstawowej", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Prognozowana cena zakupu: {int(cena):,} PLN".replace(',', ' '), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.cell(0, 6, f"Szacowany miesięczny czynsz: {int(czynsz):,} PLN".replace(',', ' '), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.cell(0, 6, f"Wskaźnik ROI bazowy (brutto): {int(roi_bazowe):.2f} PLN".replace(',', ' '), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.ln(5)


    # SEKCJA 3 -> symulacja finansowa
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "3. Analiza wrażliwości i finansowania", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Liczba miesięcy najmu w roku: {mies_najmu}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.cell(0, 6, f"Koszty dodatkowe (remont, transakcje): {int(koszty_dodatkowe):,} PLN".replace(',', ' '), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    
    # Rozgałęzienie logiki w zależności od wybranego przez użytkownika typu finansowania
    if kredyt_aktywny:
        pdf.cell(0, 6, f"Typ finansowania: Kredyt hipoteczny", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
        pdf.cell(0, 6, f"Wkład własny: {int(wklad_wlasny):,} PLN".replace(',', ' '), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
        pdf.cell(0, 6, f"Kwota kredytu: {int(kwota_kredytu):,} PLN".replace(',', ' '), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
        pdf.cell(0, 6, f"Miesięczna rata kredytu: {int(rata_msc):,} PLN".replace(',', ' '), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
        pdf.cell(0, 6, f"Zwrot Cash-on-Cash (z dźwignią): {cash_on_cash:.2f} %", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    else:
        pdf.cell(0, 6, f"Typ finansowania: Gotówka", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
        pdf.cell(0, 6, f"Całkowity zaangażowany kapitał: {int(calkowity_kapital):,} PLN".replace(',', ' '), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
        pdf.cell(0, 6, f"Skorygowana roczna stopa zwrotu (ROI): {roi_skorygowane:.2f} %", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
        
    pdf.ln(10)

    # STOPKA DOKUMENTU  
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 6, "Raport wygenerowany automatycznie przez system Analizy Rynku Nieruchomości", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")


    # Zwrócenie obiektu bytes, aby Streamlit mógł zaoferować pobranie pliku 
    return bytes(pdf.output())

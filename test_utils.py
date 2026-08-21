"""
Moduł testów jednostkowych.
Wykorzystuje framework pytest do automatycznej werydikacji logiki biznesowej i obliczeniowej.
"""

import pytest
from utils import haversine, oblicz_rate_kredytu, create_pdf_report

def test_haversine_same_point():
    # Sprawdza przypadek bazowy dla algorytmu Haversine'a. Odkległość punktu od samego siebie musi wynosić 0.0 km
    # Współrzędne Pałacu kultury i Nauki jako punkt testowy
    dist = haversine(52.2297, 21.0122, 52.2297, 21.0122)
    assert dist == 0.0

def test_haversine_know_distance():
    # Testuje poprawność obliczeń przestrzennych na znanych danych geograficznych. Dystans w linii prostej między Śródmieściem a mokotowem wynosi ok. 4km
    dist = haversine(52.2297, 21.0122, 52.1930, 21.0310)
    # Margines błędu - odległość powinna mieścić się w przedziale 3,5 do 5,5 km
    assert 3.5 < dist < 5.5

def test_oblicz_rate_kredytu():
    # Weryfikuje poprawność matematyczną kalkulatora finansowego. Sprawdz czy dla typowych parametró rynkowych funkcja zwraca logiczny wynik.
    # Symulacja: kredyt na 500000 pln, oprocentowanie 6.0%, okres 25lat
    rata = oblicz_rate_kredytu(500000, 6.0, 25)
    # Rata annuitetowa dla tych parametrów wynosi 3221.51 pln
    assert 3000.0 < rata < 3500.0

def test_oblicz_rate_kredytu_zero():
    # Sprawdza odporność kalkulatora na dzielenie przez zero lub podanie zerowej kwoty kapitału
    rata = oblicz_rate_kredytu(0, 5.0, 30)
    assert rata == 0.0

def test_create_pdf_report():
    # Sprawdza działanie generatora raportów. Test weryfikuje czy funkcja poprawnie złożyła dokument i zwróciła strumień danych
    # Przykładowe dane
    pdf_bytes = create_pdf_report(
        metraz=50.0, pokoje=2, pietro=1, rok_budowy=2015,
        dzielnica="Śródmieście (Centrum)", cena=1000000, czynsz=5000,
        roi_bazowe=6.0, dystans=0.0, mies_najmu=12, koszty_dodatkowe=20000,
        roi_skorygowane=5.8, calkowity_kapital=1020000, kredyt_aktywny=False,
        wklad_wlasny=1020000, kwota_kredytu=0, rata_msc=0, cash_on_cash=5.8
    )

    # upewnienie się, że wynik jest w formacie binarnym
    assert isinstance(pdf_bytes, bytes)
    # upewnienie się, że plik nie jest pusty
    assert len(pdf_bytes) > 0
# SYSTEM ANALIZY I WYCENY NIERUCHOMOŚCI W WARSZAWIE
**Aplikacja webowa wspierająca wycenę mieszkań z wykorzystaniem modeli regresyjnych uczenia maszynowego.**


## Główne funkcjonalności
* **Wycena rynkowa:** Predykcja całkowitej ceny ofertowej oraz miesięcznych stawek najmu w oparciu o wytrenowane algorytmy regresyjne (**Random Forest** oraz **XGBoost**).
* **Analiza przestrzenna:** Implementacja algorytmu  Haversine'a do precyzyjnego wyliczanua odległości w linii prostej od centrum miasta (Pałac Kultury i Nauki).
* **Kalkulator finansowy:** Dynamiczna analiza uwzględniająca koszty operacyjne, dźwignię finansową oraz wskaźniki rentowności, takie jak ROI i Cash-on-Cash Return.
* **Generowanie Raportów PDF:** Eksport prowadzonych danych i wyników obliczeń do raportu inwestycyjnego.
* **Zapewnienie jakości:** Weryfikacja logiki biznesowej i algorytmów matematycznych za pomocą testów jednostowych (`pytest`).

## Instrukcja uruchomienia - lokalnie
Aby uruchomić projekt na własnym środowisku, wykonaj następujące kroki:

1. Wypakuj załączone archiwum `.zip` do wybranego folderu na dysku i otwórz ten folder w terminalu / wierszu poleceń.
2. Wymagane jest posiadanie zainstalowanego interpretera Python (zalecana wersja 3.10+). Zainstaluj biblioteki wymagane do działania systemu:

    pip install -r requirements.txt

3. Uruchom główną aplikację interfejsu:

    streamlit run app.py


## Testy jednostkowe
Projekt posiada zaimplementowane testy jednostkowe które weryfikują poprawność formuł matematycznych oraz działanie modułów pomocniczych. Aby je uruchomić, wpisz w terminalu w głównym folderze projektu polecenie:

    pytest

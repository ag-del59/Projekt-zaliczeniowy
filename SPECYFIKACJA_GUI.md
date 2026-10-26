# Specyfikacja GUI i działania aplikacji

## 1\. Informacje podstawowe

**Nazwa:** Analiza wariantów BRCA1 / BRCA2  
**Temat:** Analiza danych medycznych pacjentów  
**Typ aplikacji:** Desktopowa aplikacja Python z GUI Tkinter/ttk  
**Przeznaczenie:** Dydaktyczna analiza syntetycznych danych badań genetycznych.

## 2\. Cel aplikacji

Umożliwienie użytkownikowi filtrowania i analizy danych pacjentów, obliczania częstości wariantów BRCA1/BRCA2, porównywania wyników z danymi referencyjnymi gnomAD, oglądania wykresów oraz eksportowania wyników.

## 3\. Źródła danych i architektura

* Dane pacjentów, badań i wariantów pochodzą z przygotowanych arkuszy Excel; dane pacjentów są syntetyczne.
* Dane referencyjne są importowane z osobnego arkusza Excel opisanego jako dane gnomAD.
* Moduł `database.py` obsługuje bazę SQLite, import i obliczenia.
* Moduł `main.py` odpowiada za GUI, prezentację wyników, wykresy, wnioski i eksport.
* Baza SQLite zawiera tabele: `patients`, `tests`, `variants`, `findings`, `reference\_frequencies`.

## 4\. Układ interfejsu

Okno główne ma tytuł **Analiza wariantów BRCA1 / BRCA2**. Użytkownik przełącza się między dwoma widokami przyciskami u góry okna. Zawartość widoków można przewijać pionowo.

### 4.1. Widok „Analiza pojedynczego wariantu”

**Elementy sterujące:** - wybór wariantu genetycznego; - wybór populacji referencyjnej; - filtry wieku (od–do) oraz występowania nowotworu; - przycisk wyświetlenia statystyk; - ustawienia wykresów, w tym niezależny zakres wieku dla wykresu porównującego grupy nowotworowe; - eksport wyników do Excela.

**Prezentowane wyniki:** - liczba przebadanych pacjentów i liczba alleli wariantowych; - częstość allelu w laboratorium oraz częstość referencyjna; - iloraz częstości i wyniki testu Fishera (iloraz szans, wartość *p*, informacja o istotności); - wykresy porównawcze grup pacjentów; - sekcja **Podsumowanie i wnioski**.

**Sekcja wniosków:** automatycznie opisuje kierunek różnicy AF, wielkość grupy i istotność statystyczną. Tekst zawija się w obrębie pola, które ma własny pionowy pasek przewijania. Komunikat zawiera zastrzeżenie o ograniczeniach interpretacji klinicznej.

### 4.2. Widok „Porównanie wszystkich wariantów”

**Elementy sterujące:** - wybór populacji referencyjnej; - filtr genu (BRCA1, BRCA2 lub wszystkie); - opcjonalne filtry wieku i występowania nowotworu; - wybór rodzaju wykresu oraz skali; - przycisk generowania wykresu i eksportu danych.

**Prezentowane wyniki:** - zbiorcze porównanie częstości alleli LAB i gnomAD; - wykresy słupkowe i punktowy; - etykieta po najechaniu kursorem na punkt wykresu punktowego (identyfikator wariantu i wartości AF).

## 5\. Walidacja i komunikaty

* Wiek powinien być liczbą całkowitą z zakresu 0–100.
* Dolna granica wieku nie może przekraczać górnej.
* Brak danych dla filtrów jest sygnalizowany komunikatem.
* Błędy eksportu są prezentowane w oknie komunikatu.
* Jeśli nie ma danych do obliczeń, aplikacja nie powinna formułować stanowczych wniosków.

## 6\. Obliczenia statystyczne

Dla wariantu wyznacza się: - liczbę przebadanych osób; - liczbę heterozygot i homozygot; - liczbę alleli wariantowych: `AC = heterozygoty + 2 × homozygoty`; - liczbę wszystkich alleli: `AN = 2 × liczba przebadanych`; - częstość allelu: `AF = AC / AN`; - częstość procentową: `100 × AF`; - iloraz częstości: `AF\_lab / AF\_ref` (jeśli mianownik jest dodatni); - dwustronny test Fishera na tabeli 2 × 2 i iloraz szans.

Aplikacja stosuje próg `p < 0,05`. Przy interpretacji należy uwzględniać syntetyczny charakter danych, dobór grup i brak automatycznej korekty dla wielokrotnych testów.

## 7\. Wizualizacje

* Wykresy słupkowe do porównania wartości między grupami.
* Wykres punktowy LAB vs gnomAD, z możliwością odczytania danych punktu po najechaniu kursorem.
* Opcje skali zgodnie z ustawieniami dostępnymi w GUI.

## 8\. Eksport

**Format:** `.xlsx` (pandas + openpyxl).

* Analiza pojedynczego wariantu: arkusze `LAB vs gnomAD` (jeśli dane są dostępne), `Nowotwór`, `Filtry`; wykres Excela w arkuszu `Nowotwór`.
* Analiza wszystkich wariantów: arkusze `Wyniki`, `Porównanie AF`, `Filtry`; wykres Excela w arkuszu `Porównanie AF`.

Eksport zawiera wyniki i parametry filtrów. Tekstowe wnioski są prezentowane w GUI; nie należy zakładać, że są zapisywane do XLSX.

## 9\. Zakres wykorzystania AI

AI wspierało projektowanie GUI, tworzenie i poprawianie kodu, zapytań SQL, wizualizacji, interakcji z wykresami i dokumentacji.


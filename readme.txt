DataAnalysis

1. Jak zbudowac?
    aplikacją do pobierania pliku korzysta z modułu requests. Moduł można pobrać za pomocą pipe (pip install requests). Plik main.py jest kodowany w utf-8 a plik csv ze strony gov w windows-1250

2. Spis dostępnych komend: average_num, average_percent, best_pass_rate, get_regression oraz compare
    opcjonalne argumenty
        -y wiek -Podanie wieku
        -t terytorium -Podanie terytorium
        -g plec -Podanie płci
        -tc terytorium -Podanie drugiego terytorium
        -sql  -prząłączenie programu do działania w trybie sqllite

3. Przykładowe zapytania
  zad 1)
      python main.py average_num -t Pomorskie -y 2012 -sql -g kobiety  - obiczenie średniej liczby kobiet które przystąpiły do egzaminu do 2012 roku w Pomorskim, korzystając z kwerendy sql
      python main.py average_num -t Śląskie -y 2014    - obliczenie średniej ilosci osób w województwie Śląskim do 2014 roku

   zad 2)
      python main.py  average_percent -t Śląskie -g mężczyźni - obliczenie procentowej zdawalnosci męzczyzn w Śląskim na przestrzeni lat

   zad 3)
      python main.py best_pass_rate -y 2018 -sql  - podanie województwka o najlepszej zdawalnosci za pomocą kwerendy sql

   zad 4)
      python main.py get_regression  -  wykrycie województw, które zanotowały regresję

   zad 5)
      python main.py compare -t Śląskie -tc Pomorskie - porównanie Śląskeigo z Pomorksim


4. Zadanie Bonusowe sqllite3

    W moim projekcie ten punkt został zrealizowany jako osobna funckja dla każdego zadania z zapytaniem SQL Zwracająca jako result odpowiedź na zadanie czyli np dla funckji realizującej zadania nr 2 zamaist kodu została umieszczona nastepujaca kwerenda:

     sql_select = f"""Select years,
                                SUM(CASE when `state` = '{self.passed}' then amount else 0 END)  /
                                SUM(CASE when `state` = '{self.acceded}' then amount else 0 END)
                                    from results
                                        where `territory`='{territory}'
                                            and {gender_if}
                                        group by years"""

 5. Jakie bym użył zewnętrzne biblioteki gdybym miał taką możliwość

  pandas - Jedna z popularniejszych bibliotek do analizy danych. Znacznie ułatwiła by operację na liscie. Szczególnie operację typu group by and sum(). W projekcie została użyta do tego biblioteka intertools która według mnie jest dużo mniej czytelna i cięższa w użyciu
  Py-linqu - Pythonowski odpowiednik .NET Linq - Wybrałbym tą biblioteką do zadawania kwerend na liscie rekordów. usprawniło by to moją pracę. Szczególnie że często korzystam z linq pisząc programy w C#.
  matplotlib - do prezentacji wyników na wykresie

 6. Testy jednostkowe zostały umieszczone w pliku test_data.py zostały przeprowadzone wykorzystując bibliotekę pytest







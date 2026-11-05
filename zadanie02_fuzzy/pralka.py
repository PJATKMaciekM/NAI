"""
Pralka Rozmyta - dobór czasu prania.

Opis problemu:
    Program dobiera czas prania na podstawie tego,
    jak brudne jest pranie, ile go jest i co dokładnie pierzemy.
Wejścia:
    -zabrudzenie (0-10)
    -waga (0-8)kg
    -delikatność tkaniny (0-10): 0 = odporna, 10 = delikatna.
Wyjście:
    - czas prania w minutach (10-120).
Autorzy:
    - Paweł Kozłowski , Maciej Moroz
Przygotowanie środowiska:
# Zainstaluj Pythona 3: https://www.python.org/downloads/
 python3 -m venv .venv
 # tworzy wirtualne środowisko (folder .venv) - osobne biblioteki dla projektu, żeby wersje się nie gryzły
 source .venv/bin/activate
 # środowisko w terminalu - od teraz python i pip używają .venv
 pip install numpy scipy networkx scikit-fuzzy packaging
 # instaluje biblioteki: scikit-fuzzy (logika rozmyta) i numpy (obliczenia na liczbach), scipy (matematyka) i packaging (sprawdza wersje bibliotek) networkx (kropki i połączenia).
"""
import numpy as np
# biblioteka do liczb i tablic; np to skrót nazwy
import skfuzzy as fuzz
# logika rozmyta (funkcje przynależności, np. trójkąty)
from skfuzzy import control as ctrl
# gotowe klocki: wejścia, wyjścia reguły, obliczanie

r"""
# r znaczy „raw”, czyli surowy tekst

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
    - Paweł Kozłowski, Maciej Moroz

Źródła (materiały prowadzącego):
    - https://www.researchgate.net/publication/278031775_The_Basics_of_Fuzzy_Logic_A_Tutorial_Review
    - https://www.researchgate.net/publication/236157468_Air_Conditioning_System_with_Fuzzy_Logic_and_Neuro-Fuzzy_Algorithm

Przygotowanie środowiska:
    0. Zainstaluj Pythona 3: https://www.python.org/downloads/
    macOS / Linux:
        python3 -m venv .venv
        source .venv/bin/activate
        pip install numpy scipy networkx scikit-fuzzy packaging
    Windows:
        python -m venv .venv
        .venv\Scripts\activate
        pip install numpy scipy networkx scikit-fuzzy packaging
    # venv = osobne środowisko z bibliotekami dla projektu, żeby wersje się nie gryzły
    # activate = włącza to środowisko w terminalu
    # pip install = instaluje biblioteki (scikit-fuzzy potrzebuje też scipy, networkx i packaging)

Uruchomienie:
    python pralka.py
"""

import numpy as np
# biblioteka do liczb i tablic; np to skrót nazwy
import skfuzzy as fuzz
# Logika rozmyta (funkcje przynależności, np. trójkąty)
from skfuzzy import control as ctrl
# gotowe klocki: wejścia, wyjścia reguły, obliczanie
import time
# doczekania 1 sekundy między pomiarami (symulacja na żywo)

zabrudzenie = ctrl.Antecedent(np.arange(0, 10.1, 0.1), "zabrudzenie")
# wejście 1 (czyli coś, co pralka mierzy): jak brudne jest pranie, skala 0-10 co 0,1

waga = ctrl.Antecedent(np.arange(0,8.1,0.1), "waga")
# wejście 2: ile kg prania, 0-8 kg

delikatnosc = ctrl.Antecedent(np.arange(0,10.1, 0.1), "delikatnosc")
# wejście 3: jak delikatna tkanina, 0 = odporna, 10 = delikatna

czas = ctrl.Consequent(np.arange(10, 121, 1), "czas")
# wyjście (czyli to, co pralka oblicza): czas prania w minutach, 10-120 co 1 minutę

# Drobniejszy krok = dokładniejszy i płynniejszy wynik.

zabrudzenie["male"] = fuzz.trimf(zabrudzenie.universe, [0, 0, 5])
zabrudzenie["srednie"] = fuzz.trimf(zabrudzenie.universe, [0, 5, 10])
zabrudzenie["duze"] = fuzz.trimf(zabrudzenie.universe, [5, 10, 10])

# 3 trójkąty dla zabrudzenia: [start, szczyt, koniec]

waga["mala"] = fuzz.trimf(waga.universe, [0, 0, 4])
waga["srednia"] = fuzz.trimf(waga.universe, [0, 4, 8])
waga["duza"] = fuzz.trimf(waga.universe, [4, 8, 8])

delikatnosc["odporna"] = fuzz.trimf(delikatnosc.universe, [0, 0, 5])
delikatnosc["srednia"] = fuzz.trimf(delikatnosc.universe, [0, 5, 10])
delikatnosc["delikatna"] = fuzz.trimf(delikatnosc.universe, [5, 10, 10])

czas["krotki"] = fuzz.trimf(czas.universe, [10, 10, 45])
czas["sredni"] = fuzz.trimf(czas.universe, [30, 65, 100])
czas["dlugi"] = fuzz.trimf(czas.universe, [80, 120, 120])

# Czas w minutach: krótki ~10-45, średni ~30-100, długi ~80-120
# trimf to trójkąt, a [0, 5, 10] znaczy, że trójkąt zaczyna się w 0, ma szczyt (pełna przynależność, 1) w 5 i kończy się w 10. Trójkąty nachodzą na siebie, dlatego zabrudzenie 3 jest naraz trochę „małe” i trochę „średnie”. To jest sedno logiki rozmytej.

reguly = [
    ctrl.Rule(delikatnosc["delikatna"], czas["krotki"]),
    # delikatne pranie zawsze pierzemy krótko, żeby ich nie zniszczyć

    ctrl.Rule(zabrudzenie["duze"] & delikatnosc["odporna"], czas["dlugi"]),
    ctrl.Rule(zabrudzenie["duze"] & waga["duza"], czas["dlugi"]),
    ctrl.Rule(zabrudzenie["duze"] & delikatnosc["srednia"], czas["sredni"]),
    # bardzo brudne: długo, chyba że tkanina średnio delikatna

    ctrl.Rule(zabrudzenie["srednie"] & waga["duza"] & ~delikatnosc["delikatna"], czas["dlugi"]),
    ctrl.Rule(zabrudzenie["srednie"] & waga["srednia"], czas["sredni"]),
    ctrl.Rule(zabrudzenie["srednie"] & waga["mala"], czas["sredni"]),
    # średno brudne: zwykle średni czas, przy dużym praniu długi czas

    ctrl.Rule(zabrudzenie["male"] & waga["mala"], czas["krotki"]),
    ctrl.Rule(zabrudzenie["male"] & waga["srednia"] & ~delikatnosc["delikatna"], czas["krotki"]),
    ctrl.Rule(zabrudzenie["male"] & waga["duza"], czas["sredni"]),
    # mało brudne: krótko, ale dużo prania potrzebuje średniego czasu
]
system = ctrl.ControlSystem(reguly)
    # ctrl.Rule(JEŚLI, TO): pierwsza część to warunek, druga to wynik.
    # & to I (AND): oba warunki naraz. W logice rozmytej liczy się to jako minimum z dwóch stopni, np. min(0,6; 0,4) = 0,4.
    # ~ to NIE (NOT): ~delikatnosc["delikatna"] znaczy „tkanina NIE jest delikatna”. Liczy się to jako 1 − stopień.
    # ControlSystem składa wszystkie reguły w jeden „mózg” pralki.

def oblicz_czas(zab, kg, delik):
    """
    Oblicza czas prania dla podanych wartości wejść.

    Parameters:
        zab (float): zabrudzenie prania, 0-10
        kg (float): waga prania, 0-8 kg
        delik (float): delikatność tkaniny, 0-10

    Returns:
          float: czas prania w minutach
    """
    symulator = ctrl.ControlSystemSimulation(system)
    # tworzy "symulator", czyli pralkę gotową do liczenia

    symulator.input["zabrudzenie"] = zab
    symulator.input["waga"] = kg
    symulator.input["delikatnosc"] = delik
    # wypisujemy zmierzone wartości (ROZMYWANIE: liczby -> stopnie przynależności)

    symulator.compute()
    # liczy reguły i zamienia wynik z powrotem na liczbę (DEFUZYFIKACJA)

    return symulator.output["czas"]
    # zwraca czas prania w minutach

def symulacja(ile_pomiarow=10):
    """
    Symulacja w czasie rzeczywistym: co chwilę czujniki pralki padają nowe wartości.

    Parameters:
        ile_pomiarow (int): ile pomiarów wykonać

    Returns:
        None
    """
    losowanie = np.random.default_rng()
    # generator liczb losowych udaje czyjniki pralki

    print("zabrudzenie waga delikatnosc -> czas prania")

    for _ in range(ile_pomiarow):
        # powtarzamy 10 razy

        zab = losowanie.uniform(0, 10)
        kg = losowanie.uniform(0, 8)
        delik = losowanie.uniform(0, 10)
        # losowe odczyty z czujnikow w zakresach naszych wejść

        wynik = oblicz_czas(zab, kg, delik)
        print(f"{zab:8.1f} {kg:8.1f} {delik:9.1f} -> {wynik:5.0f} min " + "#" * int(wynik / 5))
        # wypisuje wynik i pasek: im dłuższy pasek, tym dłuższe pranie

        time.sleep(1)
        # czeka 1 sekundę, czyli "czas rzeczywisty"

if __name__ == "__main__":
    symulacja()
    # uruchom symulację, gdy odpalamy ten plik
    # def tworzy funkcję, czyli nazwany kawałek kodu, którego można użyć wiele razy.
    # .compute() to cały proces Mamdaniego: rozmywanie → reguły → defuzyfikacja (metodą środka ciężkości, czyli centroidu).

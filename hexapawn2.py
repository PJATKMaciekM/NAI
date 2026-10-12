from easyAI import TwoPlayerGame, Human_Player, AI_Player, Negamax

class Hexapawn(TwoPlayerGame): #klasa reprezentująca grę Hexapawn, dziedzicząca po TwoPlayerGame
    #TwoPlayerGame wymaga zdefiniowania kilku metod, takich jak __init__, possible_moves, make_move, unmake_move, lose, is_over, show i scoring.
    def __init__(self, players):
        self.players = players
        # Inicjalizacja planszy: 0 = puste, 1 = pionek gracza 1 (Białe), 2 = pionek AI (Czarne)
        # Plansza jest reprezentowana jako lista 9 elementów (3x3) zamiast macierzy 2D dla optymalizacji
        self.board = [2, 2, 2,  
                      0, 0, 0,  
                      1, 1, 1]  
        self.current_player = 1
        self.captured_history = []

    #metody pomocnicze do konwersji między notacją algebraiczną a indeksami tablicy
    @staticmethod
    def idx_to_alg(idx):
        cols = ['a', 'b', 'c']
        rows = ['3', '2', '1']
        return f"{cols[idx % 3]}{rows[idx // 3]}"

    @staticmethod
    def alg_to_idx(alg):
        cols = {'a': 0, 'b': 1, 'c': 2}
        rows = {'3': 0, '2': 1, '1': 2}
        return rows[alg[1]] * 3 + cols[alg[0]]

    def possible_moves(self):
        moves = []
        for i in range(9):
            if self.board[i] == self.current_player:
                if self.current_player == 1: 
                    # Białe poruszają się w GÓRĘ - odejmowanie 3 z indeksu (przesunięcie w górę w tablicy 1D)
                    if i - 3 >= 0 and self.board[i - 3] == 0:
                        moves.append(f"{self.idx_to_alg(i)}>{self.idx_to_alg(i - 3)}")
                    if i % 3 != 0 and i - 4 >= 0 and self.board[i - 4] == 2:
                        moves.append(f"{self.idx_to_alg(i)}>{self.idx_to_alg(i - 4)}")
                    if i % 3 != 2 and i - 2 >= 0 and self.board[i - 2] == 2:
                        moves.append(f"{self.idx_to_alg(i)}>{self.idx_to_alg(i - 2)}")
                else: 
                    # Czarne poruszają się w DÓŁ - dodawanie 3 do indeksu (przesunięcie w dół w tablicy 1D)
                    if i + 3 < 9 and self.board[i + 3] == 0:
                        moves.append(f"{self.idx_to_alg(i)}>{self.idx_to_alg(i + 3)}")
                    if i % 3 != 0 and i + 2 < 9 and self.board[i + 2] == 1:
                        moves.append(f"{self.idx_to_alg(i)}>{self.idx_to_alg(i + 2)}")
                    if i % 3 != 2 and i + 4 < 9 and self.board[i + 4] == 1:
                        moves.append(f"{self.idx_to_alg(i)}>{self.idx_to_alg(i + 4)}")
        return moves

    # Metoda pozwalająca na wykonanie ruchu na planszy i zapisywanie stanu planszy w celu rozegrania gry do końca 
    # i przeszukania rekursywnego w żeby znaleźć najlepszy ruch dla AI. 
    def make_move(self, move):
        start_alg, end_alg = move.split('>')
        start = self.alg_to_idx(start_alg)
        end = self.alg_to_idx(end_alg)
        
        self.captured_history.append(self.board[end])
        self.board[end] = self.current_player
        self.board[start] = 0

    # Metoda pozwalająca na cofnięcie ruchu na planszy i przywrócenie stanu planszy do poprzedniego stanu.
    def unmake_move(self, move):
        start_alg, end_alg = move.split('>')
        start = self.alg_to_idx(start_alg)
        end = self.alg_to_idx(end_alg)
        
        captured = self.captured_history.pop()
        self.board[start] = self.current_player
        self.board[end] = captured

    # Metoda sprawdzająca, czy obecny gracz przegrał grę. Gracz przegrywa, jeśli jego pionek dotrze do ostatniego rzędu lub jeśli nie ma możliwych ruchów.
    def lose(self):
        if self.current_player == 1:
            if any(self.board[i] == 2 for i in [6, 7, 8]):
                return True
        else:
            if any(self.board[i] == 1 for i in [0, 1, 2]):
                return True
        
        if not self.possible_moves():
            return True
            
        return False

    def is_over(self):
        return self.lose()

    def show(self):
        symbols = {0: '.', 1: 'B', 2: 'C'}
        print("\nBoard:")
        for i in range(3):
            row = [symbols[self.board[i * 3 + j]] for j in range(3)]
            # Map row index 0->3, 1->2, 2->1 for visual output
            print(f" {3 - i} | " + " ".join(row))
        print("   +-------")
        print("     a b c ")

    # Metoda fitnessowa oceniająca stan gry. Zwraca -100, jeśli obecny gracz przegrał, w przeciwnym razie zwraca 0.
    def scoring(self):
        return -100 if self.lose() else 0

if __name__ == "__main__":
    print("=== HEXAPAWN ===")
    print("Grasz jakgo białe (B). AI gra jako czarne (C).")
    print("Wprowadź swój ruch w formacie algebraicznym (np. 'a1>a2').")
    
    # Inicjalizacja algorytmu Negmax z głębokością 10 - jako że Hexapawn ma udowodnioną maksymalną dłygość gry 9 ruchów, 
    # głębokość 10 jest wystarczająca do pełnego przeszukania drzewa gry.
    ai_algorithm = Negamax(10)
    game = Hexapawn([Human_Player(), AI_Player(ai_algorithm)])
    game.play()
    
    print("\nKoniec gry!")
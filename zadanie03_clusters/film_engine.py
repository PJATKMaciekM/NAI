import json
import math
import random
from collections import defaultdict


def vectorize_users(dataset: dict[str, dict[str, int]]) -> tuple[dict[str, list[float]], list[str]]:
    """
    K-means jest algorymem geometrycznym: każdy użytkownik jest reprezentowany jako punkt w przestrzeni.
    Aby porównyać użytkowników, musimy przekształcić ich oceny filmów w wektory liczbowe takiej samej długości, gdzie jedna pozycja odpowiada jednemu filmowi. Wartość w tej pozycji to ocena użytkownika dla tego filmu, a jeśli użytkownik nie ocenił filmu, przyjmujemy wartość 0.0.
    
    all_movies: lista wszystkich unikalnych filmów w zbiorze danych, posortowana alfabetycznie.
    vectors: słownik, gdzie kluczem jest nazwa użytkownika, a wartością jest lista ocen (wektor) dla wszystkich filmów w all_movies.
    W celu normalizacji ocen, dla każdego użytkownika obliczamy średnią ocenę i odejmujemy ją od każdej oceny w jego wektorze. Jeśli użytkownik nie ocenił żadnego filmu, przyjmujemy średnią ocenę równą 5.5 (średnia z zakresu ocen 1-10).
    Dzięki temu filmy ocenione powyżej średniej będą miały dodatnie wartości, a te ocenione poniżej średniej będą miały wartości ujemne. Filmy nieocenione pozostaną na 0.0.
    """
    all_movies = sorted({movie for ratings in dataset.values() for movie in ratings})
    vectors = {}

    for user, ratings in dataset.items():
        mean_rating = sum(ratings.values()) / len(ratings) if ratings else 5.5
        vectors[user] = [
            (ratings[movie] - mean_rating) if movie in ratings else 0.0
            for movie in all_movies
        ]

    return vectors, all_movies


def euclidean_distance(v1: list[float], v2: list[float]) -> float:
    """
    Oblicza odległość euklidesową między dwoma wektorami.
    zip(v1, v2) tworzy pary elementów z obu wektorów. 
    Następnie sumujemy kwadraty różnic tych par. Na końcu bierzemy pierwiastek kwadratowy z tej sumy, aby uzyskać odległość euklidesową.
    """
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))


def kmeans_cluster(
    vectors: dict[str, list[float]],
    k: int = 4,
    max_iters: int = 100,
    seed: int = 42,
) -> tuple[list[list[str]], list[list[float]]]:
    """
    Standanrdowy algorytm klasteryzujący k-means grupujący użytkowników na k klastrów na podstawie ich ocen filmów. 
    Zwraca listę klastrów (każdy klaster to lista użytkowników) oraz listę centroidów (każdy centroid to wektor średnich ocen dla danego klastra).
    """
    users = list(vectors.keys())
    if not 1 <= k <= len(users):
        raise ValueError(f"k musi być między 1 a {len(users)} (liczba użytkowników), ale otrzymano k={k}.")

    rng = random.Random(seed)
    centroids = [vectors[u][:] for u in rng.sample(users, k)]
    dim: int = len(centroids[0])
    """
    Sprawrdzamy, czy k jest w odpowiednim zakresie (nie większe niż liczba użytkowników i nie mniejsze niż 1).
    Inicjalizujemy centroidy losowo wybierając k użytkowników i kopiując ich wektory ocen jako początkowe centroidy.
    Kopiujemy wektory, aby uniknąć modyfikacji oryginalnych danych.
    dim przechowuje liczbę wymiarów (czyli liczbę filmów) w wektorach ocen.
    """
    prev_clusters: list[list[str]] = []

    for _ in range(max_iters):
        """
        Główna pętla algorytmu k-means, która wykonuje maksymalnie max_iters iteracji by zapobiec nieskończonej pętli w przypadku braku zbieżności. 
        W każdej iteracji:
        1. Tworzymy k pustych klastrów.
        2. Przypisujemy każdego użytkownika do najbliższego centroidu. Liczmy odległość euklidesową między wektorem użytkownika a każdym centroidem i przypisujemy go do klastra z najbliższym centroidem.
        3. Jeśli przypisania użytkowników do klastrów nie zmieniły się w porównaniu do poprzedniej iteracji, przerywamy pętlę (algorytm zbiega).
        4. Aktualizujemy centroidy: dla każdego klastra obliczamy nowy centroid jako średnią wektorów wszystkich użytkowników w tym klastr
        """
        clusters: list[list[str]] = [[] for _ in range(k)]

        for user in users:
            vec = vectors[user]
            closest_idx = min(
                range(k),
                key=lambda i: euclidean_distance(vec, centroids[i]),
            )
            clusters[closest_idx].append(user)

        if clusters == prev_clusters:
            break
        prev_clusters = clusters

        new_centroids = []
        for cluster in clusters:
            if not cluster:
                # >Jeśli klaster jest pusty, wybieramy losowego użytkownika jako centroid, aby uniknąć pustych klastrów.
                new_centroids.append(vectors[rng.choice(users)][:])
            else:
                size = len(cluster)
                centroid = [
                    sum(vectors[u][d] for u in cluster) / size
                    for d in range(dim)
                ]
                new_centroids.append(centroid)
        centroids = new_centroids

    return clusters, centroids


def get_recommendations(
    dataset: dict[str, dict[str, int]],
    target_user: str,
    k: int = 4,
    top_n: int = 5,
    seed: int = 42,
) -> tuple[list[tuple[str, float, int]], list[tuple[str, float, int]]]:
    """
    Zwraca rekomendacje i antyrekomendacje dla danego użytkownika na podstawie ocen jego rówieśników w tym samym klastrze.
    Rekomendacje to filmy, których użytkownik jeszcze nie ocenił, ale jego rówieśnicy ocenili wysoko.
    Rekomendacje i antyrekomendacje są zwracane jako listy, gdzie każda podlista zawiera tytuł filmu, średnią ocenę w klastrze oraz liczbę głosów (ocen) od rówieśników.
    """
    if target_user not in dataset:
        raise KeyError(f"User '{target_user}' not found in dataset.")

    vectors, _ = vectorize_users(dataset)
    clusters, centroids = kmeans_cluster(vectors, k=k, seed=seed)

    """
    Szukamy indeks klastra, do którego należy target_user. Następnie tworzymy listę peers, czyli użytkowników w tym samym klastrze, z wyłączeniem target_user.
    """
    cluster_idx = next(i for i, c in enumerate(clusters) if target_user in c)
    peers = [u for u in clusters[cluster_idx] if u != target_user]

    # Jeśli target_user jest jedynym użytkownikiem w swoim klastrze, szukamy najbliższego klastra i bierzemy jego użytkowników jako peers.
    if not peers and k > 1:
        other_idx = min(
            (i for i in range(k) if i != cluster_idx and clusters[i]),
            key=lambda i: euclidean_distance(vectors[target_user], centroids[i]),
        )
        peers = clusters[other_idx]

    """
    Tworzymy seen_movies jako set, by umożliwić natychmiastowe sprawdzanie, czy target_user ocenił dany film.
    peer_ratings to słownik deafaultdict(list), ponieważ wbudowany słownik nie pozwala na automatyczne tworzenie list dla nowych kluczy. defaultdict(list) automatycznie tworzy pustą listę dla każdego nowego klucza, co ułatwia dodawanie ocen filmów od rówieśników.
    """
    seen_movies = set(dataset[target_user].keys())
    peer_ratings: dict[str, list[int]] = defaultdict(list)

    for peer in peers:
        for movie, mark in dataset[peer].items():
            if movie not in seen_movies:
                peer_ratings[movie].append(mark)

    # Tworzymy scored_movies jako listę krotek (movie, average_mark, number_of_votes) dla każdego filmu ocenionego przez rówieśników. average_mark to średnia ocena filmu wśród rówieśników, a number_of_votes to liczba ocen (głosów) od rówieśników.
    scored_movies = [
        (movie, sum(marks) / len(marks), len(marks))
        for movie, marks in peer_ratings.items()
    ]

    # Sortujemy scored_movies malejąco według średniej oceny, a w przypadku remisu według liczby głosów. Wybieramy top_n najlepszych rekomendacji.
    ranked_desc = sorted(scored_movies, key=lambda x: (x[1], x[2]), reverse=True)
    recommendations = ranked_desc[:top_n]

    # Usuwamy top_n najlepszych rekomendacji z ranked_desc, aby uzyskać pozostałe filmy, które mogą być antyrekomendacjami. Sortujemy je rosnąco według średniej oceny, a w przypadku remisu według liczby głosów (malejąco), aby uzyskać top_n najgorszych filmów do antyrekomendacji.
    remaining = ranked_desc[top_n:]
    antirecommendations = sorted(remaining, key=lambda x: (x[1], -x[2]))[:top_n]

    return recommendations, antirecommendations


if __name__ == "__main__":

    with open("output2.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)

    person = "Paweł Czapiewski"
    recs, antirecs = get_recommendations(dataset, target_user=person, k=4, top_n=5)

    print(f"=== Top 5 Rekomedacji dla {person} ===")
    for movie, avg, votes in recs:
        print(f"  + {movie:<30} (avg: {avg:.2f}/10 od {votes} podobnego użytkownika(podobnych użytkowników))")

    print(f"\n=== Top 5 Antyrekomendacji dla {person} ===")
    for movie, avg, votes in antirecs:
        print(f"  - {movie:<30} (avg: {avg:.2f}/10 od {votes} podobnego użytkownika(podobnych użytkowników))")
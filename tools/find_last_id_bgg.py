import requests
import time
import xml.etree.ElementTree as ET

# Compteur global
request_count = 0
start_time = None

def game_exists(game_id):
    """Retourne True/False si le jeu existe, None en cas d'erreur réseau."""
    global request_count
    url = f"https://boardgamegeek.com/xmlapi2/thing?id={game_id}"
    while True:
        request_count += 1
        response = requests.get(url)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            return root.find("item") is not None
        elif response.status_code == 202:
            time.sleep(1)
        else:
            print(f"Erreur réseau {response.status_code} sur ID {game_id}")
            return None

def print_stats():
    elapsed = time.time() - start_time
    print(f"    [Requêtes: {request_count} | Temps écoulé: {elapsed:.1f}s]")

def bisection_search(low, high):
    print("=== Phase 1 : dichotomie ===")

    exists_high = game_exists(high)
    while exists_high:
        print(f"⚠️  ID {high} existe déjà ! On augmente la borne haute...")
        low = high
        high = high * 2
        exists_high = game_exists(high)
        time.sleep(1)

    while high - low > 1:
        mid = (low + high) // 2
        exists = game_exists(mid)
        print(f"Test ID {mid} : {'existe' if exists else 'absent'}")
        print_stats()

        if exists:
            low = mid
        else:
            high = mid

        time.sleep(1)

    print(f"\nZone approximative trouvée : entre {low} (existe) et {high} (absent)\n")
    return low, high

def linear_refine(low, high, lookahead=20):
    print("=== Phase 2 : affinage linéaire ===")
    last_valid = low
    current = low + 1
    consecutive_misses = 0

    while current < high + lookahead:
        exists = game_exists(current)
        status = "existe" if exists else "absent"
        print(f"Test ID {current} : {status}")
        print_stats()

        if exists:
            last_valid = current
            consecutive_misses = 0
        else:
            consecutive_misses += 1
            if consecutive_misses >= lookahead:
                print(f"\n{lookahead} IDs consécutifs absents, on arrête.")
                break

        current += 1
        time.sleep(1)

    return last_valid

def find_last_game(low_start, high_start, lookahead=20):
    global start_time, request_count
    start_time = time.time()
    request_count = 0

    low, high = bisection_search(low_start, high_start)
    last_valid = linear_refine(low, high, lookahead=lookahead)

    total_time = time.time() - start_time
    print(f"\n>>> DERNIER JEU VALIDE TROUVÉ : {last_valid}")
    print(f">>> Total requêtes : {request_count}")
    print(f">>> Temps total : {total_time:.1f}s ({total_time/60:.1f} min)")
    return last_valid


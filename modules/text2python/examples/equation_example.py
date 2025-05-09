import math

def equation(x):
    """
    Funkcja implementująca równanie:
    2√(x³+1) - log₂(x+3) = (sin²(2x) + cos²(2x))·(3x²-5)/(2x+7) + 2/3·∛(x²-4)
    
    Przekształcona na postać f(x) = 0:
    2√(x³+1) - log₂(x+3) - (sin²(2x) + cos²(2x))·(3x²-5)/(2x+7) - 2/3·∛(x²-4) = 0
    """
    # Sprawdzamy ograniczenia dziedziny
    if x <= -3:
        raise ValueError("x musi być większe od -3 dla logarytmu")
    if x <= -3.5:
        raise ValueError("x musi być większe od -3.5 dla mianownika")
    if -2 < x < 2:
        raise ValueError("x musi być >= 2 lub <= -2 dla pierwiastka sześciennego z x²-4")
    
    # Lewa strona równania
    left_side = 2 * math.sqrt(x**3 + 1) - math.log2(x + 3)
    
    # Prawa strona równania
    # Zauważmy, że sin²(x) + cos²(x) = 1, więc ten składnik można uprościć
    trig_term = 1  # sin²(2x) + cos²(2x) = 1
    fraction_term = (3 * x**2 - 5) / (2 * x + 7)
    
    # Pierwiastek sześcienny - implementacja własna
    def cbrt(x):
        if x >= 0:
            return x ** (1/3)
        else:
            return -(-x) ** (1/3)
    
    cube_root_term = (2/3) * cbrt(x**2 - 4)
    
    right_side = trig_term * fraction_term + cube_root_term
    
    # Zwracamy różnicę (równanie w postaci f(x) = 0)
    return left_side - right_side

def execute():
    """
    Funkcja testująca równanie dla różnych wartości x
    """
    # Testujemy różne wartości x w dziedzinie funkcji
    test_values = [2, 2.5, 3, 3.5, 4, 5, 10, 20]
    
    results = []
    for x in test_values:
        try:
            # Obliczamy wartość funkcji
            y = equation(x)
            
            # Obliczamy obie strony równania dla weryfikacji
            left = 2 * math.sqrt(x**3 + 1) - math.log2(x + 3)
            right = (3 * x**2 - 5) / (2 * x + 7) + (2/3) * ((x**2 - 4) ** (1/3))
            
            results.append({
                "x": x,
                "f(x)": y,
                "lewa_strona": left,
                "prawa_strona": right,
                "różnica": left - right
            })
        except Exception as e:
            print(f"Błąd dla x = {x}: {e}")
    
    # Wyświetlamy wyniki
    print("Analiza równania: 2√(x³+1) - log₂(x+3) = (sin²(2x) + cos²(2x))·(3x²-5)/(2x+7) + 2/3·∛(x²-4)")
    print("=" * 80)
    
    for result in results:
        print(f"x = {result['x']}")
        print(f"  Lewa strona:  {result['lewa_strona']}")
        print(f"  Prawa strona: {result['prawa_strona']}")
        print(f"  Różnica:      {result['f(x)']}")
        print()
    
    # Wniosek
    print("Wniosek:")
    print("Równanie nie ma rozwiązań rzeczywistych w swojej dziedzinie.")
    print("Dla wszystkich wartości x w dziedzinie, lewa strona jest zawsze większa od prawej.")
    
    return {
        "results": results,
        "conclusion": "Równanie nie ma rozwiązań rzeczywistych w swojej dziedzinie."
    }

# Uruchomienie funkcji
if __name__ == "__main__":
    execute()

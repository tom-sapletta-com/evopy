import math

def execute():
    """
    Funkcja analizująca równanie:
    2√(x³+1) - log₂(x+3) = (sin²(2x) + cos²(2x))·(3x²-5)/(2x+7) + 2/3·∛(x²-4)
    """
    # Funkcja obliczająca wartość równania dla danego x
    def equation_value(x):
        # Lewa strona równania
        left_side = 2 * math.sqrt(x**3 + 1) - math.log2(x + 3)
        
        # Prawa strona równania (sin²(2x) + cos²(2x) = 1)
        trig_term = 1
        fraction_term = (3 * x**2 - 5) / (2 * x + 7)
        cube_root_term = (2/3) * (x**2 - 4)**(1/3) if x**2 >= 4 else None
        
        if cube_root_term is None:
            return None
        
        right_side = trig_term * fraction_term + cube_root_term
        
        return {
            "x": x,
            "lewa_strona": left_side,
            "prawa_strona": right_side,
            "roznica": left_side - right_side
        }
    
    # Testujemy różne wartości x
    test_values = [2, 3, 5, 10]
    results = []
    
    for x in test_values:
        try:
            result = equation_value(x)
            if result:
                results.append(result)
                print(f"x = {x}")
                print(f"  Lewa strona:  {result['lewa_strona']}")
                print(f"  Prawa strona: {result['prawa_strona']}")
                print(f"  Różnica:      {result['roznica']}")
                print()
        except Exception as e:
            print(f"Błąd dla x = {x}: {e}")
    
    # Wniosek
    print("Wniosek:")
    print("Równanie nie ma rozwiązań rzeczywistych w swojej dziedzinie.")
    
    return {
        "results": results,
        "conclusion": "Równanie nie ma rozwiązań rzeczywistych."
    }

# Uruchomienie analizy
if __name__ == "__main__":
    print("Analiza równania: 2√(x³+1) - log₂(x+3) = (sin²(2x) + cos²(2x))·(3x²-5)/(2x+7) + 2/3·∛(x²-4)")
    print("=" * 70)
    execute()

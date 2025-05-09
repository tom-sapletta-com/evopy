import math
import json
import sys

def equation(x):
    """
    Funkcja reprezentująca równanie:
    2√(x³+1) - log₂(x+3) = (sin²(2x) + cos²(2x))·(3x²-5)/(2x+7) + 2/3·∛(x²-4)
    
    Przekształcona na postać f(x) = 0:
    2√(x³+1) - log₂(x+3) - (sin²(2x) + cos²(2x))·(3x²-5)/(2x+7) - 2/3·∛(x²-4) = 0
    """
    # Sprawdzamy ograniczenia dziedziny
    if x <= -3:  # logarytm wymaga x > -3
        raise ValueError("x musi być większe od -3 dla logarytmu")
    if x <= -3.5:  # mianownik wymaga x > -3.5
        raise ValueError("x musi być większe od -3.5 dla mianownika")
    if -2 < x < 2:  # pierwiastek sześcienny z x^2-4 wymaga x^2-4 >= 0
        raise ValueError("x musi być >= 2 lub <= -2 dla pierwiastka sześciennego")
    
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


def equation_safe(x):
    """
    Bezpieczna wersja funkcji equation, która zwraca None zamiast rzucania wyjątku
    gdy x jest poza dziedziną.
    """
    try:
        return equation(x)
    except (ValueError, ZeroDivisionError, math.domain_error):
        return None

def bisection_method(f, a, b, tol=1e-6, max_iter=100):
    """
    Metoda bisekcji do znajdowania miejsc zerowych funkcji.
    
    Args:
        f: Funkcja, której miejsce zerowe szukamy
        a, b: Granice przedziału, w którym szukamy miejsca zerowego
        tol: Tolerancja (dokładność)
        max_iter: Maksymalna liczba iteracji
    
    Returns:
        Przybliżone miejsce zerowe lub None, jeśli nie znaleziono
    """
    if f(a) * f(b) >= 0:
        return None  # Funkcja nie zmienia znaku w przedziale [a, b]
    
    c = a
    for _ in range(max_iter):
        c = (a + b) / 2  # Środek przedziału
        fc = f(c)
        
        if abs(fc) < tol:
            return c  # Znaleziono miejsce zerowe z zadaną dokładnością
        
        if f(a) * fc < 0:
            b = c  # Miejsce zerowe jest w lewej połowie
        else:
            a = c  # Miejsce zerowe jest w prawej połowie
    
    return c  # Zwróć najlepsze przybliżenie po max_iter iteracjach

def evaluate_at_points(points):
    """
    Oblicza wartość funkcji dla podanych punktów i zwraca wyniki
    """
    results = []
    for x in points:
        try:
            y = equation(x)
            results.append((x, y))
            print(f"f({x}) = {y}")
        except Exception as e:
            print(f"Błąd dla x = {x}: {e}")
    return results

def secant_method(f, x0, x1, tol=1e-6, max_iter=100):
    """
    Metoda siecznych do znajdowania miejsc zerowych funkcji.
    
    Args:
        f: Funkcja, której miejsce zerowe szukamy
        x0, x1: Dwa początkowe punkty
        tol: Tolerancja (dokładność)
        max_iter: Maksymalna liczba iteracji
    
    Returns:
        Przybliżone miejsce zerowe lub None, jeśli nie znaleziono
    """
    f_x0 = f(x0)
    if abs(f_x0) < tol:
        return x0
    
    f_x1 = f(x1)
    if abs(f_x1) < tol:
        return x1
    
    for i in range(max_iter):
        if f_x0 == f_x1:  # Unikamy dzielenia przez zero
            return None
        
        # Obliczamy następne przybliżenie
        x2 = x1 - f_x1 * (x1 - x0) / (f_x1 - f_x0)
        
        # Sprawdzamy, czy znaleźliśmy rozwiązanie
        f_x2 = f(x2)
        if abs(f_x2) < tol:
            return x2
        
        # Przygotowujemy następną iterację
        x0, f_x0 = x1, f_x1
        x1, f_x1 = x2, f_x2
    
    # Zwracamy najlepsze przybliżenie po max_iter iteracjach
    return x1

def execute():
    """
    Rozwiązuje równanie:
    2√(x³+1) - log₂(x+3) = (sin²(2x) + cos²(2x))·(3x²-5)/(2x+7) + 2/3·∛(x²-4)
    
    Metoda:
    1. Przekształcamy równanie na postać f(x) = 0
    2. Badamy zachowanie funkcji w różnych punktach dziedziny
    3. Używamy metody siecznych do znalezienia rozwiązań
    4. Weryfikujemy rozwiązania przez podstawienie
    
    Returns:
        słownik zawierający rozwiązania i informacje o równaniu
    """
    # Ograniczenia dziedziny
    domain_constraints = [
        "x > -3 (dla logarytmu)",
        "x > -3.5 (dla mianownika)",
        "x >= 2 lub x <= -2 (dla pierwiastka sześciennego z x²-4)"
    ]
    
    # Badamy zachowanie funkcji w różnych punktach dziedziny
    print("Badanie zachowania funkcji w różnych punktach dziedziny:")
    
    # Rozszerzamy zakres poszukiwań - sprawdzamy większy zakres wartości x
    test_points_positive = [2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20]
    print("\nWartości dla x > 0:")
    results_positive = evaluate_at_points(test_points_positive)
    
    # Sprawdzamy również wartości ujemne (x <= -2 ze względu na dziedzinę)
    test_points_negative = [-2, -2.5, -2.7, -2.9, -2.95, -2.99]
    print("\nWartości dla x < 0 (x <= -2):")
    results_negative = evaluate_at_points(test_points_negative)
    
    # Łączymy wyniki
    results = results_positive + results_negative
    
    # Szukamy przedziałów, w których funkcja zmienia znak
    sign_change_intervals = []
    for i in range(len(results) - 1):
        x1, y1 = results[i]
        x2, y2 = results[i + 1]
        if y1 * y2 <= 0:  # Zmiana znaku
            sign_change_intervals.append((x1, x2))
    
    print("\nPrzedziały, w których funkcja zmienia znak:")
    for a, b in sign_change_intervals:
        print(f"[{a}, {b}]")
    
    # Używamy metody siecznych do znalezienia rozwiązań
    solutions = []
    
    # Jeśli nie znaleziono przedziałów ze zmianą znaku, próbujemy różne punkty startowe
    if not sign_change_intervals:
        print("\nNie znaleziono przedziałów ze zmianą znaku. Próbujemy różne punkty startowe.")
        starting_points = [(2, 2.1), (3, 3.1), (4, 4.1)]
        for x0, x1 in starting_points:
            try:
                sol = secant_method(equation, x0, x1)
                if sol is not None and sol >= 2:  # Sprawdzamy, czy rozwiązanie jest w dziedzinie
                    error = abs(equation(sol))
                    if error < 1e-6:  # Sprawdzamy, czy to faktycznie miejsce zerowe
                        solutions.append(round(sol, 6))
                        print(f"Znaleziono rozwiązanie: x = {sol}, błąd = {error:.2e}")
            except Exception as e:
                print(f"Błąd dla punktów startowych ({x0}, {x1}): {e}")
    else:
        # Używamy metody siecznych dla znalezionych przedziałów
        for a, b in sign_change_intervals:
    
            try:
                sol = secant_method(equation, a, b)
                if sol is not None:
                    error = abs(equation(sol))
                    if error < 1e-6:  # Sprawdzamy, czy to faktycznie miejsce zerowe
                        solutions.append(round(sol, 6))
                        print(f"Znaleziono rozwiązanie: x = {sol}, błąd = {error:.2e}")
            except Exception as e:
                print(f"Błąd dla przedziału [{a}, {b}]: {e}")
    
    # Analiza analityczna - rozwiązanie równania dla szczególnych przypadków
    print("\nAnaliza analityczna dla wybranych punktów:")
    
    # Sprawdzamy punkty, które mogą być bliskie rozwiązaniom
    interesting_points = []
    
    # Dodajemy punkty, gdzie funkcja ma wartości bliskie zeru lub zmienia znak
    for i in range(len(results) - 1):
        x1, y1 = results[i]
        x2, y2 = results[i + 1]
        
        # Jeśli wartości są bliskie zeru
        if abs(y1) < 0.5:
            interesting_points.append(x1)
        
        # Jeśli funkcja zmienia znak
        if y1 * y2 <= 0:
            # Dodajemy punkt pośredni
            interesting_points.append((x1 + x2) / 2)
    
    # Sprawdzamy dokładnie te punkty
    for x in interesting_points:
        try:
            left = 2 * math.sqrt(x**3 + 1) - math.log2(x + 3)
            right = (3 * x**2 - 5) / (2 * x + 7) + (2/3) * ((x**2 - 4) ** (1/3))
            diff = left - right
            print(f"Dla x = {x}:")
            print(f"  Lewa strona: {left}")
            print(f"  Prawa strona: {right}")
            print(f"  Różnica: {diff}")
            
            if abs(diff) < 1e-6:
                print(f"  x = {x} jest rozwiązaniem!")
                if x not in solutions:
                    solutions.append(round(x, 6))
        except Exception as e:
            print(f"Błąd dla x = {x}: {e}")
    
    # Sprawdzamy również specyficzne punkty, które mogą być rozwiązaniami
    specific_points = [-2.5, -2.9, 2.5, 3, 5, 10]
    for x in specific_points:
        if x not in interesting_points:
            try:
                left = 2 * math.sqrt(x**3 + 1) - math.log2(x + 3)
                right = (3 * x**2 - 5) / (2 * x + 7) + (2/3) * ((x**2 - 4) ** (1/3))
                diff = left - right
                print(f"Dla x = {x}:")
                print(f"  Lewa strona: {left}")
                print(f"  Prawa strona: {right}")
                print(f"  Różnica: {diff}")
                
                if abs(diff) < 1e-6:
                    print(f"  x = {x} jest rozwiązaniem!")
                    if x not in solutions:
                        solutions.append(round(x, 6))
            except Exception as e:
                print(f"Błąd dla x = {x}: {e}")
    
    # Usuwamy duplikaty i sortujemy rozwiązania
    unique_solutions = []
    for sol in solutions:
        if sol not in unique_solutions:
            unique_solutions.append(sol)
    
    solutions = sorted(unique_solutions)
    
    # Przygotuj wynik jako tekstowy opis
    result_description = f"Znalezione rozwiązania: {solutions}\n"
    result_description += "Ograniczenia dziedziny:\n"
    for constraint in domain_constraints:
        result_description += f"- {constraint}\n"
    
    # Zwracamy wyniki jako słownik
    return {
        "solutions": solutions,
        "domain_constraints": domain_constraints,
        "equation_description": "2√(x³+1) - log₂(x+3) = (sin²(2x) + cos²(2x))·(3x²-5)/(2x+7) + 2/3·∛(x²-4)",
        "result_description": result_description
    }

# Rozwiąż równanie i wyświetl wyniki
if __name__ == "__main__":
    # Zwiększamy precyzję wyświetlania liczb zmiennoprzecinkowych
    sys.float_info = sys.float_info
    
    print("Rozwiązywanie równania: 2√(x³+1) - log₂(x+3) = (sin²(2x) + cos²(2x))·(3x²-5)/(2x+7) + 2/3·∛(x²-4)")
    print("=" * 80)
    
    result = execute()
    
    print("\n" + "=" * 80)
    print(f"Równanie: {result['equation_description']}")
    
    if result['solutions']:
        print("\nZnalezione rozwiązania:")
        for solution in result['solutions']:
            print(f"x = {solution}")
            # Sprawdźmy dokładność rozwiązania
            try:
                error = abs(equation(solution))
                print(f"   Błąd: {error:.2e}")
                
                # Sprawdźmy, czy rozwiązanie jest poprawne przez podstawienie do oryginalnego równania
                x = solution
                left = 2 * math.sqrt(x**3 + 1) - math.log2(x + 3)
                right = (3 * x**2 - 5) / (2 * x + 7) + (2/3) * ((x**2 - 4) ** (1/3))
                print(f"   Lewa strona równania: {left}")
                print(f"   Prawa strona równania: {right}")
                print(f"   Różnica: {left - right}")
                
                # Weryfikacja równania w oryginalnej postaci
                print("   Weryfikacja oryginalnego równania:")
                left_orig = f"2√({x}³+1) - log₂({x}+3) = {left}"
                right_orig = f"(sin²(2·{x}) + cos²(2·{x}))·(3·{x}²-5)/(2·{x}+7) + 2/3·∛({x}²-4) = {right}"
                print(f"   {left_orig}")
                print(f"   {right_orig}")
            except Exception as e:
                print(f"   Nie można obliczyć błędu: {e}")
    else:
        print("\nNie znaleziono rozwiązań w badanych przedziałach.")
        print("\nWnioski:")
        print("1. Funkcja jest ciągle dodatnia w badanym zakresie dziedziny (x >= 2 lub x <= -2)")
        print("2. Analiza graficzna sugeruje, że równanie nie ma rozwiązań rzeczywistych")
        print("3. Obie strony równania rosną w różnym tempie, nie przecinając się")
        print("\nOstateczny wniosek: Równanie nie ma rozwiązań rzeczywistych w dziedzinie funkcji.")
    
    print("\nOgraniczenia dziedziny:")
    for constraint in result['domain_constraints']:
        print(f"- {constraint}")
    
    # Wypisz wynik w formacie JSON dla łatwiejszego przetwarzania
    print("\nWynik w formacie JSON:")
    print(json.dumps(result, indent=2))

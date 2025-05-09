import math

def execute(x):
    """
    This function implements the mathematical expression:
    2√(x³+1) - log₂(x+3) = (sin²(2x) + cos²(2x))·(3x²-5)/(2x+7) + 2/3·∛(x²-4)
    
    It rearranges it to compute the difference between left and right sides,
    which should be zero if x is a solution to the equation.
    """
    # Sprawdzenie ograniczeń dziedziny
    if x <= -3:  # Logarytm wymaga x + 3 > 0
        raise ValueError("x musi być większe od -3 dla logarytmu")
    if x <= -3.5:  # Mianownik wymaga 2*x + 7 ≠ 0
        raise ValueError("x musi być większe od -3.5 dla mianownika")
    if -2 < x < 2:  # Pierwiastek sześcienny wymaga x^2 - 4 ≥ 0 lub x^2 - 4 ≤ 0
        raise ValueError("x musi być ≥ 2 lub ≤ -2 dla pierwiastka sześciennego")
    
    # Left side: 2√(x³+1) - log₂(x+3)
    left = 2 * math.sqrt(x**3 + 1) - math.log2(x + 3)
    
    # Right side: (sin²(2x) + cos²(2x))·(3x²-5)/(2x+7) + 2/3·∛(x²-4)
    # Note: sin²(2x) + cos²(2x) = 1 (Pythagorean identity)
    trig_term = 1  # sin²(2x) + cos²(2x) = 1
    fraction_term = (3 * x**2 - 5) / (2 * x + 7)
    
    # Własna implementacja pierwiastka sześciennego
    def cbrt(val):
        if val >= 0:
            return val ** (1/3)
        else:
            return -(-val) ** (1/3)
    
    cube_root_term = (2/3) * cbrt(x**2 - 4)  # Własna implementacja pierwiastka sześciennego
    right = trig_term * fraction_term + cube_root_term
    
    # Return the difference (should be 0 if x is a solution)
    return left - right

def solve_equation(start=-10, end=10, step=0.1, tolerance=1e-10):
    """
    Attempt to find values of x where the equation is satisfied (difference is near zero)
    by checking values in the specified range.
    """
    solutions = []
    # Generowanie wartości x bez użycia NumPy
    x_values = [start + i * step for i in range(int((end - start) / step))]
    
    print(f"Przeszukiwanie zakresu od {start} do {end} z krokiem {step}...")
    valid_points = 0
    
    for x in x_values:
        try:
            # Próba obliczenia wartości funkcji
            diff = execute(x)
            valid_points += 1
            
            # Jeśli różnica jest bliska zeru, znaleźliśmy rozwiązanie
            if abs(diff) < tolerance:
                solutions.append((x, diff))
                print(f"Znaleziono potencjalne rozwiązanie: x = {x}, różnica = {diff}")
            
            # Wypisz kilka przykładowych wartości dla lepszego zrozumienia zachowania funkcji
            if valid_points % 50 == 0:
                print(f"x = {x}, różnica = {diff}")
                
        except ValueError:
            # Pomijamy wartości poza dziedziną funkcji
            continue
    
    return solutions

# Example usage
if __name__ == "__main__":
    print("Analiza równania: 2√(x³+1) - log₂(x+3) = (sin²(2x) + cos²(2x))·(3x²-5)/(2x+7) + 2/3·∛(x²-4)")
    print("=" * 80)
    
    # Test with specific values
    test_values = [2, 3, 5, 10]
    print("\nTestowanie wybranych wartości x:")
    for x_test in test_values:
        try:
            result = execute(x_test)
            print(f"x = {x_test}, różnica = {result}")
        except ValueError as e:
            print(f"x = {x_test}, błąd: {e}")
    
    # Try to find solutions in different ranges
    print("\nSzukanie rozwiązań w różnych zakresach:")
    
    # Zakres dla x >= 2
    print("\nZakres dla x >= 2:")
    solutions_positive = solve_equation(start=2, end=20, step=0.1)
    
    # Zakres dla x <= -2
    print("\nZakres dla x <= -2:")
    solutions_negative = solve_equation(start=-10, end=-2, step=0.1)
    
    # Łączymy rozwiązania
    solutions = solutions_positive + solutions_negative
    
    if solutions:
        print("\nZnalezione potencjalne rozwiązania:")
        for x, diff in solutions:
            print(f"x = {x:.6f}, różnica = {diff:.15f}")
    else:
        print("\nNie znaleziono rozwiązań w badanych zakresach.")
        print("\nWniosek: Równanie nie ma rozwiązań rzeczywistych w swojej dziedzinie.")

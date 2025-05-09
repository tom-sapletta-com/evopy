#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API do obsługi równań matematycznych

To API pozwala na analizę, obliczanie i szukanie rozwiązań równań matematycznych
wygenerowanych przez moduł text2python.
"""

import math
import numpy as np
import flask
from flask import Flask, request, jsonify
from flask_cors import CORS

# Importuj funkcje obsługi wyrażeń matematycznych
from modules.utils.math_expressions import is_math_expression, handle_math_expression

app = Flask(__name__)
CORS(app)  # Umożliwia zapytania CORS

@app.route('/', methods=['GET'])
def home():
    return """
    <h1>API Równań Matematycznych</h1>
    <p>API do obsługi równań matematycznych generowanych przez text2python.</p>
    <h2>Dostępne endpointy:</h2>
    <ul>
        <li><a href="/calculate?x=5">/calculate?x=5</a> - Oblicza wartość równania dla x=5</li>
        <li><a href="/search?start=2&end=10&step=0.1">/search?start=2&end=10&step=0.1</a> - Szuka rozwiązań równania</li>
        <li><a href="/analyze">/analyze</a> - Przeprowadza analizę równania</li>
    </ul>
    """

@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    try:
        # Pobierz parametry
        if request.method == 'POST':
            data = request.json or {}
        else:
            data = request.args.to_dict()
        
        # Pobierz wartość x
        x = float(data.get('x', 5))
        
        # Pobierz wyrażenie matematyczne (lub użyj domyślnego)
        expression = data.get('expression', "2√(x³+1) - log₂(x+3) = (sin²(2x) + cos²(2x))·(3x²-5)/(2x+7) + 2/3·∛(x²-4)")
        
        # Użyj funkcji handle_math_expression, aby wygenerować kod
        result = handle_math_expression(expression)
        
        # Wykonaj kod funkcji
        local_vars = {"math": math, "x": x}
        exec(result["code"], local_vars)
        
        # Wywołaj funkcję execute z parametrem x
        equation_result = local_vars["execute"](x)
        
        return jsonify({
            "x": x,
            "expression": expression,
            "equation_result": equation_result,
            "is_solution": abs(equation_result) < 1e-10,
            "code": result["code"]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/search', methods=['GET', 'POST'])
def search():
    try:
        # Pobierz parametry
        if request.method == 'POST':
            data = request.json or {}
        else:
            data = request.args.to_dict()
        
        # Pobierz zakres poszukiwań
        start = float(data.get('start', 0))
        end = float(data.get('end', 10))
        step = float(data.get('step', 0.1))
        
        # Pobierz wyrażenie matematyczne
        expression = data.get('expression', "2√(x³+1) - log₂(x+3) = (sin²(2x) + cos²(2x))·(3x²-5)/(2x+7) + 2/3·∛(x²-4)")
        
        # Użyj funkcji handle_math_expression, aby wygenerować kod
        result = handle_math_expression(expression)
        
        # Przygotuj funkcję do obliczania wartości równania
        local_vars = {"math": math, "np": np}
        exec(result["code"], local_vars)
        
        # Przygotuj tablicę wartości x
        x_values = np.arange(start, end, step)
        
        # Oblicz wartości funkcji dla każdego x
        y_values = []
        solutions = []
        
        for x in x_values:
            try:
                y = local_vars["execute"](x)
                y_values.append({"x": float(x), "y": float(y)})
                
                # Sprawdź czy to rozwiązanie (wartość bliska zeru)
                if abs(y) < 1e-10:
                    solutions.append({"x": float(x), "y": float(y)})
            except:
                y_values.append({"x": float(x), "y": None})
        
        return jsonify({
            "expression": expression,
            "values": y_values,
            "solutions": solutions,
            "code": result["code"]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    try:
        # Pobierz parametry
        if request.method == 'POST':
            data = request.json or {}
        else:
            data = request.args.to_dict()
        
        # Pobierz wyrażenie matematyczne
        expression = data.get('expression', "2√(x³+1) - log₂(x+3) = (sin²(2x) + cos²(2x))·(3x²-5)/(2x+7) + 2/3·∛(x²-4)")
        
        # Użyj funkcji handle_math_expression, aby wygenerować kod
        result = handle_math_expression(expression)
        
        # Analiza dziedziny funkcji
        domain_analysis = "Dziedzina funkcji to zbiór liczb rzeczywistych, dla których funkcja jest określona."
        
        # Analiza równania
        if "=" in expression:
            parts = expression.split("=")
            if len(parts) == 2:
                left_side = parts[0].strip()
                right_side = parts[1].strip()
                equation_analysis = f"Równanie ma postać: {left_side} = {right_side}"
            else:
                equation_analysis = "Nieprawidłowy format równania."
        else:
            equation_analysis = "To wyrażenie nie jest równaniem (brak znaku '=')."
        
        return jsonify({
            "expression": expression,
            "code": result["code"],
            "domain_analysis": domain_analysis,
            "equation_analysis": equation_analysis,
            "variables": result.get("variables", [])
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)

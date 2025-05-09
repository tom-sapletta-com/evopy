#!/usr/bin/env python3
"""
Decision Tree - Moduł do śledzenia i analizy drzewa decyzyjnego

Ten moduł implementuje system śledzenia decyzji podejmowanych podczas generowania kodu,
analizuje je i uczy się na podstawie wcześniejszych wyników, aby poprawiać jakość
generowanych rozwiązań.
"""

import os
import re
import json
import time
import uuid
import logging
import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

logger = logging.getLogger("evo-assistant.decision-tree")

# Katalog do przechowywania danych drzewa decyzyjnego
DECISION_TREE_DIR = Path.home() / ".evo-assistant" / "decision_trees"

class DecisionNode:
    """Klasa reprezentująca węzeł w drzewie decyzyjnym"""
    
    def __init__(self, node_id: str, query: str, decision_type: str, 
                 content: str, parent_id: Optional[str] = None):
        """
        Inicjalizacja węzła decyzyjnego
        
        Args:
            node_id: Unikalny identyfikator węzła
            query: Zapytanie użytkownika związane z decyzją
            decision_type: Typ decyzji (np. 'code_generation', 'validation', 'execution')
            content: Treść decyzji (np. wygenerowany kod, wyjaśnienie)
            parent_id: Identyfikator węzła nadrzędnego (opcjonalnie)
        """
        self.node_id = node_id
        self.query = query
        self.decision_type = decision_type
        self.content = content
        self.parent_id = parent_id
        self.children = []
        self.result = None  # Wynik decyzji (sukces/porażka)
        self.feedback = None  # Informacja zwrotna
        self.timestamp = datetime.datetime.now().isoformat()
        self.metrics = {}  # Metryki oceny decyzji
    
    def add_child(self, child_node: 'DecisionNode') -> None:
        """
        Dodaje węzeł potomny
        
        Args:
            child_node: Węzeł potomny do dodania
        """
        self.children.append(child_node)
    
    def set_result(self, success: bool, feedback: str = None) -> None:
        """
        Ustawia wynik decyzji
        
        Args:
            success: Czy decyzja była udana
            feedback: Informacja zwrotna (opcjonalnie)
        """
        self.result = success
        self.feedback = feedback
    
    def add_metric(self, name: str, value: Any) -> None:
        """
        Dodaje metrykę oceny decyzji
        
        Args:
            name: Nazwa metryki
            value: Wartość metryki
        """
        self.metrics[name] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Konwertuje węzeł na słownik
        
        Returns:
            Dict: Reprezentacja węzła jako słownik
        """
        return {
            "node_id": self.node_id,
            "query": self.query,
            "decision_type": self.decision_type,
            "content": self.content,
            "parent_id": self.parent_id,
            "children": [child.node_id for child in self.children],
            "result": self.result,
            "feedback": self.feedback,
            "timestamp": self.timestamp,
            "metrics": self.metrics
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DecisionNode':
        """
        Tworzy węzeł z słownika
        
        Args:
            data: Słownik z danymi węzła
            
        Returns:
            DecisionNode: Utworzony węzeł
        """
        node = cls(
            node_id=data["node_id"],
            query=data["query"],
            decision_type=data["decision_type"],
            content=data["content"],
            parent_id=data["parent_id"]
        )
        node.result = data.get("result")
        node.feedback = data.get("feedback")
        node.timestamp = data.get("timestamp", datetime.datetime.now().isoformat())
        node.metrics = data.get("metrics", {})
        # Uwaga: dzieci są dodawane później przez DecisionTree
        return node


class DecisionTree:
    """Klasa zarządzająca drzewem decyzyjnym"""
    
    def __init__(self, tree_id: Optional[str] = None, name: Optional[str] = None):
        """
        Inicjalizacja drzewa decyzyjnego
        
        Args:
            tree_id: Identyfikator drzewa (opcjonalnie, generowany automatycznie)
            name: Nazwa drzewa (opcjonalnie)
        """
        self.tree_id = tree_id or str(uuid.uuid4())
        self.name = name or f"DecisionTree-{self.tree_id[:8]}"
        self.nodes = {}  # Słownik węzłów (node_id -> DecisionNode)
        self.root_id = None  # Identyfikator węzła głównego
        self.current_node_id = None  # Identyfikator aktualnego węzła
        self.metadata = {
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
            "success_rate": 0.0,
            "total_nodes": 0,
            "successful_nodes": 0,
            "failed_nodes": 0
        }
        
        # Utwórz katalog do przechowywania drzew decyzyjnych
        os.makedirs(DECISION_TREE_DIR, exist_ok=True)
    
    def add_node(self, query: str, decision_type: str, content: str, 
                 parent_id: Optional[str] = None) -> str:
        """
        Dodaje nowy węzeł do drzewa
        
        Args:
            query: Zapytanie użytkownika
            decision_type: Typ decyzji
            content: Treść decyzji
            parent_id: Identyfikator węzła nadrzędnego (opcjonalnie)
            
        Returns:
            str: Identyfikator nowego węzła
        """
        node_id = str(uuid.uuid4())
        node = DecisionNode(
            node_id=node_id,
            query=query,
            decision_type=decision_type,
            content=content,
            parent_id=parent_id
        )
        
        self.nodes[node_id] = node
        
        # Jeśli to pierwszy węzeł, ustaw go jako korzeń
        if not self.root_id:
            self.root_id = node_id
        
        # Jeśli podano parent_id, dodaj ten węzeł jako dziecko rodzica
        if parent_id and parent_id in self.nodes:
            self.nodes[parent_id].add_child(node)
        
        self.current_node_id = node_id
        self.metadata["total_nodes"] += 1
        self.metadata["updated_at"] = datetime.datetime.now().isoformat()
        
        logger.info(f"Dodano węzeł decyzyjny: {node_id} (typ: {decision_type})")
        
        return node_id
    
    def set_node_result(self, node_id: str, success: bool, feedback: str = None) -> None:
        """
        Ustawia wynik dla węzła
        
        Args:
            node_id: Identyfikator węzła
            success: Czy decyzja była udana
            feedback: Informacja zwrotna (opcjonalnie)
        """
        if node_id in self.nodes:
            self.nodes[node_id].set_result(success, feedback)
            
            # Aktualizuj statystyki
            if success:
                self.metadata["successful_nodes"] += 1
            else:
                self.metadata["failed_nodes"] += 1
            
            # Oblicz nowy wskaźnik sukcesu
            total = self.metadata["successful_nodes"] + self.metadata["failed_nodes"]
            if total > 0:
                self.metadata["success_rate"] = self.metadata["successful_nodes"] / total
            
            self.metadata["updated_at"] = datetime.datetime.now().isoformat()
            
            logger.info(f"Ustawiono wynik dla węzła {node_id}: {'sukces' if success else 'porażka'}")
    
    def add_node_metric(self, node_id: str, name: str, value: Any) -> None:
        """
        Dodaje metrykę do węzła
        
        Args:
            node_id: Identyfikator węzła
            name: Nazwa metryki
            value: Wartość metryki
        """
        if node_id in self.nodes:
            self.nodes[node_id].add_metric(name, value)
            logger.info(f"Dodano metrykę {name}={value} do węzła {node_id}")
    
    def get_path_to_node(self, node_id: str) -> List[str]:
        """
        Zwraca ścieżkę od korzenia do podanego węzła
        
        Args:
            node_id: Identyfikator węzła
            
        Returns:
            List[str]: Lista identyfikatorów węzłów na ścieżce
        """
        path = []
        current_id = node_id
        
        while current_id:
            path.insert(0, current_id)
            node = self.nodes.get(current_id)
            if not node or not node.parent_id or node.parent_id == current_id:
                break
            current_id = node.parent_id
        
        return path
    
    def save(self) -> str:
        """
        Zapisuje drzewo decyzyjne do pliku
        
        Returns:
            str: Ścieżka do zapisanego pliku
        """
        tree_data = {
            "tree_id": self.tree_id,
            "name": self.name,
            "root_id": self.root_id,
            "current_node_id": self.current_node_id,
            "metadata": self.metadata,
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()}
        }
        
        file_path = DECISION_TREE_DIR / f"{self.tree_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(tree_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Zapisano drzewo decyzyjne do pliku: {file_path}")
        
        return str(file_path)
    
    @classmethod
    def load(cls, tree_id: str) -> 'DecisionTree':
        """
        Wczytuje drzewo decyzyjne z pliku
        
        Args:
            tree_id: Identyfikator drzewa do wczytania
            
        Returns:
            DecisionTree: Wczytane drzewo decyzyjne
        """
        file_path = DECISION_TREE_DIR / f"{tree_id}.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Nie znaleziono pliku drzewa decyzyjnego: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            tree_data = json.load(f)
        
        tree = cls(tree_id=tree_data["tree_id"], name=tree_data["name"])
        tree.root_id = tree_data["root_id"]
        tree.current_node_id = tree_data["current_node_id"]
        tree.metadata = tree_data["metadata"]
        
        # Najpierw utwórz wszystkie węzły
        for node_id, node_data in tree_data["nodes"].items():
            tree.nodes[node_id] = DecisionNode.from_dict(node_data)
        
        # Następnie ustaw relacje między węzłami
        for node_id, node_data in tree_data["nodes"].items():
            for child_id in node_data["children"]:
                if child_id in tree.nodes:
                    tree.nodes[node_id].add_child(tree.nodes[child_id])
        
        logger.info(f"Wczytano drzewo decyzyjne z pliku: {file_path}")
        
        return tree
    
    @classmethod
    def list_trees(cls) -> List[Dict[str, Any]]:
        """
        Zwraca listę dostępnych drzew decyzyjnych
        
        Returns:
            List[Dict]: Lista drzew decyzyjnych z metadanymi
        """
        trees = []
        
        for file_path in DECISION_TREE_DIR.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree_data = json.load(f)
                
                trees.append({
                    "tree_id": tree_data["tree_id"],
                    "name": tree_data["name"],
                    "created_at": tree_data["metadata"]["created_at"],
                    "updated_at": tree_data["metadata"]["updated_at"],
                    "success_rate": tree_data["metadata"]["success_rate"],
                    "total_nodes": tree_data["metadata"]["total_nodes"]
                })
            except Exception as e:
                logger.error(f"Błąd podczas wczytywania drzewa z pliku {file_path}: {e}")
        
        return sorted(trees, key=lambda x: x["updated_at"], reverse=True)
    
    def visualize(self, output_path: Optional[str] = None) -> str:
        """
        Generuje wizualizację drzewa decyzyjnego
        
        Args:
            output_path: Ścieżka do zapisania wizualizacji (opcjonalnie)
            
        Returns:
            str: Ścieżka do zapisanej wizualizacji
        """
        if not output_path:
            output_path = str(DECISION_TREE_DIR / f"{self.tree_id}_viz.png")
        
        # Utwórz graf za pomocą networkx
        G = nx.DiGraph()
        
        # Dodaj węzły do grafu
        for node_id, node in self.nodes.items():
            # Określ kolor węzła na podstawie wyniku
            if node.result is None:
                color = "lightgray"  # Brak wyniku
            elif node.result:
                color = "lightgreen"  # Sukces
            else:
                color = "lightcoral"  # Porażka
            
            # Dodaj węzeł z etykietą i kolorem
            label = f"{node.decision_type}\n{node.query[:20]}..."
            G.add_node(node_id, label=label, color=color)
            
            # Dodaj krawędzie do dzieci
            for child in node.children:
                G.add_edge(node_id, child.node_id)
        
        # Utwórz rysunek
        plt.figure(figsize=(12, 8))
        pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
        
        # Pobierz kolory węzłów
        node_colors = [G.nodes[n].get("color", "lightgray") for n in G.nodes()]
        
        # Narysuj graf
        nx.draw(G, pos, with_labels=False, node_color=node_colors, 
                node_size=1000, arrows=True, arrowsize=20)
        
        # Dodaj etykiety
        labels = {n: G.nodes[n].get("label", n) for n in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)
        
        # Dodaj tytuł
        plt.title(f"Drzewo decyzyjne: {self.name}")
        
        # Zapisz rysunek
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        
        logger.info(f"Zapisano wizualizację drzewa decyzyjnego do pliku: {output_path}")
        
        return output_path
    
    def export_to_dot(self, output_path: Optional[str] = None) -> str:
        """
        Eksportuje drzewo decyzyjne do formatu DOT (Graphviz)
        
        Args:
            output_path: Ścieżka do zapisania pliku DOT (opcjonalnie)
            
        Returns:
            str: Ścieżka do zapisanego pliku DOT
        """
        if not output_path:
            output_path = str(DECISION_TREE_DIR / f"{self.tree_id}.dot")
        
        # Utwórz graf za pomocą networkx
        G = nx.DiGraph()
        
        # Dodaj węzły do grafu
        for node_id, node in self.nodes.items():
            # Określ kolor węzła na podstawie wyniku
            if node.result is None:
                color = "lightgray"  # Brak wyniku
            elif node.result:
                color = "lightgreen"  # Sukces
            else:
                color = "lightcoral"  # Porażka
            
            # Dodaj węzeł z etykietą i kolorem
            label = f"{node.decision_type}\\n{node.query[:20]}..."
            G.add_node(node_id, label=label, fillcolor=color, style="filled")
            
            # Dodaj krawędzie do dzieci
            for child in node.children:
                G.add_edge(node_id, child.node_id)
        
        # Zapisz graf w formacie DOT
        nx.nx_agraph.write_dot(G, output_path)
        
        logger.info(f"Zapisano drzewo decyzyjne w formacie DOT do pliku: {output_path}")
        
        return output_path
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """
        Analizuje wzorce w drzewie decyzyjnym
        
        Returns:
            Dict: Wyniki analizy wzorców
        """
        results = {
            "decision_types": {},
            "success_rates": {},
            "common_patterns": [],
            "failure_patterns": []
        }
        
        # Analizuj typy decyzji i wskaźniki sukcesu
        for node in self.nodes.values():
            # Zliczaj typy decyzji
            if node.decision_type not in results["decision_types"]:
                results["decision_types"][node.decision_type] = {
                    "total": 0,
                    "success": 0,
                    "failure": 0
                }
            
            results["decision_types"][node.decision_type]["total"] += 1
            
            # Zliczaj sukcesy i porażki
            if node.result is not None:
                if node.result:
                    results["decision_types"][node.decision_type]["success"] += 1
                else:
                    results["decision_types"][node.decision_type]["failure"] += 1
        
        # Oblicz wskaźniki sukcesu dla każdego typu decyzji
        for decision_type, counts in results["decision_types"].items():
            if counts["total"] > 0:
                success_rate = counts["success"] / counts["total"]
                results["success_rates"][decision_type] = success_rate
        
        # Znajdź wzorce prowadzące do sukcesu
        successful_paths = []
        for node_id, node in self.nodes.items():
            if node.result and not node.children:  # Sukces i liść
                path = self.get_path_to_node(node_id)
                if len(path) > 1:
                    path_types = [self.nodes[nid].decision_type for nid in path]
                    successful_paths.append(path_types)
        
        # Znajdź najczęstsze wzorce sukcesu
        if successful_paths:
            from collections import Counter
            path_counter = Counter(tuple(path) for path in successful_paths)
            results["common_patterns"] = [
                {"path": list(path), "count": count}
                for path, count in path_counter.most_common(5)
            ]
        
        # Znajdź wzorce prowadzące do porażki
        failure_paths = []
        for node_id, node in self.nodes.items():
            if node.result is False:  # Porażka
                path = self.get_path_to_node(node_id)
                if len(path) > 1:
                    path_types = [self.nodes[nid].decision_type for nid in path]
                    failure_paths.append(path_types)
        
        # Znajdź najczęstsze wzorce porażki
        if failure_paths:
            from collections import Counter
            path_counter = Counter(tuple(path) for path in failure_paths)
            results["failure_patterns"] = [
                {"path": list(path), "count": count}
                for path, count in path_counter.most_common(5)
            ]
        
        return results
    
    def train_decision_model(self) -> Optional[DecisionTreeClassifier]:
        """
        Trenuje model drzewa decyzyjnego na podstawie zebranych danych
        
        Returns:
            DecisionTreeClassifier: Wytrenowany model drzewa decyzyjnego lub None, jeśli brak wystarczających danych
        """
        # Przygotuj dane do treningu
        X = []  # Cechy
        y = []  # Etykiety (sukces/porażka)
        
        for node in self.nodes.values():
            if node.result is not None:  # Tylko węzły z wynikiem
                # Przygotuj cechy
                features = {
                    "decision_type": node.decision_type,
                    "query_length": len(node.query),
                    "content_length": len(node.content),
                    "has_parent": 1 if node.parent_id else 0
                }
                
                # Dodaj metryki jako cechy
                for metric_name, metric_value in node.metrics.items():
                    if isinstance(metric_value, (int, float)):
                        features[f"metric_{metric_name}"] = metric_value
                
                # Przekształć cechy na wektor
                feature_vector = self._encode_features(features)
                
                X.append(feature_vector)
                y.append(1 if node.result else 0)
        
        # Sprawdź, czy mamy wystarczająco danych
        if len(X) < 10 or len(set(y)) < 2:
            logger.warning("Niewystarczająca ilość danych do treningu modelu")
            return None
        
        # Podziel dane na zbiór treningowy i testowy
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Trenuj model
        model = DecisionTreeClassifier(max_depth=5)
        model.fit(X_train, y_train)
        
        # Oceń model
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Wytrenowano model drzewa decyzyjnego z dokładnością: {accuracy:.2f}")
        
        # Zapisz metryki modelu
        self.metadata["model_metrics"] = {
            "accuracy": accuracy,
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1": f1_score(y_test, y_pred, zero_division=0),
            "feature_importance": dict(zip(self._get_feature_names(), model.feature_importances_))
        }
        
        return model
    
    def _encode_features(self, features: Dict[str, Any]) -> List[float]:
        """
        Koduje cechy do postaci wektora
        
        Args:
            features: Słownik cech
            
        Returns:
            List[float]: Wektor cech
        """
        # Dla uproszczenia, używamy tylko cech numerycznych
        numeric_features = []
        
        # Kodowanie typu decyzji
        decision_types = ["code_generation", "validation", "execution", "analysis"]
        for dt in decision_types:
            numeric_features.append(1.0 if features.get("decision_type") == dt else 0.0)
        
        # Dodaj pozostałe cechy numeryczne
        for name, value in features.items():
            if name != "decision_type" and isinstance(value, (int, float)):
                numeric_features.append(float(value))
        
        return numeric_features
    
    def _get_feature_names(self) -> List[str]:
        """
        Zwraca nazwy cech używanych w modelu
        
        Returns:
            List[str]: Nazwy cech
        """
        # Musi być zgodne z kolejnością w _encode_features
        feature_names = ["is_code_generation", "is_validation", "is_execution", "is_analysis",
                         "query_length", "content_length", "has_parent"]
        
        # Dodaj nazwy metryk
        all_metrics = set()
        for node in self.nodes.values():
            all_metrics.update(node.metrics.keys())
        
        for metric in sorted(all_metrics):
            feature_names.append(f"metric_{metric}")
        
        return feature_names
    
    def visualize_decision_model(self, model: DecisionTreeClassifier, 
                                output_path: Optional[str] = None) -> str:
        """
        Generuje wizualizację modelu drzewa decyzyjnego
        
        Args:
            model: Model drzewa decyzyjnego
            output_path: Ścieżka do zapisania wizualizacji (opcjonalnie)
            
        Returns:
            str: Ścieżka do zapisanej wizualizacji
        """
        if not output_path:
            output_path = str(DECISION_TREE_DIR / f"{self.tree_id}_model.png")
        
        # Przygotuj nazwy cech i klas
        feature_names = self._get_feature_names()
        class_names = ["Porażka", "Sukces"]
        
        # Utwórz rysunek
        plt.figure(figsize=(20, 10))
        tree.plot_tree(model, feature_names=feature_names, class_names=class_names, 
                      filled=True, rounded=True, fontsize=8)
        
        plt.title(f"Model drzewa decyzyjnego: {self.name}")
        
        # Zapisz rysunek
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        
        logger.info(f"Zapisano wizualizację modelu drzewa decyzyjnego do pliku: {output_path}")
        
        return output_path


# Funkcja pomocnicza do tworzenia nowego drzewa decyzyjnego
def create_decision_tree(name: Optional[str] = None) -> DecisionTree:
    """
    Tworzy nowe drzewo decyzyjne
    
    Args:
        name: Nazwa drzewa (opcjonalnie)
        
    Returns:
        DecisionTree: Nowe drzewo decyzyjne
    """
    return DecisionTree(name=name)

# Funkcja pomocnicza do wczytywania drzewa decyzyjnego
def load_decision_tree(tree_id: str) -> DecisionTree:
    """
    Wczytuje drzewo decyzyjne
    
    Args:
        tree_id: Identyfikator drzewa
        
    Returns:
        DecisionTree: Wczytane drzewo decyzyjne
    """
    return DecisionTree.load(tree_id)

# Funkcja pomocnicza do listowania dostępnych drzew decyzyjnych
def list_decision_trees() -> List[Dict[str, Any]]:
    """
    Zwraca listę dostępnych drzew decyzyjnych
    
    Returns:
        List[Dict]: Lista drzew decyzyjnych z metadanymi
    """
    return DecisionTree.list_trees()

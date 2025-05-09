#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł konwersji tekstu na obrazy (Text-to-Image)
"""

import os
import sys
import logging
import json
import base64
import requests
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('text2image')

# Dodaj katalog główny projektu do ścieżki Pythona
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importuj moduł ollama_api
try:
    from ollama_api import OllamaAPI
except ImportError:
    logger.error("Nie można zaimportować modułu ollama_api. Upewnij się, że jest zainstalowany.")
    OllamaAPI = None

class Text2Image:
    """Klasa konwertująca tekst na obrazy"""
    
    def __init__(self, model="llama3", config_file=None):
        """
        Inicjalizacja konwertera text2image
        
        Args:
            model (str): Model LLM do generowania tekstu
            config_file (str): Ścieżka do pliku konfiguracyjnego
        """
        self.model = model
        self.ollama_api = OllamaAPI() if OllamaAPI else None
        
        # Załaduj konfigurację
        self.config = self._load_config(config_file)
        
        # Sprawdź dostępność modelu
        if self.ollama_api:
            logger.info(f"Sprawdzanie dostępności modelu {model}...")
            if self.ollama_api.check_model_exists(model):
                logger.info(f"Model {model} jest dostępny")
            else:
                logger.warning(f"Model {model} nie jest dostępny. Spróbuj pobrać go za pomocą 'ollama pull {model}'")
        
        # Sprawdź dostępność bibliotek do generowania obrazów
        self._check_image_libraries()
    
    def _load_config(self, config_file=None):
        """
        Ładuje konfigurację z pliku
        
        Args:
            config_file (str): Ścieżka do pliku konfiguracyjnego
            
        Returns:
            dict: Konfiguracja
        """
        default_config = {
            "output_dir": str(PROJECT_ROOT / "output" / "images"),
            "default_width": 512,
            "default_height": 512,
            "default_format": "png",
            "api_keys": {
                "stability_ai": "",
                "openai": "",
                "replicate": ""
            },
            "default_provider": "local",  # local, stability_ai, openai, replicate
            "local_model": "stable-diffusion"
        }
        
        if not config_file:
            config_file = PROJECT_ROOT / "config" / "image_config.json"
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Aktualizuj domyślną konfigurację załadowanymi wartościami
                    default_config.update(loaded_config)
                    logger.info(f"Załadowano konfigurację z pliku: {config_file}")
            else:
                logger.warning(f"Plik konfiguracyjny nie istnieje: {config_file}")
                logger.info("Tworzenie domyślnego pliku konfiguracyjnego...")
                
                # Utwórz katalog, jeśli nie istnieje
                os.makedirs(os.path.dirname(config_file), exist_ok=True)
                
                # Zapisz domyślną konfigurację
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4)
        except Exception as e:
            logger.error(f"Błąd podczas ładowania konfiguracji: {e}")
        
        # Utwórz katalog wyjściowy, jeśli nie istnieje
        os.makedirs(default_config["output_dir"], exist_ok=True)
        
        return default_config
    
    def _check_image_libraries(self):
        """Sprawdza dostępność bibliotek do generowania obrazów"""
        self.available_libraries = {
            "pillow": self._check_module("PIL"),
            "matplotlib": self._check_module("matplotlib"),
            "stable_diffusion": self._check_module("diffusers"),
            "opencv": self._check_module("cv2")
        }
        
        if not any(self.available_libraries.values()):
            logger.warning("Brak dostępnych bibliotek do generowania obrazów")
            logger.info("Zainstaluj 'pillow', 'matplotlib', 'diffusers' lub 'opencv-python' aby korzystać z generowania obrazów")
    
    def _check_module(self, module_name):
        """
        Sprawdza, czy moduł jest dostępny
        
        Args:
            module_name (str): Nazwa modułu
            
        Returns:
            bool: True jeśli moduł jest dostępny, False w przeciwnym razie
        """
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    def convert(self, text, width=None, height=None, output_format=None, provider=None):
        """
        Konwertuje tekst na obraz
        
        Args:
            text (str): Tekst do konwersji
            width (int): Szerokość obrazu
            height (int): Wysokość obrazu
            output_format (str): Format wyjściowy (png, jpg)
            provider (str): Dostawca usługi generowania obrazów
            
        Returns:
            dict: Informacje o wygenerowanym obrazie
        """
        if not text:
            return {"error": "Nie podano tekstu do konwersji"}
        
        # Ustaw domyślne wartości, jeśli nie zostały podane
        if not width:
            width = self.config.get("default_width", 512)
        
        if not height:
            height = self.config.get("default_height", 512)
        
        if not output_format:
            output_format = self.config.get("default_format", "png")
        
        if not provider:
            provider = self.config.get("default_provider", "local")
        
        # Przygotuj prompt dla modelu generującego obrazy
        prompt = self._enhance_prompt(text)
        
        try:
            # Wybierz odpowiednią metodę generowania obrazu
            if provider == "local":
                result = self._generate_local_image(prompt, width, height, output_format)
            elif provider == "stability_ai":
                result = self._generate_stability_ai_image(prompt, width, height, output_format)
            elif provider == "openai":
                result = self._generate_openai_image(prompt, width, height, output_format)
            elif provider == "replicate":
                result = self._generate_replicate_image(prompt, width, height, output_format)
            else:
                return {"error": f"Nieznany dostawca usługi generowania obrazów: {provider}"}
            
            if "error" in result:
                return result
            
            # Dodaj informacje o wygenerowanym obrazie
            result.update({
                "prompt": prompt,
                "original_text": text,
                "width": width,
                "height": height,
                "format": output_format,
                "provider": provider,
                "timestamp": datetime.now().isoformat()
            })
            
            return result
        except Exception as e:
            logger.error(f"Błąd podczas konwersji tekstu na obraz: {e}")
            return {"error": str(e)}
    
    def _enhance_prompt(self, text):
        """
        Ulepsza prompt dla modelu generującego obrazy
        
        Args:
            text (str): Oryginalny tekst
            
        Returns:
            str: Ulepszony prompt
        """
        if not self.ollama_api:
            return text
        
        try:
            # Przygotuj prompt dla modelu
            prompt = f"""Ulepsz poniższy opis, aby lepiej działał jako prompt dla modelu generującego obrazy.
Dodaj szczegóły dotyczące stylu, oświetlenia, kompozycji, ale zachowaj oryginalny sens i informacje.
Nie dodawaj nowych elementów ani nie zmieniaj znaczenia.

Opis do ulepszenia:
{text}

Ulepszony prompt:
"""
            
            # Generuj ulepszony prompt
            logger.info("Ulepszanie promptu dla modelu generującego obrazy...")
            response = self.ollama_api.generate(self.model, prompt)
            
            return response.strip()
        except Exception as e:
            logger.error(f"Błąd podczas ulepszania promptu: {e}")
            return text
    
    def _generate_local_image(self, prompt, width, height, output_format):
        """
        Generuje obraz lokalnie
        
        Args:
            prompt (str): Prompt dla modelu
            width (int): Szerokość obrazu
            height (int): Wysokość obrazu
            output_format (str): Format wyjściowy
            
        Returns:
            dict: Informacje o wygenerowanym obrazie
        """
        # Sprawdź, czy dostępne są biblioteki do generowania obrazów
        if self.available_libraries["stable_diffusion"]:
            return self._generate_stable_diffusion_image(prompt, width, height, output_format)
        elif self.available_libraries["pillow"] and self.available_libraries["matplotlib"]:
            return self._generate_text_image(prompt, width, height, output_format)
        else:
            return {"error": "Brak dostępnych bibliotek do generowania obrazów lokalnie"}
    
    def _generate_stable_diffusion_image(self, prompt, width, height, output_format):
        """
        Generuje obraz za pomocą Stable Diffusion
        
        Args:
            prompt (str): Prompt dla modelu
            width (int): Szerokość obrazu
            height (int): Wysokość obrazu
            output_format (str): Format wyjściowy
            
        Returns:
            dict: Informacje o wygenerowanym obrazie
        """
        try:
            from diffusers import StableDiffusionPipeline
            import torch
            
            # Załaduj model
            model_id = self.config.get("local_model", "stable-diffusion")
            pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
            pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
            
            # Generuj obraz
            image = pipe(prompt, height=height, width=width).images[0]
            
            # Zapisz obraz
            timestamp = self._get_timestamp()
            output_path = Path(self.config["output_dir"]) / f"image_{timestamp}.{output_format}"
            image.save(str(output_path))
            
            return {
                "success": True,
                "path": str(output_path),
                "method": "stable_diffusion"
            }
        except Exception as e:
            logger.error(f"Błąd podczas generowania obrazu za pomocą Stable Diffusion: {e}")
            return {"error": f"Błąd podczas generowania obrazu: {str(e)}"}
    
    def _generate_text_image(self, text, width, height, output_format):
        """
        Generuje prosty obraz z tekstem
        
        Args:
            text (str): Tekst do umieszczenia na obrazie
            width (int): Szerokość obrazu
            height (int): Wysokość obrazu
            output_format (str): Format wyjściowy
            
        Returns:
            dict: Informacje o wygenerowanym obrazie
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            import matplotlib.pyplot as plt
            import numpy as np
            
            # Utwórz obraz
            image = Image.new('RGB', (width, height), color=(255, 255, 255))
            draw = ImageDraw.Draw(image)
            
            # Spróbuj załadować czcionkę
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                font = ImageFont.load_default()
            
            # Podziel tekst na linie
            lines = []
            words = text.split()
            current_line = ""
            
            for word in words:
                test_line = current_line + word + " "
                text_width = draw.textlength(test_line, font=font)
                
                if text_width < width - 20:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            
            if current_line:
                lines.append(current_line)
            
            # Narysuj tekst
            y_position = 20
            for line in lines:
                draw.text((10, y_position), line, fill=(0, 0, 0), font=font)
                y_position += 30
            
            # Dodaj tło
            plt.figure(figsize=(width/100, height/100), dpi=100)
            plt.imshow(np.array(image))
            plt.axis('off')
            
            # Zapisz obraz
            timestamp = self._get_timestamp()
            output_path = Path(self.config["output_dir"]) / f"image_{timestamp}.{output_format}"
            plt.savefig(str(output_path), format=output_format, bbox_inches='tight', pad_inches=0)
            plt.close()
            
            return {
                "success": True,
                "path": str(output_path),
                "method": "text_image"
            }
        except Exception as e:
            logger.error(f"Błąd podczas generowania obrazu z tekstem: {e}")
            return {"error": f"Błąd podczas generowania obrazu: {str(e)}"}
    
    def _generate_stability_ai_image(self, prompt, width, height, output_format):
        """
        Generuje obraz za pomocą Stability AI API
        
        Args:
            prompt (str): Prompt dla modelu
            width (int): Szerokość obrazu
            height (int): Wysokość obrazu
            output_format (str): Format wyjściowy
            
        Returns:
            dict: Informacje o wygenerowanym obrazie
        """
        api_key = self.config.get("api_keys", {}).get("stability_ai")
        if not api_key:
            return {"error": "Brak klucza API dla Stability AI"}
        
        try:
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            payload = {
                "text_prompts": [{"text": prompt}],
                "cfg_scale": 7,
                "height": height,
                "width": width,
                "samples": 1,
                "steps": 30,
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                return {"error": f"Błąd API Stability AI: {response.text}"}
            
            data = response.json()
            
            # Pobierz wygenerowany obraz
            for i, image in enumerate(data["artifacts"]):
                image_data = base64.b64decode(image["base64"])
                
                # Zapisz obraz
                timestamp = self._get_timestamp()
                output_path = Path(self.config["output_dir"]) / f"image_{timestamp}.{output_format}"
                
                with open(output_path, "wb") as f:
                    f.write(image_data)
                
                return {
                    "success": True,
                    "path": str(output_path),
                    "method": "stability_ai"
                }
        except Exception as e:
            logger.error(f"Błąd podczas generowania obrazu za pomocą Stability AI: {e}")
            return {"error": f"Błąd podczas generowania obrazu: {str(e)}"}
    
    def _generate_openai_image(self, prompt, width, height, output_format):
        """
        Generuje obraz za pomocą OpenAI API
        
        Args:
            prompt (str): Prompt dla modelu
            width (int): Szerokość obrazu
            height (int): Wysokość obrazu
            output_format (str): Format wyjściowy
            
        Returns:
            dict: Informacje o wygenerowanym obrazie
        """
        api_key = self.config.get("api_keys", {}).get("openai")
        if not api_key:
            return {"error": "Brak klucza API dla OpenAI"}
        
        try:
            import openai
            
            openai.api_key = api_key
            
            # Dostosuj wymiary do wymagań API
            size = "1024x1024"  # Domyślny rozmiar
            if width == 1024 and height == 1792:
                size = "1024x1792"
            elif width == 1792 and height == 1024:
                size = "1792x1024"
            
            response = openai.Image.create(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size=size,
                response_format="b64_json"
            )
            
            image_data = base64.b64decode(response["data"][0]["b64_json"])
            
            # Zapisz obraz
            timestamp = self._get_timestamp()
            output_path = Path(self.config["output_dir"]) / f"image_{timestamp}.{output_format}"
            
            with open(output_path, "wb") as f:
                f.write(image_data)
            
            return {
                "success": True,
                "path": str(output_path),
                "method": "openai"
            }
        except Exception as e:
            logger.error(f"Błąd podczas generowania obrazu za pomocą OpenAI: {e}")
            return {"error": f"Błąd podczas generowania obrazu: {str(e)}"}
    
    def _generate_replicate_image(self, prompt, width, height, output_format):
        """
        Generuje obraz za pomocą Replicate API
        
        Args:
            prompt (str): Prompt dla modelu
            width (int): Szerokość obrazu
            height (int): Wysokość obrazu
            output_format (str): Format wyjściowy
            
        Returns:
            dict: Informacje o wygenerowanym obrazie
        """
        api_key = self.config.get("api_keys", {}).get("replicate")
        if not api_key:
            return {"error": "Brak klucza API dla Replicate"}
        
        try:
            import replicate
            
            # Ustaw klucz API
            os.environ["REPLICATE_API_TOKEN"] = api_key
            
            # Uruchom model
            output = replicate.run(
                "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
                input={
                    "prompt": prompt,
                    "width": width,
                    "height": height
                }
            )
            
            # Pobierz wygenerowany obraz
            image_url = output[0]
            response = requests.get(image_url)
            
            if response.status_code != 200:
                return {"error": f"Błąd pobierania obrazu: {response.status_code}"}
            
            # Zapisz obraz
            timestamp = self._get_timestamp()
            output_path = Path(self.config["output_dir"]) / f"image_{timestamp}.{output_format}"
            
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            return {
                "success": True,
                "path": str(output_path),
                "method": "replicate"
            }
        except Exception as e:
            logger.error(f"Błąd podczas generowania obrazu za pomocą Replicate: {e}")
            return {"error": f"Błąd podczas generowania obrazu: {str(e)}"}
    
    def _get_timestamp(self):
        """
        Generuje unikalny znacznik czasu
        
        Returns:
            str: Znacznik czasu
        """
        import time
        return str(int(time.time()))
    
    def list_images(self, limit=None):
        """
        Pobiera listę wygenerowanych obrazów
        
        Args:
            limit (int): Maksymalna liczba obrazów do pobrania
            
        Returns:
            list: Lista ścieżek do obrazów
        """
        output_dir = Path(self.config.get("output_dir"))
        
        try:
            if not output_dir.exists():
                return []
            
            # Pobierz wszystkie pliki obrazów
            image_files = []
            for ext in ["png", "jpg", "jpeg"]:
                image_files.extend(list(output_dir.glob(f"*.{ext}")))
            
            # Sortuj według daty modyfikacji (od najnowszych)
            image_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Ogranicz liczbę elementów, jeśli podano limit
            if limit and limit > 0:
                image_files = image_files[:limit]
            
            return [str(file) for file in image_files]
        except Exception as e:
            logger.error(f"Błąd podczas pobierania listy obrazów: {e}")
            return []
    
    def generate_chart(self, data, chart_type="bar", title=None, width=800, height=600):
        """
        Generuje wykres na podstawie danych
        
        Args:
            data (dict): Dane do wykresu
            chart_type (str): Typ wykresu (bar, line, pie, scatter)
            title (str): Tytuł wykresu
            width (int): Szerokość wykresu
            height (int): Wysokość wykresu
            
        Returns:
            dict: Informacje o wygenerowanym wykresie
        """
        if not self.available_libraries["matplotlib"]:
            return {"error": "Brak biblioteki matplotlib do generowania wykresów"}
        
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            # Utwórz wykres
            plt.figure(figsize=(width/100, height/100), dpi=100)
            
            if chart_type == "bar":
                plt.bar(list(data.keys()), list(data.values()))
            elif chart_type == "line":
                plt.plot(list(data.keys()), list(data.values()))
            elif chart_type == "pie":
                plt.pie(list(data.values()), labels=list(data.keys()), autopct='%1.1f%%')
            elif chart_type == "scatter":
                plt.scatter(list(data.keys()), list(data.values()))
            else:
                return {"error": f"Nieznany typ wykresu: {chart_type}"}
            
            # Dodaj tytuł
            if title:
                plt.title(title)
            
            # Zapisz wykres
            timestamp = self._get_timestamp()
            output_path = Path(self.config["output_dir"]) / f"chart_{timestamp}.png"
            plt.savefig(str(output_path), bbox_inches='tight')
            plt.close()
            
            return {
                "success": True,
                "path": str(output_path),
                "method": "matplotlib",
                "chart_type": chart_type
            }
        except Exception as e:
            logger.error(f"Błąd podczas generowania wykresu: {e}")
            return {"error": f"Błąd podczas generowania wykresu: {str(e)}"}
    
    def generate_diagram(self, text, diagram_type="flowchart", width=800, height=600):
        """
        Generuje diagram na podstawie tekstu
        
        Args:
            text (str): Tekst opisujący diagram
            diagram_type (str): Typ diagramu (flowchart, sequence, class)
            width (int): Szerokość diagramu
            height (int): Wysokość diagramu
            
        Returns:
            dict: Informacje o wygenerowanym diagramie
        """
        # Sprawdź, czy dostępne są biblioteki do generowania diagramów
        try:
            # Przygotuj prompt dla modelu
            if self.ollama_api:
                prompt = f"""Przekształć poniższy opis w kod diagramu Mermaid.
Typ diagramu: {diagram_type}

Opis:
{text}

Kod Mermaid:
```mermaid
"""
                
                # Generuj kod Mermaid
                logger.info("Generowanie kodu Mermaid dla diagramu...")
                response = self.ollama_api.generate(self.model, prompt)
                
                # Wyodrębnij kod Mermaid
                mermaid_code = response.strip()
                if "```" in mermaid_code:
                    mermaid_code = mermaid_code.split("```")[0]
            else:
                # Prosty szablon diagramu
                if diagram_type == "flowchart":
                    mermaid_code = f"""flowchart TD
    A[Start] --> B[Proces]
    B --> C[Decyzja]
    C -->|Tak| D[Akcja 1]
    C -->|Nie| E[Akcja 2]
    D --> F[Koniec]
    E --> F
"""
                elif diagram_type == "sequence":
                    mermaid_code = f"""sequenceDiagram
    participant A as Użytkownik
    participant B as System
    A->>B: Żądanie
    B->>A: Odpowiedź
"""
                elif diagram_type == "class":
                    mermaid_code = f"""classDiagram
    class Klasa1 {
        +atrybut1
        +metoda1()
    }
    class Klasa2 {
        +atrybut2
        +metoda2()
    }
    Klasa1 --|> Klasa2
"""
                else:
                    return {"error": f"Nieznany typ diagramu: {diagram_type}"}
            
            # Zapisz kod Mermaid do pliku
            timestamp = self._get_timestamp()
            mermaid_path = Path(self.config["output_dir"]) / f"diagram_{timestamp}.mmd"
            with open(mermaid_path, "w", encoding="utf-8") as f:
                f.write(mermaid_code)
            
            # Renderuj diagram za pomocą API Mermaid
            try:
                url = "https://mermaid.ink/img/"
                encoded_code = base64.urlsafe_b64encode(mermaid_code.encode()).decode()
                response = requests.get(f"{url}{encoded_code}")
                
                if response.status_code == 200:
                    # Zapisz diagram
                    output_path = Path(self.config["output_dir"]) / f"diagram_{timestamp}.png"
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    
                    return {
                        "success": True,
                        "path": str(output_path),
                        "mermaid_path": str(mermaid_path),
                        "method": "mermaid",
                        "diagram_type": diagram_type
                    }
                else:
                    return {"error": f"Błąd podczas renderowania diagramu: {response.status_code}"}
            except Exception as e:
                logger.error(f"Błąd podczas renderowania diagramu: {e}")
                return {
                    "success": True,
                    "path": str(mermaid_path),
                    "method": "mermaid_code",
                    "diagram_type": diagram_type,
                    "warning": "Wygenerowano tylko kod Mermaid, bez renderowania diagramu"
                }
        except Exception as e:
            logger.error(f"Błąd podczas generowania diagramu: {e}")
            return {"error": f"Błąd podczas generowania diagramu: {str(e)}"}

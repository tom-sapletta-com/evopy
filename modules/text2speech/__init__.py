#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł konwersji tekstu na mowę (Text-to-Speech)
"""

import os
import sys
import logging
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('text2speech')

# Dodaj katalog główny projektu do ścieżki Pythona
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importuj moduł ollama_api
try:
    from ollama_api import OllamaAPI
except ImportError:
    logger.error("Nie można zaimportować modułu ollama_api. Upewnij się, że jest zainstalowany.")
    OllamaAPI = None

class Text2Speech:
    """Klasa konwertująca tekst na mowę"""
    
    def __init__(self, model="llama3", engine="gtts", voice="pl", output_dir=None):
        """
        Inicjalizacja konwertera text2speech
        
        Args:
            model (str): Model LLM do generowania tekstu
            engine (str): Silnik TTS do użycia (gtts, pyttsx3, espeak)
            voice (str): Głos do użycia (kod języka lub nazwa głosu)
            output_dir (str): Katalog do zapisywania plików audio
        """
        self.model = model
        self.engine = engine
        self.voice = voice
        self.ollama_api = OllamaAPI() if OllamaAPI else None
        
        # Ustaw katalog wyjściowy
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = PROJECT_ROOT / "output" / "audio"
        
        # Utwórz katalog wyjściowy, jeśli nie istnieje
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Sprawdź dostępność silnika TTS
        self._check_tts_engine()
        
        # Sprawdź dostępność modelu
        if self.ollama_api:
            logger.info(f"Sprawdzanie dostępności modelu {model}...")
            if self.ollama_api.check_model_exists(model):
                logger.info(f"Model {model} jest dostępny")
            else:
                logger.warning(f"Model {model} nie jest dostępny. Spróbuj pobrać go za pomocą 'ollama pull {model}'")
    
    def _check_tts_engine(self):
        """Sprawdza dostępność wybranego silnika TTS"""
        if self.engine == "gtts":
            try:
                import gtts
                self.tts_available = True
                logger.info("Silnik gTTS jest dostępny")
            except ImportError:
                logger.warning("Silnik gTTS nie jest dostępny. Zainstaluj go za pomocą 'pip install gtts'")
                self.tts_available = False
        
        elif self.engine == "pyttsx3":
            try:
                import pyttsx3
                self.tts_available = True
                logger.info("Silnik pyttsx3 jest dostępny")
            except ImportError:
                logger.warning("Silnik pyttsx3 nie jest dostępny. Zainstaluj go za pomocą 'pip install pyttsx3'")
                self.tts_available = False
        
        elif self.engine == "espeak":
            try:
                # Sprawdź czy espeak jest zainstalowany
                subprocess.run(["espeak", "--version"], capture_output=True, check=True)
                self.tts_available = True
                logger.info("Silnik espeak jest dostępny")
            except (subprocess.SubprocessError, FileNotFoundError):
                logger.warning("Silnik espeak nie jest dostępny. Zainstaluj go za pomocą 'apt-get install espeak'")
                self.tts_available = False
        
        else:
            logger.warning(f"Nieznany silnik TTS: {self.engine}. Używanie domyślnego silnika gTTS")
            self.engine = "gtts"
            self._check_tts_engine()
    
    def convert(self, text, output_format="mp3", play=False):
        """
        Konwertuje tekst na mowę
        
        Args:
            text (str): Tekst do konwersji
            output_format (str): Format wyjściowy (mp3, wav)
            play (bool): Czy odtworzyć wygenerowany dźwięk
            
        Returns:
            str: Ścieżka do wygenerowanego pliku audio lub komunikat o błędzie
        """
        if not text:
            return "Nie podano tekstu do konwersji"
        
        # Przygotuj nazwę pliku wyjściowego
        timestamp = self._get_timestamp()
        output_file = self.output_dir / f"speech_{timestamp}.{output_format}"
        
        try:
            # Konwertuj tekst na mowę za pomocą wybranego silnika
            if self.engine == "gtts":
                self._convert_gtts(text, output_file)
            elif self.engine == "pyttsx3":
                self._convert_pyttsx3(text, output_file)
            elif self.engine == "espeak":
                self._convert_espeak(text, output_file)
            else:
                return f"Nieobsługiwany silnik TTS: {self.engine}"
            
            # Odtwórz wygenerowany dźwięk, jeśli wymagane
            if play:
                self._play_audio(output_file)
            
            return str(output_file)
        except Exception as e:
            logger.error(f"Błąd podczas konwersji tekstu na mowę: {e}")
            return f"Błąd: {str(e)}"
    
    def _convert_gtts(self, text, output_file):
        """
        Konwertuje tekst na mowę za pomocą gTTS
        
        Args:
            text (str): Tekst do konwersji
            output_file (Path): Ścieżka do pliku wyjściowego
        """
        try:
            from gtts import gTTS
            
            # Utwórz obiekt gTTS
            tts = gTTS(text=text, lang=self.voice, slow=False)
            
            # Zapisz do pliku
            tts.save(str(output_file))
            
            logger.info(f"Wygenerowano plik audio: {output_file}")
        except ImportError:
            raise ImportError("Silnik gTTS nie jest zainstalowany. Zainstaluj go za pomocą 'pip install gtts'")
    
    def _convert_pyttsx3(self, text, output_file):
        """
        Konwertuje tekst na mowę za pomocą pyttsx3
        
        Args:
            text (str): Tekst do konwersji
            output_file (Path): Ścieżka do pliku wyjściowego
        """
        try:
            import pyttsx3
            
            # Inicjalizacja silnika
            engine = pyttsx3.init()
            
            # Ustaw właściwości głosu
            voices = engine.getProperty('voices')
            for voice in voices:
                if self.voice in voice.id.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            # Zapisz do pliku
            engine.save_to_file(text, str(output_file))
            engine.runAndWait()
            
            logger.info(f"Wygenerowano plik audio: {output_file}")
        except ImportError:
            raise ImportError("Silnik pyttsx3 nie jest zainstalowany. Zainstaluj go za pomocą 'pip install pyttsx3'")
    
    def _convert_espeak(self, text, output_file):
        """
        Konwertuje tekst na mowę za pomocą espeak
        
        Args:
            text (str): Tekst do konwersji
            output_file (Path): Ścieżka do pliku wyjściowego
        """
        try:
            # Przygotuj komendę espeak
            cmd = [
                "espeak",
                "-v", self.voice,
                "-w", str(output_file),
                text
            ]
            
            # Uruchom komendę
            subprocess.run(cmd, check=True, capture_output=True)
            
            logger.info(f"Wygenerowano plik audio: {output_file}")
        except subprocess.SubprocessError as e:
            raise RuntimeError(f"Błąd podczas uruchamiania espeak: {e}")
    
    def _play_audio(self, audio_file):
        """
        Odtwarza plik audio
        
        Args:
            audio_file (Path): Ścieżka do pliku audio
        """
        try:
            # Sprawdź system operacyjny
            import platform
            system = platform.system()
            
            if system == "Linux":
                # Użyj aplay na Linuksie
                subprocess.Popen(["aplay", str(audio_file)])
            elif system == "Darwin":
                # Użyj afplay na macOS
                subprocess.Popen(["afplay", str(audio_file)])
            elif system == "Windows":
                # Użyj wbudowanego odtwarzacza na Windows
                os.startfile(str(audio_file))
            else:
                logger.warning(f"Nieobsługiwany system operacyjny: {system}")
        except Exception as e:
            logger.error(f"Błąd podczas odtwarzania pliku audio: {e}")
    
    def _get_timestamp(self):
        """
        Generuje unikalny znacznik czasu
        
        Returns:
            str: Znacznik czasu
        """
        import time
        return str(int(time.time()))
    
    def enhance_text(self, text):
        """
        Ulepsza tekst przed konwersją na mowę
        
        Args:
            text (str): Tekst do ulepszenia
            
        Returns:
            str: Ulepszony tekst
        """
        if not self.ollama_api:
            return text
        
        try:
            # Przygotuj prompt dla modelu
            prompt = f"""Ulepsz poniższy tekst, aby lepiej brzmiał w formie mówionej.
Popraw interpunkcję, dodaj pauzy i intonację, ale zachowaj oryginalny sens i informacje.
Nie dodawaj nowych informacji ani nie zmieniaj znaczenia.

Tekst do ulepszenia:
{text}

Ulepszony tekst:
"""
            
            # Generuj ulepszony tekst
            logger.info("Ulepszanie tekstu przed konwersją na mowę...")
            response = self.ollama_api.generate(self.model, prompt)
            
            return response.strip()
        except Exception as e:
            logger.error(f"Błąd podczas ulepszania tekstu: {e}")
            return text
    
    def list_available_voices(self):
        """
        Zwraca listę dostępnych głosów
        
        Returns:
            list: Lista dostępnych głosów
        """
        voices = []
        
        try:
            if self.engine == "gtts":
                # gTTS obsługuje kody języków ISO 639-1
                voices = [
                    "af", "ar", "bg", "bn", "bs", "ca", "cs", "cy", "da", "de", "el", "en", "eo", "es",
                    "et", "fi", "fr", "gu", "hi", "hr", "hu", "hy", "id", "is", "it", "ja", "jw", "km",
                    "kn", "ko", "la", "lv", "mk", "ml", "mr", "my", "ne", "nl", "no", "pl", "pt", "ro",
                    "ru", "si", "sk", "sq", "sr", "su", "sv", "sw", "ta", "te", "th", "tl", "tr", "uk",
                    "ur", "vi", "zh-CN", "zh-TW"
                ]
            
            elif self.engine == "pyttsx3":
                # Pobierz głosy z pyttsx3
                import pyttsx3
                engine = pyttsx3.init()
                for voice in engine.getProperty('voices'):
                    voices.append(voice.id)
            
            elif self.engine == "espeak":
                # Pobierz głosy z espeak
                result = subprocess.run(["espeak", "--voices"], capture_output=True, text=True)
                for line in result.stdout.splitlines()[1:]:  # Pomiń nagłówek
                    parts = line.split()
                    if len(parts) >= 4:
                        voices.append(parts[3])
        
        except Exception as e:
            logger.error(f"Błąd podczas pobierania listy głosów: {e}")
        
        return voices

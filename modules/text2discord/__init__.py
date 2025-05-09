#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł konwersji tekstu na wiadomości Discord (Text-to-Discord)
"""

import os
import sys
import logging
import json
import requests
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('text2discord')

# Dodaj katalog główny projektu do ścieżki Pythona
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importuj moduł ollama_api
try:
    from ollama_api import OllamaAPI
except ImportError:
    logger.error("Nie można zaimportować modułu ollama_api. Upewnij się, że jest zainstalowany.")
    OllamaAPI = None

class Text2Discord:
    """Klasa konwertująca tekst na wiadomości Discord"""
    
    def __init__(self, model="llama3", config_file=None):
        """
        Inicjalizacja konwertera text2discord
        
        Args:
            model (str): Model LLM do generowania tekstu
            config_file (str): Ścieżka do pliku konfiguracyjnego Discord
        """
        self.model = model
        self.ollama_api = OllamaAPI() if OllamaAPI else None
        
        # Załaduj konfigurację Discord
        self.config = self._load_config(config_file)
        
        # Sprawdź dostępność modelu
        if self.ollama_api:
            logger.info(f"Sprawdzanie dostępności modelu {model}...")
            if self.ollama_api.check_model_exists(model):
                logger.info(f"Model {model} jest dostępny")
            else:
                logger.warning(f"Model {model} nie jest dostępny. Spróbuj pobrać go za pomocą 'ollama pull {model}'")
    
    def _load_config(self, config_file=None):
        """
        Ładuje konfigurację Discord z pliku
        
        Args:
            config_file (str): Ścieżka do pliku konfiguracyjnego
            
        Returns:
            dict: Konfiguracja Discord
        """
        default_config = {
            "webhooks": {},
            "default_webhook": "",
            "default_username": "Evopy Bot",
            "default_avatar_url": "",
            "history_file": str(PROJECT_ROOT / "history" / "discord_messages.json"),
            "max_history": 100
        }
        
        if not config_file:
            config_file = PROJECT_ROOT / "config" / "discord_config.json"
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Aktualizuj domyślną konfigurację załadowanymi wartościami
                    default_config.update(loaded_config)
                    logger.info(f"Załadowano konfigurację Discord z pliku: {config_file}")
            else:
                logger.warning(f"Plik konfiguracyjny Discord nie istnieje: {config_file}")
                logger.info("Tworzenie domyślnego pliku konfiguracyjnego...")
                
                # Utwórz katalog, jeśli nie istnieje
                os.makedirs(os.path.dirname(config_file), exist_ok=True)
                
                # Zapisz domyślną konfigurację
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4)
        except Exception as e:
            logger.error(f"Błąd podczas ładowania konfiguracji Discord: {e}")
        
        # Utwórz katalog dla historii wiadomości, jeśli nie istnieje
        history_dir = os.path.dirname(default_config["history_file"])
        os.makedirs(history_dir, exist_ok=True)
        
        return default_config
    
    def convert(self, text, webhook_name=None, username=None, avatar_url=None, embed=False):
        """
        Konwertuje tekst na wiadomość Discord
        
        Args:
            text (str): Tekst do konwersji
            webhook_name (str): Nazwa webhooka do użycia
            username (str): Nazwa użytkownika bota
            avatar_url (str): URL do awatara bota
            embed (bool): Czy używać embeda zamiast zwykłej wiadomości
            
        Returns:
            dict: Informacje o przygotowanej wiadomości Discord
        """
        if not text:
            return {"error": "Nie podano tekstu do konwersji"}
        
        try:
            # Wybierz webhook
            webhook_url = None
            if webhook_name:
                webhook_url = self.config.get("webhooks", {}).get(webhook_name)
                if not webhook_url:
                    return {"error": f"Webhook o nazwie '{webhook_name}' nie istnieje w konfiguracji"}
            else:
                webhook_url = self.config.get("default_webhook")
                if not webhook_url:
                    return {"error": "Nie podano nazwy webhooka ani nie skonfigurowano domyślnego webhooka"}
            
            # Ustaw nazwę użytkownika i awatar
            if not username:
                username = self.config.get("default_username", "Evopy Bot")
            
            if not avatar_url:
                avatar_url = self.config.get("default_avatar_url", "")
            
            # Przygotuj wiadomość
            if embed:
                # Generuj tytuł dla embeda
                embed_title = self._generate_title(text)
                
                message = {
                    "username": username,
                    "avatar_url": avatar_url,
                    "embeds": [
                        {
                            "title": embed_title,
                            "description": text,
                            "color": 3447003,  # Niebieski kolor
                            "timestamp": datetime.now().isoformat()
                        }
                    ]
                }
            else:
                message = {
                    "content": text,
                    "username": username,
                    "avatar_url": avatar_url
                }
            
            return {
                "success": True,
                "webhook_url": webhook_url,
                "message": message,
                "webhook_name": webhook_name,
                "username": username,
                "avatar_url": avatar_url,
                "embed": embed,
                "text": text
            }
        except Exception as e:
            logger.error(f"Błąd podczas konwersji tekstu na wiadomość Discord: {e}")
            return {"error": str(e)}
    
    def _generate_title(self, text):
        """
        Generuje tytuł dla embeda na podstawie tekstu
        
        Args:
            text (str): Tekst wiadomości
            
        Returns:
            str: Wygenerowany tytuł
        """
        if not self.ollama_api:
            # Jeśli nie ma dostępu do API, użyj prostego algorytmu
            words = text.split()
            if len(words) <= 5:
                return text
            return " ".join(words[:5]) + "..."
        
        try:
            # Przygotuj prompt dla modelu
            prompt = f"""Wygeneruj krótki, zwięzły tytuł dla wiadomości Discord na podstawie poniższej treści.
Tytuł powinien mieć maksymalnie 50 znaków i oddawać główną myśl wiadomości.

Treść wiadomości:
{text[:500]}...

Tytuł:
"""
            
            # Generuj tytuł
            logger.info("Generowanie tytułu dla embeda Discord...")
            response = self.ollama_api.generate(self.model, prompt)
            
            # Ogranicz długość tytułu
            title = response.strip()
            if len(title) > 100:
                title = title[:97] + "..."
            
            return title
        except Exception as e:
            logger.error(f"Błąd podczas generowania tytułu: {e}")
            # Fallback - użyj pierwszych słów
            words = text.split()
            if len(words) <= 5:
                return text
            return " ".join(words[:5]) + "..."
    
    def send_message(self, message_data):
        """
        Wysyła wiadomość Discord
        
        Args:
            message_data (dict): Dane wiadomości z metody convert()
            
        Returns:
            dict: Wynik wysyłania wiadomości
        """
        if "error" in message_data:
            return message_data
        
        try:
            # Wyślij wiadomość do webhooka Discord
            webhook_url = message_data["webhook_url"]
            message = message_data["message"]
            
            response = requests.post(webhook_url, json=message)
            
            if response.status_code == 204:
                logger.info("Wiadomość Discord została wysłana")
                
                # Zapisz wiadomość do historii
                self._save_to_history(message_data)
                
                return {
                    "success": True,
                    "message": "Wiadomość Discord została wysłana",
                    "webhook_name": message_data.get("webhook_name"),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                error_message = f"Błąd podczas wysyłania wiadomości Discord: {response.status_code} - {response.text}"
                logger.error(error_message)
                return {"error": error_message}
        except Exception as e:
            logger.error(f"Błąd podczas wysyłania wiadomości Discord: {e}")
            return {"error": f"Błąd podczas wysyłania wiadomości Discord: {str(e)}"}
    
    def _save_to_history(self, message_data):
        """
        Zapisuje wiadomość do historii
        
        Args:
            message_data (dict): Dane wiadomości
        """
        history_file = self.config.get("history_file")
        max_history = self.config.get("max_history", 100)
        
        try:
            # Załaduj istniejącą historię
            history = []
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # Dodaj nową wiadomość
            history_entry = {
                "text": message_data.get("text"),
                "webhook_name": message_data.get("webhook_name"),
                "username": message_data.get("username"),
                "embed": message_data.get("embed"),
                "timestamp": datetime.now().isoformat()
            }
            history.append(history_entry)
            
            # Ogranicz liczbę elementów historii
            if len(history) > max_history:
                history = history[-max_history:]
            
            # Zapisz historię
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=4)
            
            logger.info(f"Wiadomość została zapisana do historii: {history_file}")
        except Exception as e:
            logger.error(f"Błąd podczas zapisywania wiadomości do historii: {e}")
    
    def get_history(self, limit=None):
        """
        Pobiera historię wiadomości
        
        Args:
            limit (int): Maksymalna liczba wiadomości do pobrania
            
        Returns:
            list: Lista wiadomości
        """
        history_file = self.config.get("history_file")
        
        try:
            if not os.path.exists(history_file):
                return []
            
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            # Ogranicz liczbę elementów, jeśli podano limit
            if limit and limit > 0:
                history = history[-limit:]
            
            return history
        except Exception as e:
            logger.error(f"Błąd podczas pobierania historii wiadomości: {e}")
            return []
    
    def clear_history(self):
        """
        Czyści historię wiadomości
        
        Returns:
            bool: True jeśli wyczyszczono pomyślnie, False w przeciwnym razie
        """
        history_file = self.config.get("history_file")
        
        try:
            if os.path.exists(history_file):
                with open(history_file, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                
                logger.info("Historia wiadomości została wyczyszczona")
                return True
            return False
        except Exception as e:
            logger.error(f"Błąd podczas czyszczenia historii wiadomości: {e}")
            return False
    
    def add_webhook(self, name, url):
        """
        Dodaje nowy webhook do konfiguracji
        
        Args:
            name (str): Nazwa webhooka
            url (str): URL webhooka
            
        Returns:
            bool: True jeśli dodano pomyślnie, False w przeciwnym razie
        """
        try:
            # Dodaj webhook do konfiguracji
            self.config["webhooks"][name] = url
            
            # Zapisz konfigurację
            config_file = PROJECT_ROOT / "config" / "discord_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            
            logger.info(f"Webhook '{name}' został dodany do konfiguracji")
            return True
        except Exception as e:
            logger.error(f"Błąd podczas dodawania webhooka: {e}")
            return False
    
    def remove_webhook(self, name):
        """
        Usuwa webhook z konfiguracji
        
        Args:
            name (str): Nazwa webhooka
            
        Returns:
            bool: True jeśli usunięto pomyślnie, False w przeciwnym razie
        """
        try:
            # Sprawdź, czy webhook istnieje
            if name not in self.config["webhooks"]:
                logger.warning(f"Webhook '{name}' nie istnieje w konfiguracji")
                return False
            
            # Usuń webhook z konfiguracji
            del self.config["webhooks"][name]
            
            # Zapisz konfigurację
            config_file = PROJECT_ROOT / "config" / "discord_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            
            logger.info(f"Webhook '{name}' został usunięty z konfiguracji")
            return True
        except Exception as e:
            logger.error(f"Błąd podczas usuwania webhooka: {e}")
            return False
    
    def set_default_webhook(self, name):
        """
        Ustawia domyślny webhook
        
        Args:
            name (str): Nazwa webhooka
            
        Returns:
            bool: True jeśli ustawiono pomyślnie, False w przeciwnym razie
        """
        try:
            # Sprawdź, czy webhook istnieje
            if name not in self.config["webhooks"]:
                logger.warning(f"Webhook '{name}' nie istnieje w konfiguracji")
                return False
            
            # Ustaw domyślny webhook
            self.config["default_webhook"] = self.config["webhooks"][name]
            
            # Zapisz konfigurację
            config_file = PROJECT_ROOT / "config" / "discord_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            
            logger.info(f"Webhook '{name}' został ustawiony jako domyślny")
            return True
        except Exception as e:
            logger.error(f"Błąd podczas ustawiania domyślnego webhooka: {e}")
            return False
    
    def list_webhooks(self):
        """
        Zwraca listę dostępnych webhooków
        
        Returns:
            dict: Słownik z nazwami webhooków jako kluczami i URL jako wartościami
        """
        return self.config.get("webhooks", {})

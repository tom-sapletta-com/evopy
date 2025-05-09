#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł konwersji tekstu na wiadomości Telegram (Text-to-Telegram)
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
logger = logging.getLogger('text2telegram')

# Dodaj katalog główny projektu do ścieżki Pythona
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importuj moduł ollama_api
try:
    from ollama_api import OllamaAPI
except ImportError:
    logger.error("Nie można zaimportować modułu ollama_api. Upewnij się, że jest zainstalowany.")
    OllamaAPI = None

class Text2Telegram:
    """Klasa konwertująca tekst na wiadomości Telegram"""
    
    def __init__(self, model="llama3", config_file=None):
        """
        Inicjalizacja konwertera text2telegram
        
        Args:
            model (str): Model LLM do generowania tekstu
            config_file (str): Ścieżka do pliku konfiguracyjnego Telegram
        """
        self.model = model
        self.ollama_api = OllamaAPI() if OllamaAPI else None
        
        # Załaduj konfigurację Telegram
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
        Ładuje konfigurację Telegram z pliku
        
        Args:
            config_file (str): Ścieżka do pliku konfiguracyjnego
            
        Returns:
            dict: Konfiguracja Telegram
        """
        default_config = {
            "bot_token": "",
            "chat_ids": {},
            "default_chat_id": "",
            "history_file": str(PROJECT_ROOT / "history" / "telegram_messages.json"),
            "max_history": 100
        }
        
        if not config_file:
            config_file = PROJECT_ROOT / "config" / "telegram_config.json"
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Aktualizuj domyślną konfigurację załadowanymi wartościami
                    default_config.update(loaded_config)
                    logger.info(f"Załadowano konfigurację Telegram z pliku: {config_file}")
            else:
                logger.warning(f"Plik konfiguracyjny Telegram nie istnieje: {config_file}")
                logger.info("Tworzenie domyślnego pliku konfiguracyjnego...")
                
                # Utwórz katalog, jeśli nie istnieje
                os.makedirs(os.path.dirname(config_file), exist_ok=True)
                
                # Zapisz domyślną konfigurację
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4)
        except Exception as e:
            logger.error(f"Błąd podczas ładowania konfiguracji Telegram: {e}")
        
        # Utwórz katalog dla historii wiadomości, jeśli nie istnieje
        history_dir = os.path.dirname(default_config["history_file"])
        os.makedirs(history_dir, exist_ok=True)
        
        return default_config
    
    def convert(self, text, chat_name=None, parse_mode=None, disable_notification=False):
        """
        Konwertuje tekst na wiadomość Telegram
        
        Args:
            text (str): Tekst do konwersji
            chat_name (str): Nazwa czatu do użycia
            parse_mode (str): Tryb parsowania (Markdown, HTML)
            disable_notification (bool): Czy wyłączyć powiadomienia
            
        Returns:
            dict: Informacje o przygotowanej wiadomości Telegram
        """
        if not text:
            return {"error": "Nie podano tekstu do konwersji"}
        
        try:
            # Sprawdź, czy token bota jest skonfigurowany
            bot_token = self.config.get("bot_token")
            if not bot_token:
                return {"error": "Brak skonfigurowanego tokenu bota Telegram"}
            
            # Wybierz chat_id
            chat_id = None
            if chat_name:
                chat_id = self.config.get("chat_ids", {}).get(chat_name)
                if not chat_id:
                    return {"error": f"Czat o nazwie '{chat_name}' nie istnieje w konfiguracji"}
            else:
                chat_id = self.config.get("default_chat_id")
                if not chat_id:
                    return {"error": "Nie podano nazwy czatu ani nie skonfigurowano domyślnego czatu"}
            
            # Ustaw tryb parsowania
            if not parse_mode:
                parse_mode = "HTML"  # Domyślny tryb parsowania
            
            # Przygotuj wiadomość
            message = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode,
                "disable_notification": disable_notification
            }
            
            return {
                "success": True,
                "bot_token": bot_token,
                "message": message,
                "chat_name": chat_name,
                "chat_id": chat_id,
                "parse_mode": parse_mode,
                "disable_notification": disable_notification,
                "text": text
            }
        except Exception as e:
            logger.error(f"Błąd podczas konwersji tekstu na wiadomość Telegram: {e}")
            return {"error": str(e)}
    
    def send_message(self, message_data):
        """
        Wysyła wiadomość Telegram
        
        Args:
            message_data (dict): Dane wiadomości z metody convert()
            
        Returns:
            dict: Wynik wysyłania wiadomości
        """
        if "error" in message_data:
            return message_data
        
        try:
            # Wyślij wiadomość do API Telegram
            bot_token = message_data["bot_token"]
            message = message_data["message"]
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            response = requests.post(url, json=message)
            
            if response.status_code == 200:
                logger.info("Wiadomość Telegram została wysłana")
                
                # Zapisz wiadomość do historii
                self._save_to_history(message_data)
                
                return {
                    "success": True,
                    "message": "Wiadomość Telegram została wysłana",
                    "chat_name": message_data.get("chat_name"),
                    "chat_id": message_data.get("chat_id"),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                error_message = f"Błąd podczas wysyłania wiadomości Telegram: {response.status_code} - {response.text}"
                logger.error(error_message)
                return {"error": error_message}
        except Exception as e:
            logger.error(f"Błąd podczas wysyłania wiadomości Telegram: {e}")
            return {"error": f"Błąd podczas wysyłania wiadomości Telegram: {str(e)}"}
    
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
                "chat_name": message_data.get("chat_name"),
                "chat_id": message_data.get("chat_id"),
                "parse_mode": message_data.get("parse_mode"),
                "disable_notification": message_data.get("disable_notification"),
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
    
    def add_chat(self, name, chat_id):
        """
        Dodaje nowy czat do konfiguracji
        
        Args:
            name (str): Nazwa czatu
            chat_id (str): ID czatu
            
        Returns:
            bool: True jeśli dodano pomyślnie, False w przeciwnym razie
        """
        try:
            # Dodaj czat do konfiguracji
            self.config["chat_ids"][name] = chat_id
            
            # Zapisz konfigurację
            config_file = PROJECT_ROOT / "config" / "telegram_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            
            logger.info(f"Czat '{name}' został dodany do konfiguracji")
            return True
        except Exception as e:
            logger.error(f"Błąd podczas dodawania czatu: {e}")
            return False
    
    def remove_chat(self, name):
        """
        Usuwa czat z konfiguracji
        
        Args:
            name (str): Nazwa czatu
            
        Returns:
            bool: True jeśli usunięto pomyślnie, False w przeciwnym razie
        """
        try:
            # Sprawdź, czy czat istnieje
            if name not in self.config["chat_ids"]:
                logger.warning(f"Czat '{name}' nie istnieje w konfiguracji")
                return False
            
            # Usuń czat z konfiguracji
            del self.config["chat_ids"][name]
            
            # Zapisz konfigurację
            config_file = PROJECT_ROOT / "config" / "telegram_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            
            logger.info(f"Czat '{name}' został usunięty z konfiguracji")
            return True
        except Exception as e:
            logger.error(f"Błąd podczas usuwania czatu: {e}")
            return False
    
    def set_default_chat(self, name):
        """
        Ustawia domyślny czat
        
        Args:
            name (str): Nazwa czatu
            
        Returns:
            bool: True jeśli ustawiono pomyślnie, False w przeciwnym razie
        """
        try:
            # Sprawdź, czy czat istnieje
            if name not in self.config["chat_ids"]:
                logger.warning(f"Czat '{name}' nie istnieje w konfiguracji")
                return False
            
            # Ustaw domyślny czat
            self.config["default_chat_id"] = self.config["chat_ids"][name]
            
            # Zapisz konfigurację
            config_file = PROJECT_ROOT / "config" / "telegram_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            
            logger.info(f"Czat '{name}' został ustawiony jako domyślny")
            return True
        except Exception as e:
            logger.error(f"Błąd podczas ustawiania domyślnego czatu: {e}")
            return False
    
    def set_bot_token(self, token):
        """
        Ustawia token bota Telegram
        
        Args:
            token (str): Token bota
            
        Returns:
            bool: True jeśli ustawiono pomyślnie, False w przeciwnym razie
        """
        try:
            # Ustaw token bota
            self.config["bot_token"] = token
            
            # Zapisz konfigurację
            config_file = PROJECT_ROOT / "config" / "telegram_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            
            logger.info("Token bota Telegram został ustawiony")
            return True
        except Exception as e:
            logger.error(f"Błąd podczas ustawiania tokenu bota: {e}")
            return False
    
    def list_chats(self):
        """
        Zwraca listę dostępnych czatów
        
        Returns:
            dict: Słownik z nazwami czatów jako kluczami i ID czatów jako wartościami
        """
        return self.config.get("chat_ids", {})
    
    def send_photo(self, chat_name, photo_path, caption=None, parse_mode=None, disable_notification=False):
        """
        Wysyła zdjęcie do czatu Telegram
        
        Args:
            chat_name (str): Nazwa czatu
            photo_path (str): Ścieżka do pliku zdjęcia
            caption (str): Podpis zdjęcia
            parse_mode (str): Tryb parsowania podpisu
            disable_notification (bool): Czy wyłączyć powiadomienia
            
        Returns:
            dict: Wynik wysyłania zdjęcia
        """
        try:
            # Sprawdź, czy token bota jest skonfigurowany
            bot_token = self.config.get("bot_token")
            if not bot_token:
                return {"error": "Brak skonfigurowanego tokenu bota Telegram"}
            
            # Wybierz chat_id
            chat_id = None
            if chat_name:
                chat_id = self.config.get("chat_ids", {}).get(chat_name)
                if not chat_id:
                    return {"error": f"Czat o nazwie '{chat_name}' nie istnieje w konfiguracji"}
            else:
                chat_id = self.config.get("default_chat_id")
                if not chat_id:
                    return {"error": "Nie podano nazwy czatu ani nie skonfigurowano domyślnego czatu"}
            
            # Sprawdź, czy plik istnieje
            if not os.path.exists(photo_path):
                return {"error": f"Plik zdjęcia nie istnieje: {photo_path}"}
            
            # Ustaw tryb parsowania
            if not parse_mode:
                parse_mode = "HTML"  # Domyślny tryb parsowania
            
            # Przygotuj dane
            url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            data = {
                "chat_id": chat_id,
                "parse_mode": parse_mode,
                "disable_notification": disable_notification
            }
            
            if caption:
                data["caption"] = caption
            
            # Otwórz plik zdjęcia
            with open(photo_path, "rb") as photo_file:
                files = {"photo": photo_file}
                response = requests.post(url, data=data, files=files)
            
            if response.status_code == 200:
                logger.info("Zdjęcie zostało wysłane")
                
                return {
                    "success": True,
                    "message": "Zdjęcie zostało wysłane",
                    "chat_name": chat_name,
                    "chat_id": chat_id,
                    "photo_path": photo_path,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                error_message = f"Błąd podczas wysyłania zdjęcia: {response.status_code} - {response.text}"
                logger.error(error_message)
                return {"error": error_message}
        except Exception as e:
            logger.error(f"Błąd podczas wysyłania zdjęcia: {e}")
            return {"error": f"Błąd podczas wysyłania zdjęcia: {str(e)}"}
    
    def send_document(self, chat_name, document_path, caption=None, parse_mode=None, disable_notification=False):
        """
        Wysyła dokument do czatu Telegram
        
        Args:
            chat_name (str): Nazwa czatu
            document_path (str): Ścieżka do pliku dokumentu
            caption (str): Podpis dokumentu
            parse_mode (str): Tryb parsowania podpisu
            disable_notification (bool): Czy wyłączyć powiadomienia
            
        Returns:
            dict: Wynik wysyłania dokumentu
        """
        try:
            # Sprawdź, czy token bota jest skonfigurowany
            bot_token = self.config.get("bot_token")
            if not bot_token:
                return {"error": "Brak skonfigurowanego tokenu bota Telegram"}
            
            # Wybierz chat_id
            chat_id = None
            if chat_name:
                chat_id = self.config.get("chat_ids", {}).get(chat_name)
                if not chat_id:
                    return {"error": f"Czat o nazwie '{chat_name}' nie istnieje w konfiguracji"}
            else:
                chat_id = self.config.get("default_chat_id")
                if not chat_id:
                    return {"error": "Nie podano nazwy czatu ani nie skonfigurowano domyślnego czatu"}
            
            # Sprawdź, czy plik istnieje
            if not os.path.exists(document_path):
                return {"error": f"Plik dokumentu nie istnieje: {document_path}"}
            
            # Ustaw tryb parsowania
            if not parse_mode:
                parse_mode = "HTML"  # Domyślny tryb parsowania
            
            # Przygotuj dane
            url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
            data = {
                "chat_id": chat_id,
                "parse_mode": parse_mode,
                "disable_notification": disable_notification
            }
            
            if caption:
                data["caption"] = caption
            
            # Otwórz plik dokumentu
            with open(document_path, "rb") as document_file:
                files = {"document": document_file}
                response = requests.post(url, data=data, files=files)
            
            if response.status_code == 200:
                logger.info("Dokument został wysłany")
                
                return {
                    "success": True,
                    "message": "Dokument został wysłany",
                    "chat_name": chat_name,
                    "chat_id": chat_id,
                    "document_path": document_path,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                error_message = f"Błąd podczas wysyłania dokumentu: {response.status_code} - {response.text}"
                logger.error(error_message)
                return {"error": error_message}
        except Exception as e:
            logger.error(f"Błąd podczas wysyłania dokumentu: {e}")
            return {"error": f"Błąd podczas wysyłania dokumentu: {str(e)}"}

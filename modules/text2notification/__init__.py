#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł konwersji tekstu na powiadomienia systemowe (Text-to-Notification)
"""

import os
import sys
import logging
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('text2notification')

# Dodaj katalog główny projektu do ścieżki Pythona
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importuj moduł ollama_api
try:
    from ollama_api import OllamaAPI
except ImportError:
    logger.error("Nie można zaimportować modułu ollama_api. Upewnij się, że jest zainstalowany.")
    OllamaAPI = None

class Text2Notification:
    """Klasa konwertująca tekst na powiadomienia systemowe"""
    
    def __init__(self, model="llama3", config_file=None):
        """
        Inicjalizacja konwertera text2notification
        
        Args:
            model (str): Model LLM do generowania tekstu
            config_file (str): Ścieżka do pliku konfiguracyjnego powiadomień
        """
        self.model = model
        self.ollama_api = OllamaAPI() if OllamaAPI else None
        
        # Załaduj konfigurację powiadomień
        self.config = self._load_config(config_file)
        
        # Sprawdź dostępność modelu
        if self.ollama_api:
            logger.info(f"Sprawdzanie dostępności modelu {model}...")
            if self.ollama_api.check_model_exists(model):
                logger.info(f"Model {model} jest dostępny")
            else:
                logger.warning(f"Model {model} nie jest dostępny. Spróbuj pobrać go za pomocą 'ollama pull {model}'")
        
        # Sprawdź dostępność narzędzi do powiadomień
        self._check_notification_tools()
    
    def _load_config(self, config_file=None):
        """
        Ładuje konfigurację powiadomień z pliku
        
        Args:
            config_file (str): Ścieżka do pliku konfiguracyjnego
            
        Returns:
            dict: Konfiguracja powiadomień
        """
        default_config = {
            "default_icon": str(PROJECT_ROOT / "assets" / "icons" / "evopy.png"),
            "default_timeout": 5000,  # ms
            "default_urgency": "normal",  # low, normal, critical
            "history_file": str(PROJECT_ROOT / "history" / "notifications.json"),
            "max_history": 100
        }
        
        if not config_file:
            config_file = PROJECT_ROOT / "config" / "notification_config.json"
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Aktualizuj domyślną konfigurację załadowanymi wartościami
                    default_config.update(loaded_config)
                    logger.info(f"Załadowano konfigurację powiadomień z pliku: {config_file}")
            else:
                logger.warning(f"Plik konfiguracyjny powiadomień nie istnieje: {config_file}")
                logger.info("Tworzenie domyślnego pliku konfiguracyjnego...")
                
                # Utwórz katalog, jeśli nie istnieje
                os.makedirs(os.path.dirname(config_file), exist_ok=True)
                
                # Zapisz domyślną konfigurację
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4)
        except Exception as e:
            logger.error(f"Błąd podczas ładowania konfiguracji powiadomień: {e}")
        
        # Utwórz katalog dla ikon, jeśli nie istnieje
        icon_dir = os.path.dirname(default_config["default_icon"])
        os.makedirs(icon_dir, exist_ok=True)
        
        # Utwórz katalog dla historii powiadomień, jeśli nie istnieje
        history_dir = os.path.dirname(default_config["history_file"])
        os.makedirs(history_dir, exist_ok=True)
        
        return default_config
    
    def _check_notification_tools(self):
        """Sprawdza dostępność narzędzi do powiadomień"""
        self.notification_tools = {
            "linux": {
                "notify-send": self._check_command("notify-send"),
                "zenity": self._check_command("zenity")
            },
            "darwin": {
                "osascript": self._check_command("osascript"),
                "terminal-notifier": self._check_command("terminal-notifier")
            },
            "windows": {
                "powershell": self._check_command("powershell")
            }
        }
        
        # Sprawdź, czy są dostępne jakiekolwiek narzędzia
        system = self._get_system()
        if not any(self.notification_tools[system].values()):
            logger.warning(f"Brak dostępnych narzędzi do powiadomień dla systemu {system}")
            
            # Sugestie instalacji
            if system == "linux":
                logger.info("Zainstaluj 'libnotify-bin' lub 'zenity' aby korzystać z powiadomień")
            elif system == "darwin":
                logger.info("Zainstaluj 'terminal-notifier' aby korzystać z powiadomień")
    
    def _check_command(self, command):
        """
        Sprawdza, czy komenda jest dostępna w systemie
        
        Args:
            command (str): Nazwa komendy
            
        Returns:
            bool: True jeśli komenda jest dostępna, False w przeciwnym razie
        """
        try:
            # Użyj 'where' na Windows, 'which' na innych systemach
            if sys.platform == "win32":
                result = subprocess.run(["where", command], capture_output=True, text=True)
            else:
                result = subprocess.run(["which", command], capture_output=True, text=True)
            
            return result.returncode == 0
        except Exception:
            return False
    
    def _get_system(self):
        """
        Zwraca nazwę systemu operacyjnego
        
        Returns:
            str: Nazwa systemu (linux, darwin, windows)
        """
        if sys.platform.startswith("linux"):
            return "linux"
        elif sys.platform == "darwin":
            return "darwin"
        elif sys.platform == "win32":
            return "windows"
        else:
            return "unknown"
    
    def convert(self, text, title=None, icon=None, urgency=None, timeout=None):
        """
        Konwertuje tekst na powiadomienie systemowe
        
        Args:
            text (str): Tekst do konwersji
            title (str): Tytuł powiadomienia
            icon (str): Ścieżka do ikony
            urgency (str): Priorytet powiadomienia (low, normal, critical)
            timeout (int): Czas wyświetlania powiadomienia w ms
            
        Returns:
            dict: Informacje o przygotowanym powiadomieniu
        """
        if not text:
            return {"error": "Nie podano tekstu do konwersji"}
        
        try:
            # Przygotuj tytuł powiadomienia, jeśli nie został podany
            if not title:
                title = self._generate_title(text)
            
            # Ustaw domyślne wartości, jeśli nie zostały podane
            if not icon:
                icon = self.config.get("default_icon")
            
            if not urgency:
                urgency = self.config.get("default_urgency", "normal")
            
            if not timeout:
                timeout = self.config.get("default_timeout", 5000)
            
            # Przygotuj powiadomienie
            notification = {
                "title": title,
                "text": text,
                "icon": icon,
                "urgency": urgency,
                "timeout": timeout,
                "timestamp": datetime.now().isoformat()
            }
            
            return notification
        except Exception as e:
            logger.error(f"Błąd podczas konwersji tekstu na powiadomienie: {e}")
            return {"error": str(e)}
    
    def _generate_title(self, text):
        """
        Generuje tytuł powiadomienia na podstawie tekstu
        
        Args:
            text (str): Tekst powiadomienia
            
        Returns:
            str: Wygenerowany tytuł
        """
        if not self.ollama_api:
            # Jeśli nie ma dostępu do API, użyj prostego algorytmu
            words = text.split()
            if len(words) <= 3:
                return text
            return " ".join(words[:3]) + "..."
        
        try:
            # Przygotuj prompt dla modelu
            prompt = f"""Wygeneruj krótki, zwięzły tytuł powiadomienia na podstawie poniższej treści.
Tytuł powinien mieć maksymalnie 30 znaków i oddawać główną myśl powiadomienia.

Treść powiadomienia:
{text[:200]}...

Tytuł:
"""
            
            # Generuj tytuł
            logger.info("Generowanie tytułu powiadomienia...")
            response = self.ollama_api.generate(self.model, prompt)
            
            # Ogranicz długość tytułu
            title = response.strip()
            if len(title) > 50:
                title = title[:47] + "..."
            
            return title
        except Exception as e:
            logger.error(f"Błąd podczas generowania tytułu: {e}")
            # Fallback - użyj pierwszych słów
            words = text.split()
            if len(words) <= 3:
                return text
            return " ".join(words[:3]) + "..."
    
    def send_notification(self, notification_data):
        """
        Wysyła powiadomienie systemowe
        
        Args:
            notification_data (dict): Dane powiadomienia z metody convert()
            
        Returns:
            dict: Wynik wysyłania powiadomienia
        """
        if "error" in notification_data:
            return notification_data
        
        system = self._get_system()
        
        try:
            # Wybierz odpowiednią metodę dla systemu operacyjnego
            if system == "linux":
                result = self._send_linux_notification(notification_data)
            elif system == "darwin":
                result = self._send_macos_notification(notification_data)
            elif system == "windows":
                result = self._send_windows_notification(notification_data)
            else:
                return {"error": f"Nieobsługiwany system operacyjny: {system}"}
            
            # Zapisz powiadomienie do historii
            self._save_to_history(notification_data)
            
            return result
        except Exception as e:
            logger.error(f"Błąd podczas wysyłania powiadomienia: {e}")
            return {"error": f"Błąd podczas wysyłania powiadomienia: {str(e)}"}
    
    def _send_linux_notification(self, notification):
        """
        Wysyła powiadomienie w systemie Linux
        
        Args:
            notification (dict): Dane powiadomienia
            
        Returns:
            dict: Wynik wysyłania powiadomienia
        """
        # Preferuj notify-send, jeśli jest dostępny
        if self.notification_tools["linux"]["notify-send"]:
            cmd = [
                "notify-send",
                "--app-name=Evopy",
                f"--urgency={notification['urgency']}",
                f"--expire-time={notification['timeout']}",
            ]
            
            if notification["icon"] and os.path.exists(notification["icon"]):
                cmd.append(f"--icon={notification['icon']}")
            
            cmd.extend([notification["title"], notification["text"]])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Powiadomienie zostało wysłane (notify-send)")
                return {"success": True, "method": "notify-send"}
            else:
                logger.error(f"Błąd podczas wysyłania powiadomienia: {result.stderr}")
        
        # Spróbuj użyć zenity, jeśli jest dostępny
        if self.notification_tools["linux"]["zenity"]:
            cmd = [
                "zenity",
                "--notification",
                f"--text={notification['title']}: {notification['text']}"
            ]
            
            if notification["icon"] and os.path.exists(notification["icon"]):
                cmd.append(f"--window-icon={notification['icon']}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Powiadomienie zostało wysłane (zenity)")
                return {"success": True, "method": "zenity"}
            else:
                logger.error(f"Błąd podczas wysyłania powiadomienia: {result.stderr}")
        
        return {"error": "Brak dostępnych narzędzi do wysyłania powiadomień w systemie Linux"}
    
    def _send_macos_notification(self, notification):
        """
        Wysyła powiadomienie w systemie macOS
        
        Args:
            notification (dict): Dane powiadomienia
            
        Returns:
            dict: Wynik wysyłania powiadomienia
        """
        # Preferuj terminal-notifier, jeśli jest dostępny
        if self.notification_tools["darwin"]["terminal-notifier"]:
            cmd = [
                "terminal-notifier",
                "-title", "Evopy",
                "-subtitle", notification["title"],
                "-message", notification["text"],
                "-group", "com.evopy.notification"
            ]
            
            if notification["icon"] and os.path.exists(notification["icon"]):
                cmd.extend(["-appIcon", notification["icon"]])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Powiadomienie zostało wysłane (terminal-notifier)")
                return {"success": True, "method": "terminal-notifier"}
            else:
                logger.error(f"Błąd podczas wysyłania powiadomienia: {result.stderr}")
        
        # Spróbuj użyć osascript, jeśli jest dostępny
        if self.notification_tools["darwin"]["osascript"]:
            script = f'''
            display notification "{notification['text']}" with title "Evopy" subtitle "{notification['title']}"
            '''
            
            cmd = ["osascript", "-e", script]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Powiadomienie zostało wysłane (osascript)")
                return {"success": True, "method": "osascript"}
            else:
                logger.error(f"Błąd podczas wysyłania powiadomienia: {result.stderr}")
        
        return {"error": "Brak dostępnych narzędzi do wysyłania powiadomień w systemie macOS"}
    
    def _send_windows_notification(self, notification):
        """
        Wysyła powiadomienie w systemie Windows
        
        Args:
            notification (dict): Dane powiadomienia
            
        Returns:
            dict: Wynik wysyłania powiadomienia
        """
        if self.notification_tools["windows"]["powershell"]:
            # Skrypt PowerShell do wyświetlenia powiadomienia
            script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

            $app_id = 'Evopy'
            $title = '{notification["title"]}'
            $message = '{notification["text"]}'

            $template = @"
            <toast>
                <visual>
                    <binding template="ToastText02">
                        <text id="1">$title</text>
                        <text id="2">$message</text>
                    </binding>
                </visual>
            </toast>
            "@

            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($app_id).Show($toast)
            '''
            
            # Zapisz skrypt do pliku tymczasowego
            with tempfile.NamedTemporaryFile(suffix=".ps1", delete=False) as temp:
                temp.write(script.encode('utf-8'))
                temp_path = temp.name
            
            try:
                # Uruchom skrypt PowerShell
                cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", temp_path]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info("Powiadomienie zostało wysłane (PowerShell)")
                    return {"success": True, "method": "powershell"}
                else:
                    logger.error(f"Błąd podczas wysyłania powiadomienia: {result.stderr}")
            finally:
                # Usuń plik tymczasowy
                os.unlink(temp_path)
        
        return {"error": "Brak dostępnych narzędzi do wysyłania powiadomień w systemie Windows"}
    
    def _save_to_history(self, notification):
        """
        Zapisuje powiadomienie do historii
        
        Args:
            notification (dict): Dane powiadomienia
        """
        history_file = self.config.get("history_file")
        max_history = self.config.get("max_history", 100)
        
        try:
            # Załaduj istniejącą historię
            history = []
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # Dodaj nowe powiadomienie
            history.append(notification)
            
            # Ogranicz liczbę elementów historii
            if len(history) > max_history:
                history = history[-max_history:]
            
            # Zapisz historię
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=4)
            
            logger.info(f"Powiadomienie zostało zapisane do historii: {history_file}")
        except Exception as e:
            logger.error(f"Błąd podczas zapisywania powiadomienia do historii: {e}")
    
    def get_history(self, limit=None):
        """
        Pobiera historię powiadomień
        
        Args:
            limit (int): Maksymalna liczba powiadomień do pobrania
            
        Returns:
            list: Lista powiadomień
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
            logger.error(f"Błąd podczas pobierania historii powiadomień: {e}")
            return []
    
    def clear_history(self):
        """
        Czyści historię powiadomień
        
        Returns:
            bool: True jeśli wyczyszczono pomyślnie, False w przeciwnym razie
        """
        history_file = self.config.get("history_file")
        
        try:
            if os.path.exists(history_file):
                with open(history_file, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                
                logger.info("Historia powiadomień została wyczyszczona")
                return True
            return False
        except Exception as e:
            logger.error(f"Błąd podczas czyszczenia historii powiadomień: {e}")
            return False

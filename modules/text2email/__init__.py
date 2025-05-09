#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł konwersji tekstu na wiadomości email (Text-to-Email)
"""

import os
import sys
import logging
import json
import smtplib
import ssl
import tempfile
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('text2email')

# Dodaj katalog główny projektu do ścieżki Pythona
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importuj moduł ollama_api
try:
    from ollama_api import OllamaAPI
except ImportError:
    logger.error("Nie można zaimportować modułu ollama_api. Upewnij się, że jest zainstalowany.")
    OllamaAPI = None

class Text2Email:
    """Klasa konwertująca tekst na wiadomości email"""
    
    def __init__(self, model="llama3", config_file=None):
        """
        Inicjalizacja konwertera text2email
        
        Args:
            model (str): Model LLM do generowania tekstu
            config_file (str): Ścieżka do pliku konfiguracyjnego SMTP
        """
        self.model = model
        self.ollama_api = OllamaAPI() if OllamaAPI else None
        
        # Załaduj konfigurację SMTP
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
        Ładuje konfigurację SMTP z pliku
        
        Args:
            config_file (str): Ścieżka do pliku konfiguracyjnego
            
        Returns:
            dict: Konfiguracja SMTP
        """
        default_config = {
            "smtp_server": "",
            "smtp_port": 587,
            "smtp_username": "",
            "smtp_password": "",
            "default_sender": "",
            "use_tls": True,
            "signature": "Wiadomość wygenerowana przez Evopy Assistant",
            "templates_dir": str(PROJECT_ROOT / "templates" / "email")
        }
        
        if not config_file:
            config_file = PROJECT_ROOT / "config" / "email_config.json"
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Aktualizuj domyślną konfigurację załadowanymi wartościami
                    default_config.update(loaded_config)
                    logger.info(f"Załadowano konfigurację SMTP z pliku: {config_file}")
            else:
                logger.warning(f"Plik konfiguracyjny SMTP nie istnieje: {config_file}")
                logger.info("Tworzenie domyślnego pliku konfiguracyjnego...")
                
                # Utwórz katalog, jeśli nie istnieje
                os.makedirs(os.path.dirname(config_file), exist_ok=True)
                
                # Zapisz domyślną konfigurację
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4)
        except Exception as e:
            logger.error(f"Błąd podczas ładowania konfiguracji SMTP: {e}")
        
        # Utwórz katalog na szablony, jeśli nie istnieje
        os.makedirs(default_config["templates_dir"], exist_ok=True)
        
        return default_config
    
    def convert(self, text, recipient=None, subject=None, sender=None, attachments=None):
        """
        Konwertuje tekst na wiadomość email i przygotowuje ją do wysłania
        
        Args:
            text (str): Tekst do konwersji
            recipient (str): Adres email odbiorcy
            subject (str): Temat wiadomości
            sender (str): Adres email nadawcy
            attachments (list): Lista ścieżek do załączników
            
        Returns:
            dict: Informacje o przygotowanej wiadomości email
        """
        if not text:
            return {"error": "Nie podano tekstu do konwersji"}
        
        # Jeśli nie podano odbiorcy, wymagaj go
        if not recipient:
            return {"error": "Nie podano adresu email odbiorcy"}
        
        try:
            # Przygotuj temat wiadomości, jeśli nie został podany
            if not subject:
                subject = self._generate_subject(text)
            
            # Przygotuj treść wiadomości
            email_body = self._format_email_body(text)
            
            # Przygotuj nadawcę
            if not sender:
                sender = self.config.get("default_sender", "")
                if not sender:
                    return {"error": "Nie podano adresu email nadawcy ani nie skonfigurowano domyślnego nadawcy"}
            
            # Przygotuj wiadomość email
            message = self._create_email_message(sender, recipient, subject, email_body, attachments)
            
            return {
                "success": True,
                "message": message,
                "sender": sender,
                "recipient": recipient,
                "subject": subject,
                "body": email_body,
                "attachments": attachments or []
            }
        except Exception as e:
            logger.error(f"Błąd podczas konwersji tekstu na wiadomość email: {e}")
            return {"error": str(e)}
    
    def _generate_subject(self, text):
        """
        Generuje temat wiadomości na podstawie tekstu
        
        Args:
            text (str): Tekst wiadomości
            
        Returns:
            str: Wygenerowany temat
        """
        if not self.ollama_api:
            # Jeśli nie ma dostępu do API, użyj prostego algorytmu
            words = text.split()
            if len(words) <= 5:
                return text
            return " ".join(words[:5]) + "..."
        
        try:
            # Przygotuj prompt dla modelu
            prompt = f"""Wygeneruj krótki, zwięzły temat wiadomości email na podstawie poniższej treści.
Temat powinien mieć maksymalnie 50 znaków i oddawać główną myśl wiadomości.

Treść wiadomości:
{text[:500]}...

Temat:
"""
            
            # Generuj temat
            logger.info("Generowanie tematu wiadomości email...")
            response = self.ollama_api.generate(self.model, prompt)
            
            # Ogranicz długość tematu
            subject = response.strip()
            if len(subject) > 100:
                subject = subject[:97] + "..."
            
            return subject
        except Exception as e:
            logger.error(f"Błąd podczas generowania tematu: {e}")
            # Fallback - użyj pierwszych słów
            words = text.split()
            if len(words) <= 5:
                return text
            return " ".join(words[:5]) + "..."
    
    def _format_email_body(self, text):
        """
        Formatuje treść wiadomości email
        
        Args:
            text (str): Tekst do sformatowania
            
        Returns:
            str: Sformatowana treść wiadomości
        """
        # Dodaj podstawowe formatowanie HTML
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #777; }}
    </style>
</head>
<body>
    <div class="container">
        {text.replace('\n', '<br>')}
        
        <div class="footer">
            <p>{self.config.get('signature', '')}</p>
        </div>
    </div>
</body>
</html>
"""
        return html_body
    
    def _create_email_message(self, sender, recipient, subject, body, attachments=None):
        """
        Tworzy wiadomość email
        
        Args:
            sender (str): Adres email nadawcy
            recipient (str): Adres email odbiorcy
            subject (str): Temat wiadomości
            body (str): Treść wiadomości
            attachments (list): Lista ścieżek do załączników
            
        Returns:
            MIMEMultipart: Wiadomość email
        """
        # Utwórz wiadomość
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender
        message["To"] = recipient
        
        # Dodaj treść HTML
        html_part = MIMEText(body, "html")
        message.attach(html_part)
        
        # Dodaj załączniki
        if attachments:
            for attachment_path in attachments:
                try:
                    with open(attachment_path, "rb") as file:
                        attachment = MIMEApplication(file.read())
                        attachment_name = os.path.basename(attachment_path)
                        attachment.add_header(
                            "Content-Disposition", 
                            f"attachment; filename={attachment_name}"
                        )
                        message.attach(attachment)
                except Exception as e:
                    logger.error(f"Błąd podczas dodawania załącznika {attachment_path}: {e}")
        
        return message
    
    def send_email(self, email_data):
        """
        Wysyła wiadomość email
        
        Args:
            email_data (dict): Dane wiadomości email z metody convert()
            
        Returns:
            dict: Wynik wysyłania wiadomości
        """
        if "error" in email_data:
            return email_data
        
        if not self.config.get("smtp_server") or not self.config.get("smtp_username"):
            return {"error": "Brak konfiguracji serwera SMTP. Skonfiguruj plik email_config.json"}
        
        try:
            # Przygotuj połączenie SMTP
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"]) as server:
                if self.config.get("use_tls", True):
                    server.starttls(context=context)
                
                # Zaloguj się do serwera SMTP
                server.login(self.config["smtp_username"], self.config["smtp_password"])
                
                # Wyślij wiadomość
                server.send_message(email_data["message"])
                
                logger.info(f"Wiadomość email wysłana do: {email_data['recipient']}")
                
                return {
                    "success": True,
                    "message": "Wiadomość email została wysłana",
                    "recipient": email_data["recipient"],
                    "subject": email_data["subject"],
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Błąd podczas wysyłania wiadomości email: {e}")
            return {"error": f"Błąd podczas wysyłania wiadomości email: {str(e)}"}
    
    def load_template(self, template_name):
        """
        Ładuje szablon wiadomości email
        
        Args:
            template_name (str): Nazwa szablonu
            
        Returns:
            str: Zawartość szablonu
        """
        templates_dir = Path(self.config.get("templates_dir"))
        template_path = templates_dir / f"{template_name}.html"
        
        try:
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.warning(f"Szablon {template_name} nie istnieje")
                return None
        except Exception as e:
            logger.error(f"Błąd podczas ładowania szablonu {template_name}: {e}")
            return None
    
    def save_template(self, template_name, content):
        """
        Zapisuje szablon wiadomości email
        
        Args:
            template_name (str): Nazwa szablonu
            content (str): Zawartość szablonu
            
        Returns:
            bool: True jeśli zapisano pomyślnie, False w przeciwnym razie
        """
        templates_dir = Path(self.config.get("templates_dir"))
        template_path = templates_dir / f"{template_name}.html"
        
        try:
            # Utwórz katalog, jeśli nie istnieje
            os.makedirs(templates_dir, exist_ok=True)
            
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Szablon {template_name} został zapisany")
            return True
        except Exception as e:
            logger.error(f"Błąd podczas zapisywania szablonu {template_name}: {e}")
            return False
    
    def list_templates(self):
        """
        Zwraca listę dostępnych szablonów
        
        Returns:
            list: Lista nazw szablonów
        """
        templates_dir = Path(self.config.get("templates_dir"))
        
        try:
            if not templates_dir.exists():
                return []
            
            templates = []
            for file in templates_dir.glob("*.html"):
                templates.append(file.stem)
            
            return templates
        except Exception as e:
            logger.error(f"Błąd podczas listowania szablonów: {e}")
            return []
    
    def apply_template(self, template_name, variables, text=None):
        """
        Stosuje szablon do wiadomości email
        
        Args:
            template_name (str): Nazwa szablonu
            variables (dict): Zmienne do podstawienia w szablonie
            text (str): Opcjonalny tekst do wstawienia w miejsce {content}
            
        Returns:
            str: Wiadomość email z zastosowanym szablonem
        """
        template = self.load_template(template_name)
        if not template:
            if text:
                return self._format_email_body(text)
            return None
        
        # Dodaj treść do zmiennych, jeśli podano
        if text:
            variables["content"] = text
        
        # Zastąp zmienne w szablonie
        for key, value in variables.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))
        
        return template

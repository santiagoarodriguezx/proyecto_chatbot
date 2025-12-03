"""
Evolution API Service - Servicio para interactuar con Evolution API
Maneja el envio de mensajes via WhatsApp
"""

import requests
from typing import Optional, Dict, Any

from app.config.config import settings


class EvolutionService:
    """Servicio para gestionar mensajes via Evolution API"""

    def __init__(self):
        """Inicializar servicio de Evolution API"""
        self.evolution_url = settings.evolution_api_url
        self.api_key = settings.evolution_api_key
        self.instance = settings.evolution_instance

    def is_available(self) -> bool:
        """Verificar si Evolution API esta configurada"""
        return bool(self.evolution_url and self.api_key)

    def send_text_message(self, number: str, text: str) -> Dict[str, Any]:
        """
        Enviar mensaje de texto via Evolution API

        Args:
            number: Numero de telefono destino
            text: Texto del mensaje

        Returns:
            Diccionario con status y datos de respuesta
        """
        if not self.is_available():
            print("⚠️ Evolution API no configurada")
            return {"success": False, "error": "Evolution API no configurada"}

        try:
            url = f"{self.evolution_url}/message/sendText/{self.instance}"
            headers = {
                "Content-Type": "application/json",
                "apikey": self.api_key
            }
            data = {
                "number": number,
                "text": text
            }

            response = requests.post(
                url, json=data, headers=headers, timeout=10)

            if response.status_code == 201:
                print(f"✅ Mensaje enviado a {number}")
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": response.json() if response.text else None
                }
            else:
                print(f"⚠️ Error enviando mensaje: {response.status_code}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text
                }

        except requests.exceptions.Timeout:
            print("❌ Timeout al enviar mensaje a Evolution")
            return {"success": False, "error": "Timeout"}
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de red: {str(e)}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            print(f"❌ Error enviando a Evolution: {str(e)}")
            return {"success": False, "error": str(e)}

    def send_media_message(
        self,
        number: str,
        media_url: str,
        media_type: str = "image",
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enviar mensaje multimedia via Evolution API

        Args:
            number: Numero de telefono destino
            media_url: URL del archivo multimedia
            media_type: Tipo de media (image, audio, video, document)
            caption: Texto opcional para acompanar el media

        Returns:
            Diccionario con status y datos de respuesta
        """
        if not self.is_available():
            return {"success": False, "error": "Evolution API no configurada"}

        try:
            url = f"{self.evolution_url}/message/sendMedia/{self.instance}"
            headers = {
                "Content-Type": "application/json",
                "apikey": self.api_key
            }
            data = {
                "number": number,
                "mediaUrl": media_url,
                "mediaType": media_type
            }

            if caption:
                data["caption"] = caption

            response = requests.post(
                url, json=data, headers=headers, timeout=15)

            if response.status_code == 201:
                print(f"✅ Media enviado a {number}")
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": response.json() if response.text else None
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text
                }

        except Exception as e:
            print(f"❌ Error enviando media: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_instance_status(self) -> Dict[str, Any]:
        """
        Obtener estado de la instancia de Evolution

        Returns:
            Diccionario con estado de la instancia
        """
        if not self.is_available():
            return {"success": False, "error": "Evolution API no configurada"}

        try:
            url = f"{self.evolution_url}/instance/connectionState/{self.instance}"
            headers = {"apikey": self.api_key}

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json() if response.text else None
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text
                }

        except Exception as e:
            print(f"❌ Error obteniendo estado: {str(e)}")
            return {"success": False, "error": str(e)}


# Instancia global del servicio
evolution_service = EvolutionService()

# 🤖 Bot WhatsApp con Evolution API

Bot muy simple que recibe mensajes de WhatsApp vía Evolution API, los procesa con IA de Google y responde automáticamente.

## 🚀 Inicio Rápido

### 1. Instalar dependencias

```powershell
pip install fastapi uvicorn python-dotenv google-generativeai requests
```

### 2. Configurar `.env`

Edita tu archivo `.env`:

```env
# Google AI
GOOGLE_API_KEY=tu_api_key_aqui

# Evolution API
EVOLUTION_API_URL=http://13.58.243.103:8080/
EVOLUTION_API_KEY=tu_api_key
EVOLUTION_INSTANCE=ia-whatsapp
```

### 3. Iniciar el bot

```powershell
python app.py
```

El servidor iniciará en `http://localhost:8000`

### 4. Configurar Evolution API

En Evolution, configura los webhooks para apuntar a tu servidor:

```
http://tu-servidor:8000/
```

## 📡 Eventos Soportados

El bot acepta **todos** los eventos de Evolution API:

- `application-startup`
- `call`
- `chats-delete`, `chats-set`, `chats-update`, `chats-upsert`
- `connection-update`
- `contacts-set`, `contacts-update`, `contacts-upsert`
- `group-participants-update`, `group-update`, `groups-upsert`
- `labels-association`, `labels-edit`
- `logout-instance`
- `messages-delete`, `messages-set`, `messages-update`, **`messages-upsert`** ✨
- `presence-update`
- `qrcode-updated`
- `remove-instance`
- `send-message`
- `typebot-change-status`, `typebot-start`

**Solo `messages-upsert` se procesa con IA**, los demás solo se reciben y registran.

## 📁 Archivos

- **`app.py`** - Servidor principal con todos los endpoints
- **`message_processor.py`** - Procesa mensajes y responde
- **`ai_service.py`** - Integración con Google AI
- **`.env`** - Configuración

## 🔄 Flujo

1. Usuario envía mensaje en WhatsApp
2. Evolution envía POST a `/messages-upsert`
3. Bot procesa mensaje con Google AI
4. Bot envía respuesta a Evolution API
5. Usuario recibe respuesta

## ✅ Verificar

```powershell
# Ver si el servidor está corriendo
curl http://localhost:8000/
```

Deberías ver:

```json
{ "status": "online", "bot": "Evolution WhatsApp AI" }
```

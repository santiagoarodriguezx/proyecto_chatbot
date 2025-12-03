# PROYECTO CHATBOT

Sistema de chatbot inteligente con WhatsApp utilizando Evolution API, LangChain y Google Gemini.

## DESCRIPCION

Sistema modular de chatbot que procesa mensajes de WhatsApp, genera respuestas inteligentes usando IA, mantiene contexto conversacional y almacena toda la informacion en Supabase. Incluye herramientas de busqueda en Google para respuestas actualizadas.

## CARACTERISTICAS

- Procesamiento de mensajes en tiempo real via webhooks
- Generacion de respuestas con Google Gemini (gemini-flash-lite-latest)
- Memoria conversacional con ventana de 10 interacciones
- Busqueda en Google usando Serper API
- Sistema de prompts dinamicos almacenados en base de datos
- Gestion completa de conversaciones y mensajes
- Analytics y metricas de uso
- API REST completa con FastAPI
- Arquitectura modular y escalable

## ARQUITECTURA

```
proyecto_chatbot/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── routers/
│   │           ├── webhooks.py       # Webhooks de Evolution API
│   │           ├── messages.py       # Procesamiento de mensajes
│   │           ├── prompts.py        # Gestion de prompts
│   │           ├── conversations.py  # Historial conversaciones
│   │           └── analytics.py      # Metricas y estadisticas
│   ├── core/
│   │   └── ia_service.py            # Servicio de IA con LangChain
│   ├── services/
│   │   ├── message_service.py       # Procesador de mensajes
│   │   ├── supabase_service.py      # Servicio de base de datos
│   │   ├── evolution_service.py     # Cliente Evolution API
│   │   └── webhook_service.py       # Procesamiento webhooks
│   ├── schemas/
│   │   └── models.py                # Modelos Pydantic
│   └── main.py                      # Aplicacion principal
├── .env
├── requirements.txt
└── README.md
```

## TECNOLOGIAS

- **FastAPI**: Framework web para APIs
- **LangChain**: Framework para aplicaciones con LLM
- **Google Gemini**: Modelo de lenguaje (gemini-flash-lite-latest)
- **Supabase**: Base de datos PostgreSQL
- **Evolution API**: Integracion con WhatsApp
- **Serper API**: Busqueda en Google
- **Uvicorn**: Servidor ASGI

## INSTALACION

### REQUISITOS PREVIOS

- Python 3.10 o superior
- Cuenta de Supabase
- API Key de Google AI
- API Key de Serper (opcional, para busqueda)
- Instancia de Evolution API

### PASOS

1. Clonar el repositorio:
```bash
git clone <url-repositorio>
cd proyecto_chatbot
```

2. Crear entorno virtual:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno (.env):
```env
# Google AI
GOOGLE_API_KEY=tu_api_key_de_google

# Serper API (opcional)
SERPER_API_KEY=tu_api_key_de_serper

# Supabase
SUPABASE_URL=tu_url_de_supabase
SUPABASE_KEY=tu_key_de_supabase

# Evolution API
EVOLUTION_API_URL=http://tu-servidor:8080
EVOLUTION_API_KEY=tu_api_key_evolution
EVOLUTION_INSTANCE=nombre_instancia
```

5. Crear tablas en Supabase:
```sql
-- Tabla de conversaciones
CREATE TABLE conversations (
  id BIGSERIAL PRIMARY KEY,
  phone_number VARCHAR NOT NULL UNIQUE,
  user_name VARCHAR,
  current_state VARCHAR DEFAULT 'active',
  context JSONB DEFAULT '{}',
  last_message_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de mensajes
CREATE TABLE message_logs (
  id BIGSERIAL PRIMARY KEY,
  phone_number VARCHAR NOT NULL,
  message_text TEXT NOT NULL,
  direction VARCHAR NOT NULL CHECK (direction IN ('incoming', 'outgoing')),
  status VARCHAR DEFAULT 'sent',
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de respuestas IA
CREATE TABLE ai_responses (
  id BIGSERIAL PRIMARY KEY,
  message_log_id BIGINT REFERENCES message_logs(id),
  prompt_used TEXT,
  response_text TEXT NOT NULL,
  model_used VARCHAR,
  tokens_used INTEGER,
  response_time_ms INTEGER,
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de prompts
CREATE TABLE prompts (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR NOT NULL UNIQUE,
  content TEXT NOT NULL,
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

6. Crear prompt inicial en Supabase:
```sql
INSERT INTO prompts (name, content, description, is_active)
VALUES (
  'system_prompt',
  'Eres un asistente virtual inteligente y profesional. Tu objetivo es ayudar a los usuarios de manera clara, concisa y util. Responde de forma natural y conversacional.',
  'Prompt principal del sistema',
  TRUE
);
```

## USO

### INICIAR SERVIDOR

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### ENDPOINTS PRINCIPALES

#### WEBHOOKS

- `POST /api/v1/webhooks/messages-upsert` - Recibir mensajes de WhatsApp
- `GET /api/v1/webhooks/stats` - Estadisticas de webhooks

#### MENSAJES

- `POST /api/v1/messages/process` - Procesar mensaje manualmente
- `POST /api/v1/messages/send` - Enviar mensaje directo

#### PROMPTS

- `GET /api/v1/prompts/` - Listar prompts
- `POST /api/v1/prompts/` - Crear/actualizar prompt

#### CONVERSACIONES

- `GET /api/v1/conversations/` - Listar conversaciones
- `GET /api/v1/conversations/{phone}` - Historial de conversacion
- `DELETE /api/v1/conversations/{phone}` - Eliminar conversacion

#### ANALYTICS

- `GET /api/v1/analytics/summary?days=7` - Resumen de metricas

### EJEMPLO DE USO

```python
import requests

# Procesar mensaje
response = requests.post(
    "http://localhost:8000/api/v1/messages/process",
    json={
        "phone": "5491234567890",
        "message": "Hola, necesito ayuda"
    }
)

# Obtener historial
history = requests.get(
    "http://localhost:8000/api/v1/conversations/5491234567890"
)

# Ver analytics
analytics = requests.get(
    "http://localhost:8000/api/v1/analytics/summary?days=30"
)
```

## CONFIGURACION DE WEBHOOKS

En Evolution API, configurar el webhook para apuntar a:
```
http://tu-servidor:8000/api/v1/webhooks/messages-upsert
```

Eventos a escuchar:
- messages.upsert
- messages.update
- chats.upsert

## SERVICIOS

### IA SERVICE
Maneja toda la logica de inteligencia artificial:
- Configuracion de modelo Gemini
- Gestion de memoria conversacional
- Herramientas de busqueda en Google
- Creacion y ejecucion de agentes LangChain

### SUPABASE SERVICE
Operaciones de base de datos:
- CRUD de conversaciones
- Registro de mensajes
- Gestion de prompts
- Almacenamiento de respuestas IA

### EVOLUTION SERVICE
Integracion con WhatsApp:
- Envio de mensajes de texto
- Envio de archivos multimedia
- Gestion de instancias

### MESSAGE SERVICE
Orquestacion del flujo de mensajes:
- Procesamiento de mensajes entrantes
- Generacion de respuestas
- Envio a Evolution API
- Registro en base de datos

## DESARROLLO

### ESTRUCTURA DE CODIGO

- **Separation of Concerns**: Cada servicio tiene una responsabilidad unica
- **Dependency Injection**: Los servicios se inyectan como dependencias
- **Error Handling**: Manejo centralizado de errores
- **Logging**: Sistema de logs completo
- **Type Hints**: Tipado estatico en todo el codigo

### MEJORES PRACTICAS

- Usar servicios modularizados
- Validar disponibilidad de servicios externos
- Mantener prompts en base de datos
- Registrar todas las interacciones
- Implementar retry logic para APIs externas

## TROUBLESHOOTING

### ERROR: AttributeError _load_system_prompt
Asegurate de tener el prompt 'system_prompt' creado en Supabase.

### ERROR: Supabase no disponible
Verifica las credenciales en el archivo .env y la conectividad.

### ERROR: Evolution API timeout
Aumenta el timeout en evolution_service.py o verifica la URL de la API.

### ADVERTENCIA: LangChain deprecation
La memoria ConversationBufferWindowMemory esta deprecada, pero funcional. Migrar segun guia oficial de LangChain.

## METRICAS Y MONITOREO

El sistema registra:
- Tiempo de respuesta de IA
- Tokens utilizados
- Errores y excepciones
- Volumen de mensajes por dia
- Conversaciones activas

Acceder via endpoint de analytics o directamente en Supabase.

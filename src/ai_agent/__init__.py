def __init__(self):
    self.model = "gemini-1.5-flash"

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("❌ GEMINI_API_KEY no está configurada en las variables de entorno")

    if len(api_key) < 30:  # Validación básica
        raise ValueError("❌ GEMINI_API_KEY parece inválida (demasiado corta)")

    try:
        self.client = genai.Client(api_key=api_key)
        print("✅ Cliente Gemini inicializado correctamente")
    except Exception as e:
        raise ConnectionError(f"❌ Error al crear el cliente Gemini: {str(e)}")
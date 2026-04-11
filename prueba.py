from ultralytics import YOLO

# 1. Cargas el modelo que descargaste a tu PC 
# (Asegúrate de que el archivo esté en la misma carpeta que este script de Python)
model = YOLO('best.onnx') # O usa 'best.pt' si prefieres usar ese formato

# 2. Ejecutamos la predicción usando la cámara web local (source=0)
# stream=True es vital para procesar video en tiempo real sin saturar la memoria RAM
# show=True abre una ventana emergente para que veas lo que ve la cámara con las detecciones
resultados = model.predict(source=0, stream=True, show=True)

# 3. Mantenemos el flujo de video activo leyendo frame por frame
for resultado in resultados:
    # Verificamos si hay detecciones de fuego
    if resultado.boxes is not None and len(resultado.boxes) > 0:
        print("¡Alerta! Fuego detectado")
    # Por ahora, aquí podemos agregar más lógica en el futuro

# Nota: Para cerrar la ventana emergente de la cámara de forma segura cuando termines, 
# debes hacer clic en la ventana de video y presionar la tecla 'q' o 'Esc' (dependiendo de tu sistema)
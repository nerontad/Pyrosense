from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.schemas.usuario import UsuarioCreate, LoginRequest, TokenResponse, UsuarioResponse
from app.services.auth_service import registrar_usuario, login_usuario, obtener_usuario_por_id
from app.utils.security import decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/auth", tags=["Autenticación"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    usuario = obtener_usuario_por_id(payload["sub"])
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return usuario


@router.post("/registro", response_model=UsuarioResponse)
def registro(data: UsuarioCreate):
    usuario = registrar_usuario(
        nombre=data.nombre,
        email=data.email,
        password=data.password,
        telegram_chat_id=data.telegram_chat_id
    )
    if not usuario:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    return usuario

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    resultado = login_usuario(data.email, data.password)
    if not resultado:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return {
        "access_token": resultado["token"],
        "token_type": "bearer",
        "usuario": resultado["usuario"]
    }

@router.get("/me", response_model=UsuarioResponse)
def me(usuario=Depends(get_current_user)):
    return usuario

@router.get("/test-telegram")
async def test_telegram(usuario=Depends(get_current_user)):
    from app.services.telegram_service import enviar_alerta_video
    import os
    # Crear un video de prueba vacío
    ruta = "videos/test.mp4"
    os.makedirs("videos", exist_ok=True)
    
    # Crear archivo de video de prueba con OpenCV
    import cv2
    import numpy as np
    writer = cv2.VideoWriter(
        ruta,
        cv2.VideoWriter_fourcc(*"mp4v"),
        20, (640, 480)
    )
    for _ in range(40):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(frame, "TEST ALERTA", (150, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
        writer.write(frame)
    writer.release()

    if not usuario.get("telegram_chat_id"):
        return {"error": "No tienes telegram_chat_id configurado"}

    enviar_alerta_video(
        chat_id=usuario["telegram_chat_id"],
        ruta_video=ruta,
        ubicacion="Bodega principal",
        clase="fire",
        confianza=0.95,
        alerta_id="test-123"
    )
    return {"mensaje": "Video de prueba enviado por Telegram"}
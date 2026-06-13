import uuid
from app.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository):
    def obtener_por_id(self, usuario_id: str):
        # Obtiene un usuario por su ID
        return self._one(
            "SELECT * FROM usuarios WHERE id = %s",
            (usuario_id,)
        )

    def obtener_por_firebase_uid(self, firebase_uid: str):
        # Busca usuario por su UID de Firebase
        return self._one(
            "SELECT * FROM usuarios WHERE firebase_uid = %s",
            (firebase_uid,)
        )

    def obtener_por_email(self, email: str):
        # Busca usuario por correo electrónico
        return self._one(
            "SELECT * FROM usuarios WHERE email = %s",
            (email,)
        )

    def obtener_por_telegram_chat_id(self, chat_id: str):
        # Encuentra usuario asociado a un chat de Telegram
        return self._one(
            "SELECT id, nombre FROM usuarios WHERE telegram_chat_id = %s",
            (chat_id,)
        )

    def crear(self, firebase_uid: str, email: str, nombre: str):
        # Crea nuevo usuario autenticado con Firebase
        user_id = str(uuid.uuid4())
        self._query(
            """INSERT INTO usuarios (id, firebase_uid, nombre, email, password_hash)
               VALUES (%s, %s, %s, %s, %s)""",
            (user_id, firebase_uid, nombre, email, "firebase_auth")
        )
        return self.obtener_por_id(user_id)

    def crear_local(self, nombre: str, email: str, password_hash: str, telegram_chat_id: str = None):
        # Crea nuevo usuario con autenticación local (sin Firebase)
        user_id = str(uuid.uuid4())
        self._query(
            """INSERT INTO usuarios (id, nombre, email, password_hash, telegram_chat_id)
               VALUES (%s, %s, %s, %s, %s)""",
            (user_id, nombre, email, password_hash, telegram_chat_id)
        )
        return self.obtener_por_id(user_id)

    def vincular_firebase_uid(self, email: str, firebase_uid: str):
        # Asocia una cuenta local existente con Firebase UID
        self._query(
            "UPDATE usuarios SET firebase_uid = %s WHERE email = %s",
            (firebase_uid, email)
        )

    def actualizar_telegram(self, usuario_id: str, chat_id: str):
        # Vincula el chat_id de Telegram con la cuenta del usuario
        self._query(
            "UPDATE usuarios SET telegram_chat_id = %s WHERE id = %s",
            (chat_id, usuario_id)
        )

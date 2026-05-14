import uuid
from typing import Optional
from app.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository):
    tabla = "usuarios"

    def obtener_por_email(self, email: str) -> Optional[dict]:
        return self._query_one(
            "SELECT * FROM usuarios WHERE email = %s",
            (email,)
        )

    def obtener_publico_por_id(self, user_id: str) -> Optional[dict]:
        return self._query_one(
            "SELECT id, nombre, email, telegram_chat_id, creado_en "
            "FROM usuarios WHERE id = %s",
            (user_id,)
        )

    def obtener_por_telegram_chat(self, chat_id: str) -> Optional[dict]:
        return self._query_one(
            "SELECT id, nombre FROM usuarios WHERE telegram_chat_id = %s",
            (chat_id,)
        )

    def crear(self, nombre: str, email: str, password_hash: str,
              telegram_chat_id: Optional[str] = None) -> dict:
        user_id = str(uuid.uuid4())
        self._query(
            """INSERT INTO usuarios
               (id, nombre, email, password_hash, telegram_chat_id)
               VALUES (%s, %s, %s, %s, %s)""",
            (user_id, nombre, email, password_hash, telegram_chat_id)
        )
        return self.obtener_por_id(user_id)

    def actualizar_telegram(self, user_id: str, chat_id: str) -> None:
        self._query(
            "UPDATE usuarios SET telegram_chat_id = %s WHERE id = %s",
            (chat_id, user_id)
        )

    def obtener_por_firebase_uid(self, firebase_uid: str) -> Optional[dict]:
        return self._query_one(
            "SELECT * FROM usuarios WHERE firebase_uid = %s",
            (firebase_uid,)
        )

    def vincular_firebase_uid(self, email: str, firebase_uid: str) -> Optional[dict]:
        self._query(
            "UPDATE usuarios SET firebase_uid = %s WHERE email = %s",
            (firebase_uid, email)
        )
        return self.obtener_por_email(email)

    def crear_desde_firebase(self, firebase_uid: str, nombre: str,
                             email: str) -> dict:
        import uuid
        user_id = str(uuid.uuid4())
        self._query(
            """INSERT INTO usuarios (id, firebase_uid, nombre, email, password_hash)
               VALUES (%s, %s, %s, %s, %s)""",
            (user_id, firebase_uid, nombre, email, "firebase_auth")
        )
        return self.obtener_por_id(user_id)

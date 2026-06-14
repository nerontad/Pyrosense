"""Tests unitarios de las utilidades de seguridad: hash de contraseñas y JWT."""

from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)


class TestHashPassword:
    def test_hash_no_es_la_contrasena_en_claro(self):
        # El hash nunca debe contener la contraseña original
        h = hash_password("MiClave123")
        assert h != "MiClave123"
        assert "MiClave123" not in h

    def test_verify_acepta_contrasena_correcta(self):
        h = hash_password("Secreta!")
        assert verify_password("Secreta!", h) is True

    def test_verify_rechaza_contrasena_incorrecta(self):
        h = hash_password("Secreta!")
        assert verify_password("otra", h) is False

    def test_dos_hashes_de_la_misma_clave_son_distintos(self):
        # bcrypt usa salt aleatorio: el mismo input da hashes distintos,
        # pero ambos verifican correctamente.
        h1 = hash_password("igual")
        h2 = hash_password("igual")
        assert h1 != h2
        assert verify_password("igual", h1)
        assert verify_password("igual", h2)


class TestJWT:
    def test_token_se_puede_decodificar(self):
        token = create_access_token({"sub": "user-123", "email": "a@b.cl"})
        claims = decode_token(token)
        assert claims is not None
        assert claims["sub"] == "user-123"
        assert claims["email"] == "a@b.cl"

    def test_token_incluye_expiracion(self):
        token = create_access_token({"sub": "x"})
        claims = decode_token(token)
        assert "exp" in claims

    def test_token_invalido_devuelve_none(self):
        # Un token corrupto/no firmado por nosotros no debe decodificar
        assert decode_token("esto.no.es.un.jwt") is None

    def test_token_firmado_con_otra_clave_es_rechazado(self):
        from jose import jwt
        # Token válido en formato pero firmado con una clave distinta
        falso = jwt.encode({"sub": "intruso"}, "clave-equivocada", algorithm="HS256")
        assert decode_token(falso) is None

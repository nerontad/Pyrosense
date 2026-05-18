"""Capa Repository — abstrae el acceso a la BD.

Los routers y services usan estas instancias singleton en vez de llamar
execute_query directamente. Esto permite cambiar el motor de
persistencia (MySQL → otro) tocando solo esta capa.
"""
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.alerta_repository import AlertaRepository
from app.repositories.video_alerta_repository import VideoAlertaRepository
from app.repositories.camara_repository import CamaraRepository
from app.repositories.dispositivo_repository import DispositivoRepository
from app.repositories.lectura_repository import LecturaRepository
from app.repositories.ubicacion_repository import UbicacionRepository
from app.repositories.tipo_dispositivo_repository import TipoDispositivoRepository

usuario_repo = UsuarioRepository()
alerta_repo = AlertaRepository()
video_alerta_repo = VideoAlertaRepository()
camara_repo = CamaraRepository()
dispositivo_repo = DispositivoRepository()
lectura_repo = LecturaRepository()
ubicacion_repo = UbicacionRepository()
tipo_dispositivo_repo = TipoDispositivoRepository()

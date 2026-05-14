from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.dispositivo_repository import DispositivoRepository
from app.repositories.camara_repository import CamaraRepository
from app.repositories.lectura_repository import LecturaRepository
from app.repositories.alerta_repository import AlertaRepository
from app.repositories.video_repository import VideoAlertaRepository
from app.repositories.tipo_repository import TipoDispositivoRepository

usuario_repo     = UsuarioRepository()
dispositivo_repo = DispositivoRepository()
camara_repo      = CamaraRepository()
lectura_repo     = LecturaRepository()
alerta_repo      = AlertaRepository()
video_repo       = VideoAlertaRepository()
tipo_repo        = TipoDispositivoRepository()

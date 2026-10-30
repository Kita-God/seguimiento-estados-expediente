from src.aplicacion import EventPublisherPort, ExpedienteRepositoryPort


class RepositorioMemoria(ExpedienteRepositoryPort):  # Patrón Repository
    def __init__(self):
        self._datos = {}

    def obtener(self, codigo):
        return self._datos.get(codigo)

    def guardar(self, expediente):
        self._datos[expediente.codigo] = expediente


class PublicadorMemoria(EventPublisherPort):  # Observer / Domain Events
    def __init__(self):
        self.eventos = []

    def publicar(self, evento):
        self.eventos.append(evento)

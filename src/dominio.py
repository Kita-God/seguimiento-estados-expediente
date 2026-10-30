from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class Estado(str, Enum):
    RECIBIDO = "RECIBIDO"
    EN_OCR = "EN_OCR"
    EN_REVISION_DOCUMENTAL = "EN_REVISION_DOCUMENTAL"
    EN_EVALUACION = "EN_EVALUACION"
    OBSERVADO = "OBSERVADO"
    PRE_EVALUADO = "PRE_EVALUADO"
    RESUELTO = "RESUELTO"


# Patrón State (tabla de transiciones permitidas)
TRANSICIONES = {
    Estado.RECIBIDO: {Estado.EN_OCR},
    Estado.EN_OCR: {Estado.EN_REVISION_DOCUMENTAL},
    Estado.EN_REVISION_DOCUMENTAL: {Estado.EN_EVALUACION, Estado.OBSERVADO},
    Estado.EN_EVALUACION: {Estado.PRE_EVALUADO, Estado.OBSERVADO},
    Estado.OBSERVADO: {Estado.EN_REVISION_DOCUMENTAL},
    Estado.PRE_EVALUADO: {Estado.RESUELTO, Estado.OBSERVADO},
    Estado.RESUELTO: set(),
}


class TransicionInvalida(Exception):
    pass


@dataclass(frozen=True)
class Transicion:
    de: Estado
    a: Estado
    actor: str
    fecha: datetime
    motivo: str = ""


@dataclass
class Expediente:
    codigo: str
    estado: Estado = Estado.RECIBIDO
    historial: list = field(default_factory=list)

    def cambiar_estado(self, nuevo: Estado, actor: str, motivo: str = "") -> Transicion:
        if nuevo not in TRANSICIONES[self.estado]:
            raise TransicionInvalida(f"{self.estado.value} -> {nuevo.value}")
        t = Transicion(self.estado, nuevo, actor, datetime.now(timezone.utc), motivo)
        self.estado = nuevo
        self.historial.append(t)
        return t

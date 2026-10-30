from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Set, Optional


class Estado(str, Enum):
    RECIBIDO = "RECIBIDO"
    EN_OCR = "EN_OCR"
    EN_REVISION_DOCUMENTAL = "EN_REVISION_DOCUMENTAL"
    EN_EVALUACION = "EN_EVALUACION"
    OBSERVADO = "OBSERVADO"
    PRE_EVALUADO = "PRE_EVALUADO"
    RESUELTO = "RESUELTO"


# Patrón State: Mapa de transiciones permitidas
TRANSICIONES: dict[Estado, Set[Estado]] = {
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


class DecisionAutomaticaProhibida(Exception):
    pass


class ExpedienteNoEncontrado(Exception):
    pass


@dataclass(frozen=True)
class Transicion:
    de: Estado
    a: Estado
    responsable: str
    fecha_hora: datetime
    motivo: str = ""


@dataclass
class Expediente:
    codigo: str
    tipo_tramite: str = "Licencia de funcionamiento"
    estado_actual: Estado = Estado.RECIBIDO
    historial: List[Transicion] = field(default_factory=list)

    def cambiar_estado(self, nuevo_estado: Estado, responsable: str, motivo: str = "") -> Transicion:
        # Validación de reglas de negocio
        if nuevo_estado not in TRANSICIONES[self.estado_actual]:
            raise TransicionInvalida(
                f"Transición no permitida: de {self.estado_actual.value} solo se puede pasar a {[e.value for e in TRANSICIONES[self.estado_actual]]}"
            )

        # Regla Human-in-the-loop: Los agentes no pueden resolver expedientes
        if nuevo_estado == Estado.RESUELTO and "agente" in responsable.lower():
            raise DecisionAutomaticaProhibida("La decisión final requiere intervención humana.")

        transicion = Transicion(
            de=self.estado_actual,
            a=nuevo_estado,
            responsable=responsable,
            fecha_hora=datetime.now(timezone.utc),
            motivo=motivo,
        )

        self.estado_actual = nuevo_estado
        self.historial.append(transicion)
        return transicion

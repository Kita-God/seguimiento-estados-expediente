from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.dominio import Estado, Expediente


class ExpedienteNoEncontrado(Exception):
    pass


class DecisionAutomaticaProhibida(Exception):
    pass


@dataclass(frozen=True)
class CambiarEstadoCommand:  # Patrón Command
    codigo: str
    nuevo_estado: Estado
    actor: str
    es_humano: bool
    motivo: str = ""


# Puertos de salida
class ExpedienteRepositoryPort(ABC):
    @abstractmethod
    def obtener(self, codigo: str) -> Expediente | None: ...

    @abstractmethod
    def guardar(self, expediente: Expediente) -> None: ...


class EventPublisherPort(ABC):
    @abstractmethod
    def publicar(self, evento: dict) -> None: ...


# Puerto de entrada + caso de uso (Facade)
class CambiarEstadoUseCase:
    def __init__(self, repo: ExpedienteRepositoryPort, publicador: EventPublisherPort):
        self.repo = repo
        self.publicador = publicador

    def ejecutar(self, cmd: CambiarEstadoCommand) -> Expediente:
        exp = self.repo.obtener(cmd.codigo)
        if exp is None:
            raise ExpedienteNoEncontrado(cmd.codigo)
        if cmd.nuevo_estado == Estado.RESUELTO and not cmd.es_humano:
            raise DecisionAutomaticaProhibida("La decisión final es humana (HU-09)")
        t = exp.cambiar_estado(cmd.nuevo_estado, cmd.actor, cmd.motivo)
        self.repo.guardar(exp)
        self.publicador.publicar({
            "tipo": "expediente.estado_cambiado",
            "codigo": exp.codigo,
            "de": t.de.value,
            "a": t.a.value,
            "actor": t.actor,
        })
        return exp

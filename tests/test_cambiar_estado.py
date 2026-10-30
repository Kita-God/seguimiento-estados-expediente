import pytest

from src.adaptadores import PublicadorMemoria, RepositorioMemoria
from src.aplicacion import (CambiarEstadoCommand, CambiarEstadoUseCase,
                            DecisionAutomaticaProhibida, ExpedienteNoEncontrado)
from src.dominio import Estado, Expediente, TransicionInvalida


@pytest.fixture
def ctx():
    repo, pub = RepositorioMemoria(), PublicadorMemoria()
    return repo, pub, CambiarEstadoUseCase(repo, pub)


def _exp(repo, estado):
    repo.guardar(Expediente("EXP-2026-0001", estado))


def _cmd(nuevo, humano=False, actor="agente.documental"):
    return CambiarEstadoCommand("EXP-2026-0001", nuevo, actor, humano, "prueba")


def test_pu01_transicion_valida_actualiza_estado(ctx):
    repo, _, uc = ctx
    _exp(repo, Estado.EN_REVISION_DOCUMENTAL)
    assert uc.ejecutar(_cmd(Estado.EN_EVALUACION)).estado == Estado.EN_EVALUACION


def test_pu02_transicion_valida_publica_evento(ctx):
    repo, pub, uc = ctx
    _exp(repo, Estado.EN_REVISION_DOCUMENTAL)
    uc.ejecutar(_cmd(Estado.EN_EVALUACION))
    assert pub.eventos[0]["tipo"] == "expediente.estado_cambiado"
    assert pub.eventos[0]["a"] == "EN_EVALUACION"


def test_pu03_registra_transicion_en_historial(ctx):
    repo, _, uc = ctx
    _exp(repo, Estado.RECIBIDO)
    exp = uc.ejecutar(_cmd(Estado.EN_OCR))
    assert len(exp.historial) == 1
    assert exp.historial[0].actor == "agente.documental"


def test_pu04_transicion_invalida_se_rechaza(ctx):
    repo, pub, uc = ctx
    _exp(repo, Estado.RECIBIDO)
    with pytest.raises(TransicionInvalida):
        uc.ejecutar(_cmd(Estado.RESUELTO, humano=True))
    assert pub.eventos == []


def test_pu05_resolver_por_agente_esta_prohibido(ctx):
    repo, _, uc = ctx
    _exp(repo, Estado.PRE_EVALUADO)
    with pytest.raises(DecisionAutomaticaProhibida):
        uc.ejecutar(_cmd(Estado.RESUELTO, humano=False))


def test_pu06_resolver_por_funcionario_es_valido(ctx):
    repo, _, uc = ctx
    _exp(repo, Estado.PRE_EVALUADO)
    exp = uc.ejecutar(_cmd(Estado.RESUELTO, humano=True, actor="funcionario.jperez"))
    assert exp.estado == Estado.RESUELTO


def test_pu07_expediente_inexistente(ctx):
    _, _, uc = ctx
    with pytest.raises(ExpedienteNoEncontrado):
        uc.ejecutar(_cmd(Estado.EN_OCR))


def test_pu08_estado_final_no_admite_transiciones(ctx):
    repo, _, uc = ctx
    _exp(repo, Estado.RESUELTO)
    with pytest.raises(TransicionInvalida):
        uc.ejecutar(_cmd(Estado.OBSERVADO, humano=True))


def test_pu09_observado_retorna_a_revision_documental(ctx):
    repo, _, uc = ctx
    _exp(repo, Estado.OBSERVADO)
    assert uc.ejecutar(_cmd(Estado.EN_REVISION_DOCUMENTAL)).estado == Estado.EN_REVISION_DOCUMENTAL

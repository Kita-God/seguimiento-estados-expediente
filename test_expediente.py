import pytest
from domain import (
    Expediente,
    Estado,
    TransicionInvalida,
    DecisionAutomaticaProhibida,
    ExpedienteNoEncontrado,
)


def test_transicion_valida_actualiza_estado():
    exp = Expediente(codigo="EXP-2026-0001", estado_actual=Estado.EN_REVISION_DOCUMENTAL)
    exp.cambiar_estado(Estado.EN_EVALUACION, responsable="Funcionario Evaluador")
    assert exp.estado_actual == Estado.EN_EVALUACION


def test_se_registra_transicion_en_historial():
    exp = Expediente(codigo="EXP-2026-0001", estado_actual=Estado.RECIBIDO)
    exp.cambiar_estado(Estado.EN_OCR, responsable="Mesa de Partes")
    assert len(exp.historial) == 1
    assert exp.historial[0].responsable == "Mesa de Partes"
    assert exp.historial[0].de == Estado.RECIBIDO
    assert exp.historial[0].a == Estado.EN_OCR


def test_transicion_invalida_se_rechaza():
    exp = Expediente(codigo="EXP-2026-0001", estado_actual=Estado.RECIBIDO)
    with pytest.raises(TransicionInvalida):
        exp.cambiar_estado(Estado.RESUELTO, responsable="Usuario")


def test_agente_no_puede_resolver_expediente():
    exp = Expediente(codigo="EXP-2026-0001", estado_actual=Estado.PRE_EVALUADO)
    with pytest.raises(DecisionAutomaticaProhibida):
        exp.cambiar_estado(Estado.RESUELTO, responsable="Agente IA Documental")


def test_funcionario_humano_si_puede_resolver():
    exp = Expediente(codigo="EXP-2026-0001", estado_actual=Estado.PRE_EVALUADO)
    exp.cambiar_estado(Estado.RESUELTO, responsable="Funcionario Decisor")
    assert exp.estado_actual == Estado.RESUELTO


def test_estado_final_resuelto_no_admite_cambios():
    exp = Expediente(codigo="EXP-2026-0001", estado_actual=Estado.RESUELTO)
    with pytest.raises(TransicionInvalida):
        exp.cambiar_estado(Estado.OBSERVADO, responsable="Funcionario Decisor")


def test_expediente_observado_vuelve_a_revision():
    exp = Expediente(codigo="EXP-2026-0001", estado_actual=Estado.OBSERVADO)
    exp.cambiar_estado(Estado.EN_REVISION_DOCUMENTAL, responsable="Mesa de Partes")
    assert exp.estado_actual == Estado.EN_REVISION_DOCUMENTAL

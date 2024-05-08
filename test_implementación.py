import pytest
from datetime import datetime
from Implementación import SistemaIoT, EstrategiaMediaDesviacion, EstrategiaCuantiles, EstrategiaMaxMin, ManejadorCalculo, Operador, Observable, ManejadorUmbral

@pytest.fixture
def sistema_iot():
    estrategia = EstrategiaMaxMin()  # Elige una estrategia por defecto
    return SistemaIoT.obtener_instancia(estrategia)

def test_singleton(sistema_iot):
    sistema2 = SistemaIoT.obtener_instancia(EstrategiaMediaDesviacion())
    assert sistema_iot is sistema2, "Singleton pattern should return the same instance"

def test_estrategia_media_desviacion(capfd):
    estrategia = EstrategiaMediaDesviacion()
    temperaturas = [(datetime.now(), 20), (datetime.now(), 30), (datetime.now(), 25)]
    estrategia.calcular(temperaturas)
    out, err = capfd.readouterr()
    assert "Media" in out and "Desviación estándar" in out

def test_estrategia_cuantiles(capfd):
    estrategia = EstrategiaCuantiles()
    temperaturas = [(datetime.now(), 20), (datetime.now(), 30), (datetime.now(), 25)]
    estrategia.calcular(temperaturas)
    out, err = capfd.readouterr()
    assert "Cuantiles" in out

def test_estrategia_max_min(capfd):
    estrategia = EstrategiaMaxMin()
    temperaturas = [(datetime.now(), 20), (datetime.now(), 30), (datetime.now(), 25)]
    estrategia.calcular(temperaturas)
    out, err = capfd.readouterr()
    assert "Máximo" in out and "Mínimo" in out

def test_operador_actualizar(capfd):
    manejador = ManejadorCalculo(EstrategiaMaxMin())
    operador = Operador(manejador)
    operador.actualizar((datetime.now(), 22))
    out, err = capfd.readouterr()
    assert "Temperatura actual" in out

def test_observer_registration():
    observable = Observable()
    observer = Operador(None)
    observable.registrar_observadores(observer)
    assert observer in observable._observadores, "Observer should be added to the list"

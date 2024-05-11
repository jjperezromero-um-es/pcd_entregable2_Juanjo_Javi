import pytest
from datetime import datetime, timedelta
from Implementacion import SistemaIoT, Observable, Operador, ManejadorCalculo, ManejadorUmbral, ManejadorAumentoRapido, EstrategiaMediaDesviacion, EstrategiaCuantiles, EstrategiaMaxMin, ErrorDeSistema, ErrorDeCalculo, ErrorDeEntrada
import time



def sistema_iot():
    estrategia = EstrategiaMaxMin()  # Elige una estrategia por defecto
    return SistemaIoT.obtener_instancia(estrategia)

def test_estrategia_media_desviacion(capfd: pytest.CaptureFixture[str]):
    estrategia = EstrategiaMediaDesviacion()
    temperaturas = [(datetime.now(), 20), (datetime.now(), 30), (datetime.now(), 25)]
    estrategia.calcular(temperaturas)
    out, err = capfd.readouterr()
    assert "Media" in out and "Desviación estándar" in out

def test_estrategia_cuantiles(capfd: pytest.CaptureFixture[str]):
    estrategia = EstrategiaCuantiles()
    temperaturas = [(datetime.now(), 20), (datetime.now(), 30), (datetime.now(), 25)]
    estrategia.calcular(temperaturas)
    out, err = capfd.readouterr()
    assert "Cuantiles" in out

def test_estrategia_max_min(capfd: pytest.CaptureFixture[str]):
    estrategia = EstrategiaMaxMin()
    temperaturas = [(datetime.now(), 20), (datetime.now(), 30), (datetime.now(), 25)]
    estrategia.calcular(temperaturas)
    out, err = capfd.readouterr()
    assert "Máximo" in out and "Mínimo" in out

def test_operador_actualizar(capfd: pytest.CaptureFixture[str]):
    manejador = ManejadorCalculo(EstrategiaMaxMin())
    operador = Operador(manejador)
    tiempo_inicio = datetime.now() - timedelta(minutes=2)
    tiempo_actual = datetime.now()
    tiempo_transcurrido = (tiempo_actual - tiempo_inicio).total_seconds()
    operador.actualizar((tiempo_actual, 22), tiempo_transcurrido)
    out, err = capfd.readouterr()
    assert "Temperatura actual" in out

def test_instancia_sin_estrategia():
    with pytest.raises(ValueError):
        SistemaIoT.obtener_instancia()

def test_system_error_on_init():
    with pytest.raises(ValueError):
        SistemaIoT.obtener_instancia()
        
def test_estrategia_cuantiles_con_datos_insuficientes():
    estrategia = EstrategiaCuantiles()
    with pytest.raises(ErrorDeCalculo):
        estrategia.calcular([(datetime.now(), 25)])  
        
def test_estrategia_media_y_desviacion_con_datos_insuficientes():
    estrategia = EstrategiaMediaDesviacion()
    with pytest.raises(ErrorDeCalculo):
        estrategia.calcular([(datetime.now(), 25)])  


def test_estrategia_cuantiles_con_suficientes_datos():
    estrategia = EstrategiaCuantiles()
    estrategia.calcular([(datetime.now(), 25), (datetime.now(), 30)])

def test_manejador_umbral():
    manejador = ManejadorUmbral()
    manejador.verificar_umbral(26)

def test_manejador_aumento_rapido():
    manejador = ManejadorAumentoRapido()
    manejador.temperaturas = [(datetime.now() - timedelta(seconds=20), 20), (datetime.now(), 32)]
    manejador.comprobar_aumento_rapido()
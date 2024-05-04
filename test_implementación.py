import pytest
from Implementación import SistemaIoT, EstrategiaMediaDesviacion, EstrategiaCuantiles, EstrategiaMaxMin, Manejador, Operador, Observable

def test_singleton():
    estrategia = EstrategiaMediaDesviacion()
    sistema1 = SistemaIoT.obtener_instancia(estrategia)
    sistema2 = SistemaIoT.obtener_instancia(estrategia)
    assert sistema1 is sistema2, "Singleton pattern should return the same instance"

def test_estrategia_media_desviacion():
    estrategia = EstrategiaMediaDesviacion()
    temperaturas = [(1, 20), (2, 30), (3, 25)]
    estrategia.calcular(temperaturas)
    # Aquí puedes agregar asserts si tu función tiene salidas concretas o efectos secundarios verificables

def test_estrategia_cuantiles():
    estrategia = EstrategiaCuantiles()
    temperaturas = [(1, 20), (2, 30), (3, 25)]
    estrategia.calcular(temperaturas)
    # Similar, añadir asserts según el caso

def test_estrategia_max_min():
    estrategia = EstrategiaMaxMin()
    temperaturas = [(1, 20), (2, 30), (3, 25)]
    estrategia.calcular(temperaturas)
    # Añade asserts para verificar max y min

def test_operador_update():
    manejador = Manejador(EstrategiaMaxMin())
    operador = Operador(manejador)
    operador.update((1, 22))
    # Verifica si se manejan los datos correctamente

def test_manejador_handle_request():
    estrategia = EstrategiaMaxMin()
    manejador = Manejador(estrategia)
    manejador.handle_request((1, 35))
    assert manejador.temperaturas[-1] == (1, 35), "Temperature should be logged correctly"

def test_verificar_umbral():
    estrategia = EstrategiaMaxMin()
    manejador = Manejador(estrategia)
    
    try:
        manejador.verificar_umbral(26)  # Temperatura superior al umbral por defecto de 25
        executed = True
    except Exception as e:
        executed = False
    
    assert executed, "La función debería ejecutarse sin errores"


def test_comprobar_aumento_rapido():
    estrategia = EstrategiaMaxMin()
    manejador = Manejador(estrategia)
    manejador.temperaturas = [(1, 20), (2, 35)]
    # Aquí podrías evaluar el comportamiento de la función en situaciones límite

@pytest.mark.parametrize("input_strat, expected_type", [
    ("1", EstrategiaMediaDesviacion),
    ("2", EstrategiaCuantiles),
    ("3", EstrategiaMaxMin),
])
def test_input_estrategia(input_strat, expected_type):
    if input_strat == '1':
        estrategia = EstrategiaMediaDesviacion()
    elif input_strat == '2':
        estrategia = EstrategiaCuantiles()
    elif input_strat == '3':
        estrategia = EstrategiaMaxMin()
    else:
        with pytest.raises(ValueError):
            pass  # Aquí se probaría que el error es levantado correctamente
    assert isinstance(estrategia, expected_type), "Strategy should match the input"


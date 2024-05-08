import random
import time
from datetime import datetime
from abc import ABC, abstractmethod
from functools import reduce
from statistics import mean, stdev, quantiles

# Definición de Excepciones Personalizadas
class ErrorDeEntrada(Exception):
    """Excepción para manejar errores en las entradas de los usuarios."""
    pass

class ErrorDeCalculo(Exception):
    """Excepción para manejar errores durante los cálculos estadísticos."""
    pass

class ErrorDeSistema(Exception):
    """Excepción para manejar errores generales del sistema."""
    pass

class SistemaIoT:
    _unicaInstancia = None

    def __init__(self, estrategia):
        self.estrategia = estrategia
        self.datos_temperatura = []
        self.observable = Observable()
        self.ManejadorCondiciones = ManejadorCondiciones()
        self.manejador = ManejadorCalculo(self.estrategia, ManejadorCondiciones())
        self.operador = Operador(self.manejador)
        self.observable.registrar_observadores(self.operador)

    @classmethod
    def obtener_instancia(cls, estrategia=None):
        if cls._unicaInstancia is None:
            if estrategia is None:
                raise ValueError("Es necesario proporcionar una estrategia para inicializar el sistema")
            cls._unicaInstancia = cls(estrategia)
        return cls._unicaInstancia

    def iniciar(self, run_time_seconds):
        try:
            self.observable.run(run_time_seconds)
        except Exception as e:
            raise ErrorDeSistema(f"Error en el sistema IoT: {str(e)}")

class Observable:
    def __init__(self):
        self._observadores= []

    def registrar_observadores(self, observador):
        self._observadores.append(observador)

    def notificar_observadores(self, data):
        for observador in self._observadores:
            observador.actualizar(data)

    def run(self, run_time_seconds):
        start_time = time.time()
        while (time.time() - start_time) < run_time_seconds: # El bucle termina cuando se cumple el tiempo de ejecución
            timestamp = datetime.now()
            temperatura = random.randint(14, 33)
            self.notificar_observadores((timestamp, temperatura))
            time.sleep(5) # Cada 5 segundos se genera una nueva medición de temperatura

class observador(ABC):
    @abstractmethod
    def actualizar(self, data):
        pass

class Operador(observador):
    def __init__(self, manejador):
        self.manejador = manejador

    def actualizar(self, data):
        print(f"\n{'-' * 80}")
        print(f"Timestamp: {data[0]}. Temperatura actual: {data[1]}°C")
        try:
            self.manejador.manejador_peticion(data)
        except ErrorDeCalculo as e:
            print(f"Error durante el cálculo: {e}")

class Manejador(ABC):
    def __init__(self, sucesor=None):
        self.sucesor = sucesor

    @abstractmethod
    def manejador_peticion(self, data):
        if self.sucesor:
            self.sucesor.manejador_peticion(data)

class ManejadorCalculo(Manejador):
    def __init__(self, estrategia, sucesor=None):
        super().__init__(sucesor)
        self.estrategia = estrategia
        self.temperaturas = []

    def manejador_peticion(self, data):
        timestamp, temperatura = data
        self.temperaturas.append((timestamp, temperatura))
        try:
            self.estrategia.calcular(self.temperaturas)
        except Exception as e:
            raise ErrorDeCalculo(f"Error en el cálculo de estadísticas: {e}")
        if self.sucesor:
            self.sucesor.manejador_peticion(data)

class ManejadorCondiciones(Manejador):
    def __init__(self, sucesor=None):
        super().__init__(sucesor)
        self.temperaturas = []

    def manejador_peticion(self, data):
        timestamp, temperatura = data
        self.temperaturas.append((timestamp, temperatura))
        try:
            self.verificar_umbral(temperatura)
            self.comprobar_aumento_rapido()
        except Exception as e:
            raise ErrorDeCalculo(f"Error al verificar condiciones: {e}")
        if self.sucesor:
            self.sucesor.manejador_peticion(data)

    def verificar_umbral(self, temperatura_actual, umbral=25):
        if temperatura_actual > umbral:
            print(f"Alerta: La temperatura {temperatura_actual}°C supera el umbral de {umbral}°C.")

    def comprobar_aumento_rapido(self):
        if len(self.temperaturas) > 1:
            ultimo_ts, ultima_temp = self.temperaturas[-1]
            mediciones_recientes = list(filter(lambda x: (ultimo_ts - x[0]).seconds <= 30, self.temperaturas[:-1]))
            if any(ultima_temp - temperatura > 10 for _, temperatura in mediciones_recientes):
                print("Alerta: Incremento de temperatura > 10°C en los últimos 30 segundos.")


class EstrategiaCalculo(ABC):
    @abstractmethod
    def calcular(self, temperaturas):
        if not temperaturas:
            raise ErrorDeCalculo("Dato de entrada vacío o incorrecto")
        pass

#A continuacion las implementaciones de cada estrategia de calculo que tendra el sistema
class EstrategiaMediaDesviacion(EstrategiaCalculo):
    def calcular(self, temperaturas):
        if len(temperaturas) >= 2:
            temps = list(map(lambda x: x[1], temperaturas))
            try:
                total_sum = reduce(lambda x, y: x + y, temps)
                media = total_sum / len(temps)
                suma_cuadrados = reduce(lambda x, y: x + (y - media) ** 2, temps, 0)
                desviacion_estandar = (suma_cuadrados / (len(temps) - 1)) ** 0.5
                print(f"Media: {media:.2f}, Desviación estándar: {desviacion_estandar:.2f}")
            except Exception:
                raise ErrorDeCalculo("Error en cálculo de media y desviación estándar.")


class EstrategiaCuantiles(EstrategiaCalculo):
    def calcular(self, temperaturas):
        if len(temperaturas) < 2:
            raise ErrorDeCalculo("Datos insuficientes para calcular los cuantiles.")
        else:
            temps = list(map(lambda x: x[1], temperaturas))
            try:
                print(f"Cuantiles: {quantiles(temps)}")
            except Exception:
                raise ErrorDeCalculo("Error en el cálculo de cuantiles.")

class EstrategiaMaxMin(EstrategiaCalculo):
    def calcular(self, temperaturas):
        if temperaturas:
            temps = list(map(lambda x: x[1], temperaturas))
            try:
                maximo = reduce(lambda x, y: x if x > y else y, temps)
                minimo = reduce(lambda x, y: x if x < y else y, temps)
                print(f"Máximo: {maximo}, Mínimo: {minimo}")
            except Exception:
                raise ErrorDeCalculo("Error en el cálculo de máximo y mínimo.")

if __name__ == '__main__':
    # Bucle para que el usuario pueda elegir la cantidad de tiempo de ejecución.
    seguir = True
    while seguir:
        tiempo_ejecucion = input("\nIngrese el tiempo de ejecución en segundos del muestreo que se va a llevar a cabo: ")
        if tiempo_ejecucion.isdigit():  
            tiempo_ejecucion = int(tiempo_ejecucion)  
            if tiempo_ejecucion > 5:  
                seguir = False  
            else:
                print("\n------Error------\n\nEl tiempo de ejecución debe ser un número entero positivo mayor a 5.\n\n------Intente de nuevo------")
        else:
            print("\n------Error------\n\nEl tiempo de ejecución debe ser un número entero positivo mayor o igual a 5.\n\n------Intente de nuevo------")
    
    estrategia = input("\nSeleccione la estrategia de cálculo (1: Media y Desviación, 2: Cuantiles, 3: Máximo y Mínimo): ")
    while estrategia not in ['1', '2', '3']:
        print("\n------Error------\n\nSeleccione una opción válida (1, 2 o 3).\n\n------Intente de nuevo------")
        estrategia = input("\nSeleccione la estrategia de cálculo (1: Media y Desviación, 2: Cuantiles, 3: Máximo y Mínimo): ")
        
    if estrategia == '1':
        estrategia = EstrategiaMediaDesviacion()
    elif estrategia == '2':
        estrategia = EstrategiaCuantiles()
    elif estrategia == '3':
        estrategia = EstrategiaMaxMin()
        
    
    sistema_iot = SistemaIoT.obtener_instancia(estrategia)
    sistema_iot.iniciar(tiempo_ejecucion)



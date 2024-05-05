import random
import time
from datetime import datetime
from abc import ABC, abstractmethod
from statistics import mean, stdev, quantiles

# Definición de excepciones personalizadas para manejar errores específicos en el sistema IoT.
class ErrorDeConfiguracion(Exception):
    """Excepción para errores de configuración del sistema IoT."""
    pass

class ErrorDeTemperatura(Exception):
    """Excepción para temperaturas fuera de los límites establecidos."""
    pass

class ErrorDeCalculo(Exception):
    """Excepción para errores durante los cálculos estadísticos."""
    pass

# Clase principal del Sistema IoT que usa el patrón Singleton para garantizar una única instancia.
# Patrón de diseño Singleton
class SistemaIoT:
    _unicaInstancia = None

    def __init__(self, estrategia):
        # Inicialización de componentes principales del sistema.
        self.observable = Observable()
        self.manejador = Manejador(estrategia)
        self.operador = Operador(self.manejador)
        self.observable.register_observer(self.operador)

    @classmethod
    def obtener_instancia(cls, estrategia=None):
        if cls._unicaInstancia is None:
            cls._unicaInstancia = cls(estrategia)
        return cls._unicaInstancia

    def iniciar(self, run_time_seconds):
        self.observable.run(run_time_seconds)

# Clase para gestionar los datos observados y notificar a los observadores.
class Observable:
    def __init__(self):
        self._observers = []

    def register_observer(self, observer):
        self._observers.append(observer)

    def notify_observers(self, data):
        for observer in self._observers:
            observer.update(data)

    def run(self, run_time_seconds):
        start_time = time.time()
        while (time.time() - start_time) < run_time_seconds:
            timestamp = datetime.now()
            temperature = random.randint(14, 33)  # Simulación de la lectura de temperatura.
            self.notify_observers((timestamp, temperature))
            time.sleep(5)

# Clase abstracta para definir la interfaz de los observadores.
# Patrón de diseño Observer
class Observer(ABC):
    @abstractmethod
    def update(self, data):
        pass

# Clase que maneja las actualizaciones de datos y utiliza un Manejador para procesarlos.
class Operador(Observer):
    def __init__(self, manejador):
        self.manejador = manejador

    def update(self, data):
        print(f"\n{'-' * 50}")
        print(f"Timestamp: {data[0]} - Temperatura actual: {data[1]}°C")
        self.manejador.handle_request(data)

# Clase encargada de manejar las solicitudes de datos y aplicar las estrategias de cálculo.
class Manejador:
    def __init__(self, estrategia):
        self.temperaturas = []
        self.estrategia = estrategia

    def handle_request(self, data):
        timestamp, temperature = data
        self.temperaturas.append((timestamp, temperature))
        self.estrategia.calcular(self.temperaturas)
        self.verificar_umbral(temperature)
        self.comprobar_aumento_rapido()

    def verificar_umbral(self, temperatura_actual, umbral=25):
        if temperatura_actual > umbral:
            print(f"Alerta: La temperatura {temperatura_actual}°C supera el umbral de {umbral}°C.")

    def comprobar_aumento_rapido(self):
        if len(self.temperaturas) > 1:
            ultimo_ts, ultima_temp = self.temperaturas[-1]
            mediciones_recientes = list(filter(lambda x: (ultimo_ts - x[0]).seconds <= 30, self.temperaturas[:-1]))
            if any(ultima_temp - temperatura > 10 for _, temperatura in mediciones_recientes):
                print("Alerta: Incremento de temperatura > 10°C en los últimos 30 segundos.")

# Clase abstracta para definir estrategias de cálculo de estadísticas sobre las temperaturas.
# Patrón de diseño Strategy
class EstrategiaCalculo(ABC):
    @abstractmethod
    def calcular(self, temperaturas):
        pass

# Implementaciones concretas de la estrategia de cálculo.
class EstrategiaMediaDesviacion(EstrategiaCalculo):
    def calcular(self, temperaturas):
        if len(temperaturas) >= 2:
            temps = [temp for _, temp in temperaturas]
            print(f"Media: {mean(temps):.2f}, Desviación estándar: {stdev(temps):.2f}")

class EstrategiaCuantiles(EstrategiaCalculo):
    def calcular(self, temperaturas):
        if len(temperaturas) >= 2:
            temps = [temp for _, temp in temperaturas]
            print(f"Cuantiles: {quantiles(temps)}")

class EstrategiaMaxMin(EstrategiaCalculo):
    def calcular(self, temperaturas):
        if temperaturas:
            temps = [temp for _, temp in temperaturas]
            print(f"Máximo: {max(temps)}, Mínimo: {min(temps)}")

if __name__ == '__main__':
    while True:
        tiempo_ejecucion = input("Ingrese el tiempo de ejecución en segundos del muestreo que se va a llevar a cabo: ")
        
        if tiempo_ejecucion.isdigit():  
            tiempo_ejecucion = int(tiempo_ejecucion)  
            if tiempo_ejecucion >= 5:  
                break  
            else:
                print("\n------Error------\n\nEl tiempo de ejecución debe ser un número entero positivo mayor o igual a 5.\n\n------Intente de nuevo------\n")
        else:
            print("\n------Error------\n\nEl tiempo de ejecución debe ser un número entero positivo mayor o igual a 5.\n\n------Intente de nuevo------\n")
    
    estrategia = input("\nSeleccione la estrategia de cálculo (1: Media y Desviación, 2: Cuantiles, 3: Máximo y Mínimo): ")
    if estrategia == '1':
        estrategia = EstrategiaMediaDesviacion()
    elif estrategia == '2':
        estrategia = EstrategiaCuantiles()
    elif estrategia == '3':
        estrategia = EstrategiaMaxMin()
    else:
        raise ValueError("Estrategia inválida. Escriba 1, 2 o 3.")
    
    sistema = SistemaIoT.obtener_instancia(estrategia)
    sistema.iniciar(tiempo_ejecucion)

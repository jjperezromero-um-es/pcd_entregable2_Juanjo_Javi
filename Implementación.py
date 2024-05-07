import random
import time
from datetime import datetime
from abc import ABC, abstractmethod
from functools import reduce
from statistics import mean, stdev, quantiles

class ErrorDeConfiguracion(Exception):
    pass

class ErrorDeTemperatura(Exception):
    pass

class ErrorDeCalculo(Exception):
    pass

class SistemaIoT:
    _unicaInstancia = None

    def __init__(self, estrategia):
        self.estrategia = estrategia
        self.datos_temperatura = []
        self.observable = Observable()
        manejador_umbral = ManejadorUmbral()
        self.manejador = ManejadorCalculo(self.estrategia, ManejadorUmbral())
        self.operador = Operador(self.manejador)
        self.observable.register_observer(self.operador)

    @classmethod
    def obtener_instancia(cls, estrategia=None):
        if cls._unicaInstancia is None:
            if estrategia is None:
                raise ValueError("Es necesario proporcionar una estrategia para inicializar el sistema")
            cls._unicaInstancia = cls(estrategia)
        return cls._unicaInstancia

    def iniciar(self, run_time_seconds):
        self.observable.run(run_time_seconds)

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
        while (time.time() - start_time) < run_time_seconds: # El bucle termina cuando se cumple el tiempo de ejecución
            timestamp = datetime.now()
            temperature = random.randint(14, 33)
            self.notify_observers((timestamp, temperature))
            time.sleep(5) # Cada 5 segundos se genera una nueva medición de temperatura

class Observer(ABC):
    @abstractmethod
    def update(self, data):
        pass

class Operador(Observer):
    def __init__(self, manejador):
        self.manejador = manejador

    def update(self, data):
        # Imprime por pantalla la información de la medición de temperatura y la fecha
        print(f"\n{'-' * 80}")
        print(f"Timestamp: {data[0]}. Temperatura actual: {data[1]}°C")
        # Calcula las estadísticas de temperatura usando la estrategia seleccionada usando la funcion handle_request del Manejador
        self.manejador.handle_request(data)

class Manejador(ABC):
    def __init__(self, successor=None):
        self.successor = successor

    @abstractmethod
    def handle_request(self, data):
        if self.successor:
            self.successor.handle_request(data)

class ManejadorCalculo(Manejador):
    def __init__(self, estrategia, successor=None):
        super().__init__(successor)
        self.estrategia = estrategia
        self.temperaturas = []

    def handle_request(self, data):
        timestamp, temperature = data
        self.temperaturas.append((timestamp, temperature))
        self.estrategia.calcular(self.temperaturas)  # Pasa todas las temperaturas recogidas hasta ahora
        if self.successor:
            self.successor.handle_request(data)
        

class ManejadorUmbral(Manejador):
    def __init__(self, successor=None):
        super().__init__(successor)
        self.temperaturas = []

    def handle_request(self, data):
        timestamp, temperature = data
        self.temperaturas.append((timestamp, temperature))
        self.verificar_umbral(temperature)
        self.comprobar_aumento_rapido()
        if self.successor:
            self.successor.handle_request(data)

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
        pass

#A continuacion las implementaciones de cada estrategia de calculo que tendra el sistema
class EstrategiaMediaDesviacion(EstrategiaCalculo):
    def calcular(self, temperaturas):
        if len(temperaturas) >= 2:
            #temperaturas en una lista (cojemos x[1] ya que x es una tupla (timestamp,temp))
            temps = list(map(lambda x: x[1], temperaturas))
            print(f"Media: {mean(temps):.2f}, Desviación estándar: {stdev(temps):.2f}")

class EstrategiaCuantiles(EstrategiaCalculo):
    def calcular(self, temperaturas):
        if len(temperaturas) >= 2:
            temps = list(map(lambda x: x[1], temperaturas))
            print(f"Cuantiles: {quantiles(temps)}")

class EstrategiaMaxMin(EstrategiaCalculo):
    def calcular(self, temperaturas):
        if temperaturas:
            temps = list(map(lambda x: x[1], temperaturas))
            maximo = reduce(lambda x, y: x if x > y else y, temps)
            minimo = reduce(lambda x, y: x if x < y else y, temps)
            print(f"Máximo: {maximo}, Mínimo: {minimo}")

if __name__ == '__main__':
    # Bucle para que el usuario pueda elegir la cantidad de tiempo de ejecución.
    seguir = True
    while seguir:
        tiempo_ejecucion = input("\nIngrese el tiempo de ejecución en segundos del muestreo que se va a llevar a cabo: ")
        if tiempo_ejecucion.isdigit():  
            tiempo_ejecucion = int(tiempo_ejecucion)  
            if tiempo_ejecucion >= 5:  
                seguir = False  
            else:
                print("\n------Error------\n\nEl tiempo de ejecución debe ser un número entero positivo mayor o igual a 5.\n\n------Intente de nuevo------")
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



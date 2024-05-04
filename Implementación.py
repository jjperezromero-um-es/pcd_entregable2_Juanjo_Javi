import random
import time
from datetime import datetime
from abc import ABC, abstractmethod
from statistics import mean, stdev, quantiles

class SistemaIoT:
    _instance = None

    @staticmethod
    def getInstance(estrategia=None):
        if SistemaIoT._instance is None:
            SistemaIoT._instance = SistemaIoT(estrategia)
        return SistemaIoT._instance

    def __init__(self, estrategia):
        if SistemaIoT._instance is not None:
            raise Exception("Este sistema es Singleton y solo se puede crear una instancia.")
        else:
            self.observable = Observable()
            self.manejador = Manejador(estrategia)
            self.operador = Operador(self.manejador)
            self.observable.register_observer(self.operador)
            SistemaIoT._instance = self

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
        while (time.time() - start_time) < run_time_seconds:
            timestamp = datetime.now()
            temperature = random.randint(18, 30) 
            self.notify_observers((timestamp, temperature))
            time.sleep(5)  

class Observer(ABC):
    @abstractmethod
    def update(self, data):
        pass

class Operador(Observer):
    def __init__(self, manejador):
        self.manejador = manejador

    def update(self, data):
        self.manejador.handle_request(data)

class Manejador:
    def __init__(self, estrategia):
        self.temperaturas = []
        self.estrategia = estrategia

    def handle_request(self, data):
        timestamp, temperature = data
        # Clear old temperatures (older than 60 seconds)
        self.temperaturas = [(ts, temp) for ts, temp in self.temperaturas if (timestamp - ts).seconds <= 60]
        self.temperaturas.append((timestamp, temperature))
        self.estrategia.calcular(self.temperaturas)
        self.verificar_umbral(temperature)
        self.comprobar_aumento_rapido()

    def verificar_umbral(self, temperatura_actual, umbral=25):
        if temperatura_actual > umbral:
            print(f"\nAlerta: La temperatura actual de {temperatura_actual}°C supera el umbral de {umbral}°C.\n")

    def comprobar_aumento_rapido(self):
        if len(self.temperaturas) > 1:
            ultimos_30_seg = [(ts, temp) for ts, temp in self.temperaturas if (self.temperaturas[-1][0] - ts).seconds <= 30]
            if len(ultimos_30_seg) >= 2 and (ultimos_30_seg[-1][1] - ultimos_30_seg[0][1]) > 10:
                print("\nAlerta: Incremento de temperatura superior a 10°C en los últimos 30 segundos.\n")

class EstrategiaCalculo(ABC):
    @abstractmethod
    def calcular(self, temperaturas):
        pass

class EstrategiaMediaDesviacion(EstrategiaCalculo):
    def calcular(self, temperaturas):
        if len(temperaturas) >= 2:
            temps = [temp for _, temp in temperaturas]
            print(f"        Media: {mean(temps):.2f}, Desviación estándar: {stdev(temps):.2f}")

class EstrategiaCuantiles(EstrategiaCalculo):
    def calcular(self, temperaturas):
        if len(temperaturas) >= 2:
            temps = [temp for _, temp in temperaturas]
            print(f"        Cuantiles: {quantiles(temps)}")

class EstrategiaMaxMin(EstrategiaCalculo):
    def calcular(self, temperaturas):
        if temperaturas:
            temps = [temp for _, temp in temperaturas]
            print(f"        Máximo: {max(temps)}, Mínimo: {min(temps)}")

if __name__ == '__main__':
    
    estrategia = input("Seleccione la estrategia de cálculo (1: Media y Desviación, 2: Cuantiles, 3: Máximo y Mínimo): ")
    if estrategia == '1':
        estrategia = EstrategiaMediaDesviacion()
    elif estrategia == '2':
        estrategia = EstrategiaCuantiles()
    elif estrategia == '3':
        estrategia = EstrategiaMaxMin()
    else:
        raise ValueError("Estrategia inválida. Seleccione 1, 2 o 3.")
    sistema = SistemaIoT(estrategia)
    sistema.iniciar(60)  
    


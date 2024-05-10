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
        self.ManejadorAumentoRapido = ManejadorAumentoRapido()
        self.ManejadorUmbral = ManejadorUmbral(self.ManejadorAumentoRapido)
        self.manejador = ManejadorCalculo(self.estrategia, self.ManejadorUmbral)
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

# Clase Observable encargada de 
class Observable:
    def __init__(self):
        self._observadores= []

    # Funcion que resgistra a los observadores(En este sistema solo tendremos un observador)
    def registrar_observadores(self, observador):
        self._observadores.append(observador)

    #Funcion encargada de poner en marcha la función actualizar del Operador
    def notificar_observadores(self, data, tiempo_inicio):
        for observador in self._observadores:
            observador.actualizar(data, tiempo_inicio)

    def run(self, run_time_seconds):
        start_time = time.time()
        while (time.time() - start_time) < run_time_seconds: # El bucle termina cuando se cumple el tiempo de ejecución
            # Ponemos el time sleep al principio para que cada 60 segundos se generen 12 mediciones de temperatura
            # Si lo pongo al final, en los primeros 60 segundos se generan 13 mediciones
            time.sleep(5) # Cada 5 segundos se genera una nueva medición de temperatura
            timestamp = datetime.now()
            temperatura = random.randint(14, 33)
            # Cuando se genera una nueva temperatura ponemos en marcha la funcion notificar_observadores para el Operador actualice la salida
            self.notificar_observadores((timestamp, temperatura), start_time)
            

# Clase abstracta operador que define el metodo abstracto actualizar(Utilizado por el operador)
class observador(ABC):
    @abstractmethod
    def actualizar(self, data, tiempo_inicio):
        pass

# Clase encargada de actualizar la salida cada vez que se recibe una nueva medición de temperatura
class Operador(observador):
    def __init__(self, manejador):
        self.manejador = manejador

    def actualizar(self, data, tiempo_inicio):
        # Imprime por pantalla la información de la medición de temperatura y la fecha
        print(f"\n{'-' * 80}")
        print(f"Timestamp: {data[0]}. Temperatura actual: {data[1]}°C después de {time.time() - tiempo_inicio:.0f} segundos.")
        # Cuando termina su funcion, pondra en marcha la función del manejador.
        try:
            self.manejador.manejador_peticion(data, tiempo_inicio)
        except ErrorDeCalculo as e:
            print(f"Error durante el cálculo: {e}")

class Manejador(ABC): # Clase abstracta Manejador que será la base para la cadena de responsabilidad
    def __init__(self, sucesor=None):
        self.sucesor = sucesor

    @abstractmethod
    def manejador_peticion(self, data, tiempo_inicio):
        if self.sucesor:
            self.sucesor.manejador_peticion(data, tiempo_inicio)

# Este manejador es la primera parte de nuestra cadena de responsabilidad
# Se encargará de realizar las estrategias de calculo
class ManejadorCalculo(Manejador):
    def __init__(self, estrategia, sucesor=None):
        super().__init__(sucesor)
        self.estrategia = estrategia
        self.temperaturas = []

    def manejador_peticion(self, data, tiempo_inicio):
        #como quiero calcular las estrategias cada 60 segundos, verifico si el resto de el tiempo transcurrido entre 60 es < a 0.1 
        timestamp, temperatura = data
        self.temperaturas.append((timestamp, temperatura))
        # No puedo poner que sea exactamente = 0 porque al ser una variable continua nunca llevaremos exactamente 60 segundos  
        if (time.time() - tiempo_inicio)%60 < 0.1 and len(self.temperaturas) > 1:
            try:
                # Seleccionamos las temperaturas en los ultimos 60 segundos para hacer la estrategia en cuestion
                temperaturas_ultimos_60_segundos = self.temperaturas[-12:]
                self.estrategia.calcular(temperaturas_ultimos_60_segundos) # Realiza la estrategía
            except Exception as e:
                raise ErrorDeCalculo(f"Error en el cálculo de estadísticas: {e}") 
        # Si tiene un sucesor(En este caso el sucesor será ManejadorCondiciones), activará la funcion manejador_peticion de ese sucesor
        if self.sucesor:
            self.sucesor.manejador_peticion(data, tiempo_inicio)
        
# Este manejador es la segunda parte de la cadena de responsabilidad.
# Aqui se verificará si la temperatura supera el umbral.
class ManejadorUmbral(Manejador):
    def __init__(self, sucesor=None):
        super().__init__(sucesor)
        self.temperaturas = []

    def manejador_peticion(self, data, tiempo_inicio):
        timestamp, temperatura = data
        self.temperaturas.append((timestamp, temperatura))
        try:
            self.verificar_umbral(temperatura)
        except Exception as e:
            raise ErrorDeCalculo(f"Error al verificar condiciones: {e}")
        # En este sistema el sucesor será ManejadorAumentoRapido
        if self.sucesor:
            self.sucesor.manejador_peticion(data, tiempo_inicio)

    # Función para verificar si la temperatura actual es mayor al umbral establecido (25 grados)
    def verificar_umbral(self, temperatura_actual, umbral=25):
        if temperatura_actual > umbral:
            print(f"Alerta: La temperatura {temperatura_actual}°C supera el umbral de {umbral}°C.")


# Esta clase controla que la temperatura no aumente >10 grados en 30 segundos
# Terecera parte de la cadena de responsabilidad
class ManejadorAumentoRapido(Manejador):
    def __init__(self, sucesor=None):
        super().__init__(sucesor)
        self.temperaturas = []

    def manejador_peticion(self, data, tiempo_inicio):
        timestamp, temperatura = data
        self.temperaturas.append((timestamp, temperatura))
        try:
            self.comprobar_aumento_rapido()
        except Exception as e:
            raise ErrorDeCalculo(f"Error al verificar condiciones: {e}")
        if self.sucesor:
            self.sucesor.manejador_peticion(data, tiempo_inicio)

    # Funcion para comprobar el aumento rapido
    def comprobar_aumento_rapido(self):
        if len(self.temperaturas) > 1:
            # Sacamos la ultima temperatura que hemos obtenido
            ultimo_ts, ultima_temp = self.temperaturas[-1]
            # Filtramos las mediciones de los últimos 30 segundos usando la funcion filter
            mediciones_recientes = list(filter(lambda x: (ultimo_ts - x[0]).seconds <= 30, self.temperaturas[:-1]))
            # Si la diferencia entre la última temperatura y alguna de las mediciones filtradas es mayor a 10 grados se lanza una alerta
            if any(ultima_temp - temperatura > 10 for _, temperatura in mediciones_recientes):
                print("Alerta: Incremento de temperatura > 10°C en los últimos 30 segundos.")        

# Funcion abstracta calcular que utilizamos posteriormente en cada estrategia
class EstrategiaCalculo(ABC):
    @abstractmethod
    def calcular(self, datos):
        pass

#A continuacion las implementaciones de cada estrategia de calculo que tendra el sistema
class EstrategiaMediaDesviacion(EstrategiaCalculo):
    def calcular(self, temperaturas):
            if len(temperaturas) < 2: 
                raise ErrorDeCalculo("Datos insuficientes para calcular cuantiles.")
            temps = list(map(lambda x: x[1], temperaturas))
            # Metemos SOLO las temperaturas en una lista para calcular lo necesario con ellas
            temps = list(map(lambda x: x[1], temperaturas))
            try:
                #calculo de la media con la funcion lambda reduce
                total_sum = reduce(lambda x, y: x + y, temps)
                media = total_sum / len(temps)
                #calculo de la desviacion tipica con la funcion lambda reduce
                suma_cuadrados = reduce(lambda x, y: x + (y - media) ** 2, temps, 0)
                desviacion_estandar = (suma_cuadrados / (len(temps) - 1)) ** 0.5
                print(f"Media: {media:.2f} y Desviación estándar: {desviacion_estandar:.2f} en los ultimos 60 segundos")
            except Exception:
                raise ErrorDeCalculo("Error en cálculo de media y desviación estándar.")

class EstrategiaCuantiles(EstrategiaCalculo):
    def calcular(self, temperaturas):
            if len(temperaturas) < 2:
                raise ErrorDeCalculo("Datos insuficientes para calcular cuantiles.")
            temps = list(map(lambda x: x[1], temperaturas))
            try:
                # Calculo de los cuantiles
                print(f"Cuantiles: {quantiles(temps)} en los ultimos 60 segundos")
            except Exception:
                raise ErrorDeCalculo("Error en el cálculo de cuantiles.")

class EstrategiaMaxMin(EstrategiaCalculo):
    def calcular(self, temperaturas): 
        if len(temperaturas) < 2:  # Si se necesita al menos dos datos para calcular cuantiles
            raise ErrorDeCalculo("Datos insuficientes para calcular cuantiles")        
        if temperaturas:
            temps = list(map(lambda x: x[1], temperaturas))
            try:
                # Calculo de maximo y minimo mediante la funcion lambda reduce
                maximo = reduce(lambda x, y: x if x > y else y, temps)
                minimo = reduce(lambda x, y: x if x < y else y, temps)
                print(f"Máximo: {maximo} y Mínimo: {minimo} en los ultimos 60 segundos")
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
    
    # El usuario selecciona la estrategia
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
        
    # Ponemos en marcha el sistema
    sistema_iot = SistemaIoT.obtener_instancia(estrategia)
    sistema_iot.iniciar(tiempo_ejecucion)
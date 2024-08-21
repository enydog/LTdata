import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Función para convertir los segundos por kilómetro a minutos por kilómetro
def segundos_a_minutos(segundos):
    minutos = int(segundos // 60)
    segundos_restantes = int(segundos % 60)
    return f'{minutos:02d}:{segundos_restantes:02d}'


# Trazar las líneas de las pendientes desde el vértice
def calcular_pendiente(p1, p2):
    return (p2[1] - p1[1]) / (p2[0] - p1[0])


# Cargar los datos desde el archivo CSV 
csv_path = 'runner1.csv'
df = pd.read_csv(csv_path)

# Convertir la columna Pace (que está en formato min/km) a segundos por kilómetro
pace_sec = df['Pace (s/km)']
lactato = df['mmol']

# Ajustar una curva polinómica de grado 4 con los datos
coef_pol = np.polyfit(pace_sec, lactato, 4)
polinomio = np.poly1d(coef_pol)

# Crear un rango para evaluar el polinomio ajustado
pace_fit = np.linspace(min(pace_sec), max(pace_sec), 500)
lactato_fit = polinomio(pace_fit)

# Derivar la curva ajustada (primera, segunda y tercera derivada)
primera_derivada = np.polyder(polinomio, 1)
segunda_derivada = np.polyder(polinomio, 2)

# Evaluar las derivadas sobre el ajuste de la curva
derivada_1_fit = primera_derivada(pace_fit)
derivada_2_fit = segunda_derivada(pace_fit)

# Encontrar el vértice de la parábola de la segunda derivada
vertice_idx = np.argmin(derivada_2_fit)
vertice_pace = pace_fit[vertice_idx]
vertice_valor = derivada_2_fit[vertice_idx]

# Definir un porcentaje del total de puntos a la izquierda y derecha del vértice
porcentaje_rango = 0.02  # Elige un 2% del total de puntos

# Calcular el número dinámico de puntos a la izquierda y derecha basado en el porcentaje
num_puntos = len(pace_fit)
rango_izquierda = max(1, int(porcentaje_rango * vertice_idx))  # Asegurar al menos 1 punto
rango_derecha = max(1, int(porcentaje_rango * (num_puntos - vertice_idx)))

# Recalcular la pendiente izquierda y derecha con un rango dinámico de puntos
pendiente_izquierda = calcular_pendiente(
    (pace_fit[vertice_idx - rango_izquierda], derivada_2_fit[vertice_idx - rango_izquierda]),
    (vertice_pace, vertice_valor)
)
pendiente_derecha = calcular_pendiente(
    (vertice_pace, vertice_valor),
    (pace_fit[vertice_idx + rango_derecha], derivada_2_fit[vertice_idx + rango_derecha])
)

# Crear las líneas de pendiente ajustadas
linea_izquierda = pendiente_izquierda * (pace_fit[:vertice_idx] - vertice_pace) + vertice_valor
linea_derecha = pendiente_derecha * (pace_fit[vertice_idx:] - vertice_pace) + vertice_valor


# Identificar VT1 (cercano a 2 mmol) y VT2 (cercano a 4 mmol)
vt1_idx = np.abs(lactato_fit - 2).argmin()
vt1_pace = pace_fit[vt1_idx]
vt1_lactato = polinomio(vt1_pace)

vt2_idx = np.abs(lactato_fit - 4).argmin()
vt2_pace = pace_fit[vt2_idx]
vt2_lactato = polinomio(vt2_pace)



# Crear una figura con múltiples subplots
fig, axs = plt.subplots(3, 1, figsize=(12, 16))

# Subplot 1: Gráfico de puntos y polinómica de grado 4
axs[0].plot(pace_sec, lactato, 'bo', label='Datos Test de Lactato')
axs[0].plot(pace_fit, lactato_fit, 'r--', label='Ajuste Polinómico Grado 4')
axs[0].invert_xaxis()
axs[0].set_title('Curva Pace vs Lactato con Ajuste Polinómico Grado 4')
axs[0].set_ylabel('mmol/L')
axs[0].legend()
axs[0].grid(True)
# Formatear etiquetas del eje X a min/km
axs[0].set_xticks(np.arange(min(pace_sec), max(pace_sec), step=20))
axs[0].set_xticklabels([segundos_a_minutos(sec) for sec in np.arange(min(pace_sec), max(pace_sec), step=20)])

# Subplot 2: Curva de lactato con VT1 y VT2
axs[1].plot(pace_fit, lactato_fit, 'r-', label='Curva de Lactato')
axs[1].axvline(x=vt1_pace, color='green', linestyle='--', label=f'PI range VT1 ({segundos_a_minutos(vt1_pace)})')
axs[1].axvline(x=vt2_pace, color='magenta', linestyle='--', label=f'PI range VT2 ({segundos_a_minutos(vt2_pace)})')
axs[1].invert_xaxis()
axs[1].set_title('Curva de Lactato con VT1 y VT2')
axs[1].set_ylabel('mmol/L')
axs[1].legend()
axs[1].grid(True)
# Formatear etiquetas del eje X a min/km
axs[1].set_xticks(np.arange(min(pace_sec), max(pace_sec), step=20))
axs[1].set_xticklabels([segundos_a_minutos(sec) for sec in np.arange(min(pace_sec), max(pace_sec), step=20)])

# Subplot 4: Curvatura (Segunda derivada) con las pendientes
axs[2].plot(pace_fit, derivada_2_fit, 'g-', label='Curvatura (2da derivada)')
axs[2].plot(vertice_pace, vertice_valor, 'ro', label='Vértice de la parábola')
axs[2].plot(pace_fit[:vertice_idx], linea_izquierda, 'r--', label='Pendiente Izquierda')
axs[2].plot(pace_fit[vertice_idx:], linea_derecha, 'b--', label='Pendiente Derecha')
axs[2].invert_xaxis()
axs[2].set_title('Curvatura (Segunda Derivada) con Pendientes')
axs[2].set_ylabel('mmol/L²/s²')
axs[2].legend()
axs[2].grid(True)

# Formatear etiquetas del eje X a min/km
axs[2].set_xticks(np.arange(min(pace_sec), max(pace_sec), step=20))
axs[2].set_xticklabels([segundos_a_minutos(sec) for sec in np.arange(min(pace_sec), max(pace_sec), step=20)])

# Ajustar el layout
plt.tight_layout()

# Mostrar las gráficas
plt.show()


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Cargar los datos desde el archivo CSV proporcionado
csv_path_new = 'runner1.csv'
df_run_new = pd.read_csv(csv_path_new)

# Convertir la columna Pace (que está en formato min/km) a segundos por kilómetro
pace_sec_new = df_run_new['Pace (s/km)']
mmol_new = df_run_new['mmol']

# Ajustar una curva polinómica de grado 4 con los nuevos datos
coeffs_polinomio_new = np.polyfit(pace_sec_new, mmol_new, 4)
polynomial_pace_new = np.poly1d(coeffs_polinomio_new)

# Crear un rango para evaluar el polinomio ajustado
pace_fit_new = np.linspace(min(pace_sec_new), max(pace_sec_new), 500)
mmol_fit_new = polynomial_pace_new(pace_fit_new)

# Derivar la curva ajustada (primera y segunda derivada)
first_derivative_new = np.polyder(polynomial_pace_new, 1)
second_derivative_new = np.polyder(polynomial_pace_new, 2)
pace_fit_first_derivative_new = first_derivative_new(pace_fit_new)
pace_fit_second_derivative_new = second_derivative_new(pace_fit_new)

# Identificar VT1 (cercano a 2 mmol) y VT2 (cercano a 4 mmol)
vt1_index_new_corrected = np.abs(mmol_fit_new - 2).argmin()
vt1_pace_new_corrected = pace_fit_new[vt1_index_new_corrected]
vt1_mmol_new_corrected = polynomial_pace_new(vt1_pace_new_corrected)

vt2_index_new_corrected = np.abs(mmol_fit_new - 4).argmin()
vt2_pace_new_corrected = pace_fit_new[vt2_index_new_corrected]
vt2_mmol_new_corrected = polynomial_pace_new(vt2_pace_new_corrected)

# Aclaramiento de lactato: observar la curva después de VT2
pace_post_vt2 = pace_fit_new[pace_fit_new < vt2_pace_new_corrected]  # Después de VT2
mmol_post_vt2 = polynomial_pace_new(pace_post_vt2)

# Función para convertir los segundos por kilómetro a minutos por kilómetro
def seconds_to_pace_label(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f'{minutes:02d}:{remaining_seconds:02d}'

# Crear una figura con múltiples subplots
fig, axs = plt.subplots(5, 1, figsize=(12, 20))

# Subplot 1: Gráfico de puntos y polinómica de grado 4 con trazo doble
axs[0].plot(pace_sec_new, mmol_new, 'bo', label='Datos Originales')
axs[0].plot(pace_fit_new, mmol_fit_new, 'r--', label='Ajuste Polinómico Grado 4')
axs[0].invert_xaxis()
axs[0].set_title('Curva Pace_sec vs mmol con Ajuste Polinómico Grado 4 (Trazo Doble)')
axs[0].set_ylabel('mmol/L')
axs[0].legend()
axs[0].grid(True)
# Formatear etiquetas del eje X a min/km
axs[0].set_xticks(np.arange(min(pace_sec_new), max(pace_sec_new), step=20))
axs[0].set_xticklabels([seconds_to_pace_label(sec) for sec in np.arange(min(pace_sec_new), max(pace_sec_new), step=20)])

# Subplot 2: Curva de lactato con VT1 y VT2
axs[1].plot(pace_fit_new, mmol_fit_new, 'r-', label='Curva Lactato')
axs[1].axvline(x=vt1_pace_new_corrected, color='green', linestyle='--', label=f'VT1 ({seconds_to_pace_label(vt1_pace_new_corrected)})')
axs[1].axvline(x=vt2_pace_new_corrected, color='magenta', linestyle='--', label=f'VT2 ({seconds_to_pace_label(vt2_pace_new_corrected)})')
axs[1].invert_xaxis()
axs[1].set_title('Curva de Lactato con VT1 y VT2')
axs[1].set_ylabel('mmol/L')
axs[1].legend()
axs[1].grid(True)
# Formatear etiquetas del eje X a min/km
axs[1].set_xticks(np.arange(min(pace_sec_new), max(pace_sec_new), step=20))
axs[1].set_xticklabels([seconds_to_pace_label(sec) for sec in np.arange(min(pace_sec_new), max(pace_sec_new), step=20)])

# Subplot 3: Tasa de cambio (Primera derivada)
axs[2].plot(pace_fit_new, pace_fit_first_derivative_new, 'b-', label='Tasa de Cambio (1ra derivada)')
axs[2].invert_xaxis()
axs[2].set_title('Tasa de Cambio (Primera Derivada)')
axs[2].set_ylabel('mmol/L/s')
axs[2].legend()
axs[2].grid(True)
# Formatear etiquetas del eje X a min/km
axs[2].set_xticks(np.arange(min(pace_sec_new), max(pace_sec_new), step=20))
axs[2].set_xticklabels([seconds_to_pace_label(sec) for sec in np.arange(min(pace_sec_new), max(pace_sec_new), step=20)])

# Subplot 4: Curvatura (Segunda derivada) con las zonas sombreadas (Fácil, Duro, Severo)
axs[3].plot(pace_fit_new, pace_fit_second_derivative_new, 'g-', label='Curvatura (2da derivada)')
# Sombrear las zonas
# Zona Fácil
axs[3].fill_between(pace_fit_new, pace_fit_second_derivative_new, where=(pace_fit_new >= 325),
                 color='green', alpha=0.3, label='Zona Fácil (verde)')
# Zona Dura
axs[3].fill_between(pace_fit_new, pace_fit_second_derivative_new, where=(pace_fit_new >= 297) & (pace_fit_new < 325),
                 color='orange', alpha=0.3, label='Zona Dura (naranja)')
# Zona Severa
axs[3].fill_between(pace_fit_new, pace_fit_second_derivative_new, where=(pace_fit_new < 297),
                 color='red', alpha=0.3, label='Zona Severa (rojo)')
axs[3].invert_xaxis()
axs[3].set_title('Curvatura (Segunda Derivada) con Zonas Fácil, Dura y Severa')
axs[3].set_ylabel('mmol/L²/s²')
axs[3].legend()
axs[3].grid(True)
# Formatear etiquetas del eje X a min/km
axs[3].set_xticks(np.arange(min(pace_sec_new), max(pace_sec_new), step=20))
axs[3].set_xticklabels([seconds_to_pace_label(sec) for sec in np.arange(min(pace_sec_new), max(pace_sec_new), step=20)])

# Subplot 5: Aclaramiento de lactato post-VT2
axs[4].plot(pace_fit_new, mmol_fit_new, 'r-', label='Curva Lactato')
axs[4].plot(pace_post_vt2, mmol_post_vt2, 'b-', label='Curva Post-VT2')
axs[4].axvline(x=vt2_pace_new_corrected, color='magenta', linestyle='--', label=f'VT2 ({seconds_to_pace_label(vt2_pace_new_corrected)})')
axs[4].invert_xaxis()
axs[4].set_title('Comportamiento del Lactato después de VT2')
axs[4].set_xlabel('Pace (min/km)')
axs[4].set_ylabel('mmol/L')
axs[4].legend()
axs[4].grid(True)
# Formatear etiquetas del eje X a min/km
axs[4].set_xticks(np.arange(min(pace_sec_new), max(pace_sec_new), step=20))
axs[4].set_xticklabels([seconds_to_pace_label(sec) for sec in np.arange(min(pace_sec_new), max(pace_sec_new), step=20)])

# Ajustar el layout
plt.tight_layout()

# Mostrar las gráficas
plt.show()


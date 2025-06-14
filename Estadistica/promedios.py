
# Verificar estilos disponibles y usar uno compatible
available_styles = plt.style.available
print("Estilos disponibles:", available_styles)

# Usar 'seaborn' (o el más parecido disponible)
current_style = 'seaborn' if 'seaborn' in available_styles else 'ggplot'
plt.style.use(current_style)

# Configuración de tamaños
plt.rcParams['figure.figsize'] = [14, 10]
plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True

def procesar_datos(csv_path='video_metrics_summary.csv'):
    # Leer el archivo CSV
    try:
        df = pd.read_csv(csv_path, parse_dates=['timestamp'])
        print(f"Datos cargados correctamente desde {csv_path}")
        print(f"Registros encontrados: {len(df)}")
    except Exception as e:
        print(f"Error al leer el archivo: {str(e)}")
        return None

    # Calcular métricas agregadas
    metricas = {
        'Promedio Voltaje (mV)': df['Volt'].mean(),
        'Promedio Corriente (mA)': df['Curr'].mean(),
        'Promedio Potencia (mW)': df['power'].mean(),
        'Consumo Total (mWh)': (df['power'] * df['duracion_s'] / 3600).sum(),
        'FPS Promedio': df['fps_promedio'].mean(),
        'Duración Total (s)': df['duracion_s'].sum()
    }

    # Crear figura con múltiples subplots
    fig, axs = plt.subplots(3, 1, figsize=(14, 16))
    
    # Gráfico 1: Evolución de parámetros eléctricos
    axs[0].plot(df['timestamp'], df['Volt'], 'o-', label='Voltaje (mV)', color='blue')
    axs[0].plot(df['timestamp'], df['Curr'], 's-', label='Corriente (mA)', color='orange')
    axs[0].plot(df['timestamp'], df['power'], 'd-', label='Potencia (mW)', color='green')
    axs[0].set_title('Evolución de Parámetros Eléctricos')
    axs[0].set_ylabel('Valor')
    axs[0].legend()
    axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    
    # Gráfico 2: Rendimiento del sistema
    axs[1].plot(df['timestamp'], df['fps_promedio'], 'o-', label='FPS Promedio', color='red')
    axs[1].plot(df['timestamp'], df['mem_allocated_MB'], 's-', label='Memoria Alloc (MB)', color='purple')
    axs[1].set_title('Rendimiento del Sistema')
    axs[1].set_ylabel('Valor')
    axs[1].legend()
    axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    
    # Gráfico 3: Consumo acumulado
    df['consumo_acumulado_mWh'] = (df['power'] * df['duracion_s'] / 3600).cumsum()
    axs[2].plot(df['timestamp'], df['consumo_acumulado_mWh'], 'o-', color='brown')
    axs[2].set_title('Consumo Energético Acumulado')
    axs[2].set_ylabel('Consumo (mWh)')
    axs[2].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    
    # Ajustar formato de fechas
    for ax in axs:
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    # Mostrar métricas calculadas
    print("\n--- Métricas Agregadas ---")
    for k, v in metricas.items():
        print(f"{k}: {v:.2f}")
    
    # Guardar gráficos
    timestamp_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"analisis_energetico_{timestamp_actual}.png"
    plt.savefig(nombre_archivo, dpi=150, bbox_inches='tight')  # DPI reducido para Jetson
    print(f"\nGráficos guardados como: {nombre_archivo}")
    
    return df, metricas

if __name__ == "__main__":
    print(f"Usando estilo: {current_style}")
    datos, metricas = procesar_datos()
    plt.show()

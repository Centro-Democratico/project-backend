
"""RF_1 – Como usuario, quiero contar con 
una interfaz sobrepuesta que muestre los 
FPS en tiempo real y un resumen al 
finalizar para monitorear el desempeño 
técnico de mis juegos de forma inmediata"""

def calculate_session_metrics(fps_list):
    if not fps_list:
        return {'max_fps': 0, 'min_fps': 0, 'avg_fps': 0.0}
    return {
        'max_fps': max(fps_list),
        'min_fps': min(fps_list),
        'avg_fps': round(sum(fps_list) / len(fps_list), 2)
    }

"""RF_2 – Como usuario, quiero activar y 
desactivar la interfaz mediante una 
combinación de teclas personalizada para 
controlar la visibilidad de las estadísticas 
sin interrumpir mi flujo de trabajo o juego"""

def toggle_overlay_state(current_state):
    if not isinstance(current_state, bool):
        raise ValueError("El estado debe ser booleano")
    return not current_state

"""RF_6 – Como usuario, quiero comparar mis 
resultados con los de dispositivos estándar 
del mercado para situar el rendimiento de 
mi máquina en relación con otros equipos"""

def calculate_performance_gap(user_fps, market_fps):
    if market_fps <= 0:
        return 0.0
    gap = ((user_fps - market_fps) / market_fps) * 100
    return round(gap, 2)

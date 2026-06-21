import requests
from datetime import datetime

def obtener_mejor_partido():
    # Obtener la fecha de hoy
    hoy = datetime.today().strftime('%Y-%m-%d')
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={hoy}"
    
    print(f"Buscando partidos para hoy: {hoy}...")
    respuesta = requests.get(url).json()

    if 'dates' not in respuesta or not respuesta['dates']:
        print("No hay juegos de la MLB programados para hoy.")
        return

    juegos = respuesta['dates'][0]['games']
    mejor_juego = None
    mayor_diferencia = -1
    ganador_proyectado = ""

    for juego in juegos:
        try:
            visitante = juego['teams']['away']
            local = juego['teams']['home']

            # Obtener récord de victorias y derrotas
            v_victorias = visitante['leagueRecord']['wins']
            v_derrotas = visitante['leagueRecord']['losses']
            l_victorias = local['leagueRecord']['wins']
            l_derrotas = local['leagueRecord']['losses']

            # Calcular el porcentaje de victorias (Win Percentage)
            pct_visitante = v_victorias / (v_victorias + v_derrotas) if (v_victorias + v_derrotas) > 0 else 0
            pct_local = l_victorias / (l_victorias + l_derrotas) if (l_victorias + l_derrotas) > 0 else 0

            # Calcular la diferencia de nivel
            diferencia = abs(pct_visitante - pct_local)

            if diferencia > mayor_diferencia:
                mayor_diferencia = diferencia
                mejor_juego = f"{visitante['team']['name']} (Visita) vs {local['team']['name']} (Local)"
                ganador_proyectado = visitante['team']['name'] if pct_visitante > pct_local else local['team']['name']
                
        except KeyError:
            # Si un equipo no tiene récords aún (ej. pretemporada), lo saltamos
            continue

    if mejor_juego:
        print("\n⚾ --- PREDICCIÓN DEL DÍA --- ⚾")
        print(f"Partido: {mejor_juego}")
        print(f"Ganador estadístico más probable: **{ganador_proyectado}**")
        print(f"Ventaja (Diferencia de Win%): {mayor_diferencia:.3f}")
        
        # Nota de la realidad:
        print("\n*Recuerda: ¡En el béisbol cualquier cosa puede pasar!*")

if __name__ == "__main__":
    obtener_mejor_partido()


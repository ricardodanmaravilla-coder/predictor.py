import requests
from datetime import datetime

def obtener_prediccion_avanzada():
    hoy = datetime.today().strftime('%Y-%m-%d')
    # Usamos 'hydrate' para traer pitchers, estadísticas de temporada y brazos de lanzar en 1 sola petición
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={hoy}&hydrate=probablePitcher,team(stats(type=season,season=2026))"
    
    print(f"📊 Analizando la cartelera y métricas avanzadas para hoy: {hoy}...\n")
    respuesta = requests.get(url).json()

    if 'dates' not in respuesta or not respuesta['dates']:
        print("No hay juegos de la MLB programados para hoy.")
        return

    juegos = respuesta['dates'][0]['games']
    mejor_juego = None
    mayor_probabilidad = 0
    analisis_completo = ""

    for juego in juegos:
        try:
            # Datos básicos del juego
            visitante = juego['teams']['away']
            local = juego['teams']['home']
            es_de_noche = juego.get('dayNight', 'unknown') == 'night'
            horario_str = "Noche 🌙" if es_de_noche else "Día ☀️"

            # Nombres de los equipos
            nom_visita = visitante['team']['name']
            nom_local = local['team']['name']

            # --- ESTADÍSTICAS DEL EQUIPO (Para Carreras Esperadas) ---
            # Extraemos las estadísticas generales de la temporada de los equipos
            stats_visita = visitante['team']['teamStats'][0]['splits'][0]['stat']
            stats_local = local['team']['teamStats'][0]['splits'][0]['stat']

            runs_visita = stats_visita.get('runs', 0)
            juegos_visita = stats_visita.get('gamesPlayed', 1)
            runs_allowed_visita = stats_visita.get('runsAllowed', 0)

            runs_local = stats_local.get('runs', 0)
            juegos_local = stats_local.get('gamesPlayed', 1)
            runs_allowed_local = stats_local.get('runsAllowed', 0)

            # Promedio de carreras anotadas y permitidas por juego
            promedio_anotadas_visita = runs_visita / juegos_visita
            promedio_permitidas_visita = runs_allowed_visita / juegos_visita
            
            promedio_anotadas_local = runs_local / juegos_local
            promedio_permitidas_local = runs_allowed_local / juegos_local

            # --- ESTADÍSTICAS DE LANZADORES ABRIDORES ---
            pitcher_visita = "TBD"
            era_visita = 4.50 # Promedio de la liga por defecto si no hay pitcher asignado
            brazo_visita = "D/Z"
            
            if 'probablePitcher' in visitante:
                p_data = visitante['probablePitcher']
                pitcher_visita = p_data.get('fullName', 'TBD')
                brazo_visita = p_data.get('pitchHand', {}).get('code', 'D/Z')
                # Simulamos sacar el ERA (la API a veces requiere una llamada extra para stats de jugador, usaremos un factor si no está)

            pitcher_local = "TBD"
            era_local = 4.50
            brazo_local = "D/Z"
            
            if 'probablePitcher' in local:
                p_data = local['probablePitcher']
                pitcher_local = p_data.get('fullName', 'TBD')
                brazo_local = p_data.get('pitchHand', {}).get('code', 'D/Z')

            # --- CÁLCULO DE CARRERAS ESPERADAS (Fórmula Heurística) ---
            # Carreras Esperadas Visita = (Anotadas Promedio Visita + Permitidas Promedio Local) / 2
            carreras_esperadas_visita = (promedio_anotadas_visita + promedio_permitidas_local) / 2
            
            # Carreras Esperadas Local = (Anotadas Promedio Local + Permitidas Promedio Visita) / 2
            carreras_esperadas_local = (promedio_anotadas_local + promedio_permitidas_visita) / 2

            # --- CÁLCULO DE VICTORIA (Teorema Pitagórico del Béisbol modificado) ---
            # Win% = (Runs Scored^1.83) / (Runs Scored^1.83 + Runs Allowed^1.83)
            win_pct_visita = (carreras_esperadas_visita**1.83) / ((carreras_esperadas_visita**1.83) + (carreras_esperadas_local**1.83))
            win_pct_local = 1 - win_pct_visita

            # Ajuste ligero por localía (+2% al equipo de casa)
            win_pct_local += 0.02
            win_pct_visita -= 0.02

            # Determinamos quién es el favorito de este partido
            diferencia_pct = abs(win_pct_local - win_pct_visita)

            if diferencia_pct > mayor_probabilidad:
                mayor_probabilidad = diferencia_pct
                favorito = nom_local if win_pct_local > win_pct_visita else nom_visita
                probabilidad_favorito = max(win_pct_local, win_pct_visita) * 100

                mejor_juego = f"{nom_visita} vs {nom_local}"
                
                analisis_completo = f"""
⚾ EL MEJOR PARTIDO PARA APOSTAR / SEGUIR ⚾
--------------------------------------------------
Juego: {nom_visita} vs {nom_local}
Horario/Condición: {horario_str}

🎯 PREDICCIÓN ESTADÍSTICA:
🏆 Favorito: {favorito} (Probabilidad de victoria: {probabilidad_favorito:.1f}%)

🔥 CARRERAS ESPERADAS (Marcador Proyectado):
- {nom_visita}: {carreras_esperadas_visita:.1f} carreras
- {nom_local}: {carreras_esperadas_local:.1f} carreras
- Total de carreras proyectadas en el juego (Over/Under): {(carreras_esperadas_visita + carreras_esperadas_local):.1f}

⚾ LANZADORES ABRIDORES:
- Visita: {pitcher_visita} (Lanza a la: {brazo_visita})
- Local: {pitcher_local} (Lanza a la: {brazo_local})

📈 NOTA DEL MODELO: 
Cálculo basado en carreras promedio anotadas/permitidas y el Teorema Pitagórico del Béisbol.
--------------------------------------------------
"""
        except Exception as e:
            # Si a un juego le faltan estadísticas (pasa a veces con dobles carteleras o juegos cancelados), lo ignoramos
            continue

    if mejor_juego:
        print(analisis_completo)
    else:
        print("No se encontraron estadísticas suficientes para analizar los partidos de hoy.")

if __name__ == "__main__":
    obtener_prediccion_avanzada()

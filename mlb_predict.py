import requests
from datetime import datetime

def obtener_prediccion_avanzada():
    hoy_dt = datetime.today()
    hoy = hoy_dt.strftime('%Y-%m-%d')
    anio_actual = hoy_dt.year
    
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={hoy}&hydrate=probablePitcher,team(stats(type=season,season={anio_actual}))"
    
    print(f"📊 Analizando la cartelera para hoy: {hoy}...")
    try:
        respuesta = requests.get(url).json()
    except Exception as e:
        print(f"Error al conectar con la API: {e}")
        return

    # Si no hay juegos programados hoy
    if 'dates' not in respuesta or not respuesta['dates'] or not respuesta['dates'][0]['games']:
        generar_html_vacio(hoy_dt.strftime('%d/%m/%Y'))
        print("No hay juegos hoy. Se generó página de descanso.")
        return

    juegos = respuesta['dates'][0]['games']
    mejor_juego = None
    mayor_probabilidad = -1
    datos_mejor_juego = {}

    for juego in juegos:
        try:
            visitante = juego['teams']['away']
            local = juego['teams']['home']
            es_de_noche = juego.get('dayNight', 'unknown') == 'night'
            
            nom_visita = visitante['team']['name']
            nom_local = local['team']['name']

            # Estadísticas de temporada
            stats_visita = visitante['team']['teamStats'][0]['splits'][0]['stat']
            stats_local = local['team']['teamStats'][0]['splits'][0]['stat']

            runs_visita = stats_visita.get('runs', 0)
            juegos_visita = stats_visita.get('gamesPlayed', 1)
            runs_allowed_visita = stats_visita.get('runsAllowed', 0)

            runs_local = stats_local.get('runs', 0)
            juegos_local = stats_local.get('gamesPlayed', 1)
            runs_allowed_local = stats_local.get('runsAllowed', 0)

            prom_anotadas_visita = runs_visita / juegos_visita
            prom_permitidas_visita = runs_allowed_visita / juegos_visita
            prom_anotadas_local = runs_local / juegos_local
            prom_permitidas_local = runs_allowed_local / juegos_local

            # Pitchers probables
            pitcher_visita = visitante.get('probablePitcher', {}).get('fullName', 'Por anunciar (TBD)')
            brazo_visita = visitante.get('probablePitcher', {}).get('pitchHand', {}).get('code', '-')
            
            pitcher_local = local.get('probablePitcher', {}).get('fullName', 'Por anunciar (TBD)')
            brazo_local = local.get('probablePitcher', {}).get('pitchHand', {}).get('code', '-')

            # Carreras esperadas (Fórmula heurística cruzada)
            carreras_esperadas_visita = (prom_anotadas_visita + prom_permitidas_local) / 2
            carreras_esperadas_local = (prom_anotadas_local + prom_permitidas_visita) / 2

            # Teorema Pitagórico del Béisbol
            runs_v_exp = carreras_esperadas_visita**1.83
            runs_l_exp = carreras_esperadas_local**1.83
            
            if (runs_v_exp + runs_l_exp) > 0:
                win_pct_visita = runs_v_exp / (runs_v_exp + runs_l_exp)
            else:
                win_pct_visita = 0.5
            win_pct_local = 1 - win_pct_visita

            # Ajuste de ventaja por localía (+2%)
            win_pct_local += 0.02
            win_pct_visita -= 0.02

            diferencia_pct = abs(win_pct_local - win_pct_visita)

            # Buscamos el partido con mayor ventaja/diferencia estadística clara
            if diferencia_pct > mayor_probabilidad:
                mayor_probabilidad = diferencia_pct
                favorito = nom_local if win_pct_local > win_pct_visita else nom_visita
                probabilidad_favorito = max(win_pct_local, win_pct_visita) * 100

                datos_mejor_juego = {
                    "fecha": hoy_dt.strftime('%d/%m/%Y'),
                    "visita": nom_visita,
                    "local": nom_local,
                    "horario": "Noche 🌙" if es_de_noche else "Día ☀️",
                    "favorito": favorito,
                    "probabilidad": probabilidad_favorito,
                    "carreras_visita": carreras_esperadas_visita,
                    "carreras_local": carreras_esperadas_local,
                    "total_carreras": carreras_esperadas_visita + carreras_esperadas_local,
                    "pitcher_visita": pitcher_visita,
                    "brazo_visita": brazo_visita,
                    "pitcher_local": pitcher_local,
                    "brazo_local": brazo_local
                }
        except Exception as e:
            continue

    if datos_mejor_juego:
        generar_html_prediccion(datos_mejor_juego)
        print("¡Archivo index.html generado con éxito!")
    else:
        generar_html_vacio(hoy_dt.strftime('%d/%m/%Y'))
        print("Datos insuficientes hoy. Se generó página por defecto.")

def generar_html_prediccion(d):
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MLB Predictor Bot</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            margin: 0;
            padding: 15px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        .container {{
            max-width: 500px;
            width: 100%;
            background: #1e293b;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.4);
            padding: 20px;
            border: 1px solid #334155;
            box-sizing: border-box;
        }}
        h1 {{
            text-align: center;
            color: #38bdf8;
            margin-top: 0;
            font-size: 22px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .date {{
            text-align: center;
            color: #94a3b8;
            font-size: 13px;
            margin-bottom: 20px;
        }}
        .matchup {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #0f172a;
            padding: 12px 15px;
            border-radius: 12px;
            margin-bottom: 15px;
            font-weight: bold;
            font-size: 15px;
            border-left: 5px solid #38bdf8;
        }}
        .condition {{
            font-size: 11px;
            background: #334155;
            padding: 3px 8px;
            border-radius: 20px;
            color: #cbd5e1;
        }}
        .section-title {{
            color: #94a3b8;
            font-size: 13px;
            margin-top: 20px;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding-bottom: 3px;
        }}
        .prediction-card {{
            background: linear-gradient(135deg, #1e3a8a 0%, #0369a1 100%);
            padding: 18px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(3, 105, 161, 0.3);
            border: 1px solid #2563eb;
        }}
        .prediction-card .fav {{
            font-size: 20px;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 4px;
        }}
        .prediction-card .prob {{
            font-size: 15px;
            color: #e0f2fe;
        }}
        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 15px;
        }}
        .card {{
            background: #0f172a;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid #334155;
        }}
        .card-title {{
            font-size: 11px;
            color: #64748b;
            text-transform: uppercase;
            margin-bottom: 4px;
        }}
        .card-value {{
            font-size: 14px;
            font-weight: bold;
        }}
        .total-box {{
            background: #311042;
            border: 1px solid #581c87;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            color: #f3e8ff;
            font-size: 13px;
            margin-bottom: 20px;
        }}
        footer {{
            text-align: center;
            font-size: 10px;
            color: #64748b;
            margin-top: 20px;
            line-height: 1.4;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>⚾ MLB Predictor ⚾</h1>
        <div class="date">Selección del Día • {d['fecha']}</div>
        
        <div class="matchup">
            <div>{d['visita']} <span style="color:#64748b; font-size:12px;">@</span> {d['local']}</div>
            <div class="condition">{d['horario']}</div>
        </div>

        <div class="prediction-card">
            <div style="font-size: 11px; text-transform: uppercase; color: #bae6fd; letter-spacing: 1px; margin-bottom: 4px;">Mayor ventaja estadística</div>
            <div class="fav">🏆 {d['favorito']}</div>
            <div class="prob">Probabilidad de ganar: <strong>{d['probabilidad']:.1f}%</strong></div>
        </div>

        <div class="section-title">🔥 Carreras Esperadas (Proyección)</div>
        <div class="grid">
            <div class="card" style="border-top: 3px solid #ef4444;">
                <div class="card-title">{d['visita']}</div>
                <div class="card-value">{d['carreras_visita']:.1f} Runs</div>
            </div>
            <div class="card" style="border-top: 3px solid #10b981;">
                <div class="card-title">{d['local']}</div>
                <div class="card-value">{d['carreras_local']:.1f} Runs</div>
            </div>
        </div>
        
        <div class="total-box">
            📊 Total carreras en el juego (Over/Under): {d['total_carreras']:.1f}
        </div>

        <div class="section-title">🧢 Lanzadores Abridores</div>
        <div class="grid">
            <div class="card">
                <div class="card-title">Visita</div>
                <div class="card-value" style="font-size:13px;">{d['pitcher_visita']}</div>
                <div style="font-size:10px; color:#64748b; margin-top:2px;">Brazo: {d['brazo_visita']}</div>
            </div>
            <div class="card">
                <div class="card-title">Local</div>
                <div class="card-value" style="font-size:13px;">{d['pitcher_local']}</div>
                <div style="font-size:10px; color:#64748b; margin-top:2px;">Brazo: {d['brazo_local']}</div>
            </div>
        </div>

        <footer>
            Actualizado automáticamente mediante GitHub Actions.<br>
            Basado en el Teorema Pitagórico de Sabermetría. ¡Usa con responsabilidad!
        </footer>
    </div>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def generar_html_vacio(fecha):
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MLB Predictor Bot</title>
    <style>
        body {{ font-family: sans-serif; background-color: #0f172a; color: #f8fafc; text-align: center; padding: 50px 15px; margin: 0; }}
        .box {{ background: #1e293b; padding: 25px; border-radius: 12px; display: inline-block; max-width: 400px; border: 1px solid #334155; }}
        h1 {{ color: #38bdf8; font-size: 20px; }}
    </style>
</head>
<body>
    <div class="box">
        <h1>⚾ MLB Predictor ⚾</h1>
        <p style="font-size: 14px; color: #94a3b8;">Fecha: {fecha}</p>
        <p>Hoy no hay partidos programados en la MLB o las estadísticas oficiales no están disponibles aún.</p>
        <p style="color: #64748b; font-size: 12px; margin-top: 20px;">El sistema volverá a escanear mañana temprano.</p>
    </div>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    obtener_prediccion_avanzada()
    

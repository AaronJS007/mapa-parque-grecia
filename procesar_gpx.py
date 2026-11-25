import os
import json
import gpxpy
import gpxpy.gpx

def procesar():
    print("Iniciando procesamiento de trazas GPX...")
    features = []
    
    if os.path.exists('trazas'):
        for filename in os.listdir('trazas'):
            if filename.endswith('.gpx'):
                print(f"Procesando: {filename}")
                try:
                    with open(f'trazas/{filename}', 'r', encoding='utf-8') as gpx_file:
                        gpx = gpxpy.parse(gpx_file)
                        
                        # 1. Extraer puntos de interés (waypoints)
                        for waypoint in gpx.waypoints:
                            time_str = waypoint.time.isoformat() if waypoint.time else "2024-01-01T00:00:00"
                            
                            # Extraer la foto: waypoint.link YA ES EL TEXTO del enlace
                            foto_url = ""
                            if waypoint.link:
                                # .split('/')[-1] asegura que si viene una ruta larga, solo tome el nombre final (.jpg)
                                foto_url = str(waypoint.link).split('/')[-1]
                                
                            features.append({
                                "type": "Feature",
                                "geometry": {"type": "Point", "coordinates": [waypoint.longitude, waypoint.latitude]},
                                "properties": {
                                    "name": waypoint.name or "Punto sin nombre", 
                                    "desc": waypoint.description or "", 
                                    "type": "punto", 
                                    "time": time_str,
                                    "foto": foto_url 
                                }
                            })
                        
                        # 2. Extraer trazas (recorridos)
                        for track in gpx.tracks:
                            for segment in track.segments:
                                coords = [[point.longitude, point.latitude] for point in segment.points]
                                first_point = segment.points[0] if segment.points else None
                                time_str = first_point.time.isoformat() if first_point and first_point.time else "2024-01-01T00:00:00"
                                
                                if coords:
                                    features.append({
                                        "type": "Feature",
                                        "geometry": {"type": "LineString", "coordinates": coords},
                                        "properties": {"name": track.name or "Traza sin nombre", "type": "traza", "time": time_str}
                                    })
                except Exception as e:
                    print(f"Error procesando el archivo {filename}: {e}")

    geojson = {"type": "FeatureCollection", "features": features}
    with open('datos.geojson', 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
        
    print(f"¡Proceso terminado! Se guardaron {len(features)} elementos en datos.geojson")

if __name__ == "__main__":
    procesar()

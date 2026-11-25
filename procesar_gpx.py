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
                with open(f'trazas/{filename}', 'r') as gpx_file:
                    gpx = gpxpy.parse(gpx_file)
                    
                    # Extraer puntos de interés (waypoints)
                    for waypoint in gpx.waypoints:
                        # Extraer la fecha (si existe)
                        time_str = waypoint.time.isoformat() if waypoint.time else "2024-01-01T00:00:00"
                        features.append({
                            "type": "Feature",
                            "geometry": {"type": "Point", "coordinates": [waypoint.longitude, waypoint.latitude]},
                            "properties": {"name": waypoint.name, "desc": waypoint.description, "type": "punto", "time": time_str}
                        })
                    
                    # Extraer trazas (recorridos)
                    for track in gpx.tracks:
                        for segment in track.segments:
                            coords = [[point.longitude, point.latitude] for point in segment.points]
                            # Extraer la fecha del primer punto de la traza
                            first_point = segment.points[0] if segment.points else None
                            time_str = first_point.time.isoformat() if first_point and first_point.time else "2024-01-01T00:00:00"
                            
                            if coords:
                                features.append({
                                    "type": "Feature",
                                    "geometry": {"type": "LineString", "coordinates": coords},
                                    "properties": {"name": track.name, "type": "traza", "time": time_str}
                                })

    geojson = {"type": "FeatureCollection", "features": features}
    with open('datos.geojson', 'w') as f:
        json.dump(geojson, f)
    print(f"¡Proceso terminado! Se guardaron {len(features)} elementos en datos.geojson")

if __name__ == "__main__":
    procesar()

import os
import json
import gpxpy
import gpxpy.gpx

def procesar():
    print("Iniciando procesamiento de trazas GPX...")
    features = []
    
    # Buscar archivos GPX en la carpeta 'trazas'
    if os.path.exists('trazas'):
        for filename in os.listdir('trazas'):
            if filename.endswith('.gpx'):
                print(f"Procesando: {filename}")
                with open(f'trazas/{filename}', 'r') as gpx_file:
                    gpx = gpxpy.parse(gpx_file)
                    
                    # Extraer puntos de interés (waypoints)
                    for waypoint in gpx.waypoints:
                        features.append({
                            "type": "Feature",
                            "geometry": {"type": "Point", "coordinates": [waypoint.longitude, waypoint.latitude]},
                            "properties": {"name": waypoint.name, "desc": waypoint.description, "type": "punto"}
                        })
                    
                    # Extraer trazas (recorridos)
                    for track in gpx.tracks:
                        for segment in track.segments:
                            coords = [[point.longitude, point.latitude] for point in segment.points]
                            if coords:
                                features.append({
                                    "type": "Feature",
                                    "geometry": {"type": "LineString", "coordinates": coords},
                                    "properties": {"name": track.name, "type": "traza"}
                                })

    # Guardar el archivo GeoJSON
    geojson = {"type": "FeatureCollection", "features": features}
    with open('datos.geojson', 'w') as f:
        json.dump(geojson, f)
    print(f"¡Proceso terminado! Se guardaron {len(features)} elementos en datos.geojson")

if __name__ == "__main__":
    procesar()

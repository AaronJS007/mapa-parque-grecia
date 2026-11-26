import os
import json
import gpxpy
import gpxpy.gpx
import zipfile
import shutil

def extraer_y_ordenar_zips():
    print("Buscando archivos ZIP de OSMTracker...")
    
    # Crear carpetas si no existen
    if not os.path.exists('trazas'): os.makedirs('trazas')
    if not os.path.exists('fotos'): os.makedirs('fotos')

    for filename in os.listdir('.'):
        if filename.endswith('.zip'):
            print(f"Extrayendo: {filename}")
            temp_dir = "temp_extract"
            
            try:
                with zipfile.ZipFile(filename, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Recorrer los archivos extraídos
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        # Si es GPX, va a trazas/
                        if file.endswith('.gpx'):
                            shutil.move(file_path, os.path.join('trazas', file))
                            print(f"  -> Movido a trazas/: {file}")
                            
                        # Si es imagen o audio, va a fotos/
                        elif file.lower().endswith(('.jpg', '.jpeg', '.png', '.3gp', '.m4a', '.mp3')):
                            shutil.move(file_path, os.path.join('fotos', file))
                            print(f"  -> Movido a fotos/: {file}")
                            
            except Exception as e:
                print(f"Error extrayendo {filename}: {e}")
            finally:
                # Limpiar carpeta temporal y borrar el ZIP original
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                os.remove(filename)
                print(f"  -> Archivo {filename} procesado y eliminado.")

def procesar_gpx():
    print("Iniciando procesamiento de trazas GPX...")
    features = []
    
    if os.path.exists('trazas'):
        for filename in os.listdir('trazas'):
            if filename.endswith('.gpx'):
                print(f"Procesando: {filename}")
                try:
                    with open(f'trazas/{filename}', 'r', encoding='utf-8') as gpx_file:
                        gpx = gpxpy.parse(gpx_file)
                        
                        for waypoint in gpx.waypoints:
                            time_str = waypoint.time.isoformat() if waypoint.time else "2024-01-01T00:00:00"
                            
                            foto_url = ""
                            if waypoint.link:
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
    extraer_y_ordenar_zips() # Primero descomprime y ordena
    procesar_gpx()           # Luego procesa los GPX

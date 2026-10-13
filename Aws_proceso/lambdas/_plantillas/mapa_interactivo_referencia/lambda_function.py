"""
Lambda: Generador de Mapa Interactivo — Emergencia Sísmica
CDO · Alcaldía de Santiago de Cali

Lee cruces de curated/ + RUD georreferenciado (IDECS)
y genera HTML con Leaflet en analytics/mapa/

Capas:
1. Reportes ciudadanos (Blend/InstantDB)
2. Evaluaciones técnicas (EDE)
3. RUD cruzado con reportes (por dirección)
4. RUD georreferenciado IDECS (geocodificación municipal) ← NUEVO
"""

import json
import os
import re
import boto3
import pandas as pd
from io import BytesIO
from datetime import datetime, timezone

S3_BUCKET      = os.environ.get("S3_BUCKET", "aca-prod-calitrack-sismo-cali")
CRUCES_PREFIX  = os.environ.get("CRUCES_PREFIX", "curated/cruces")
RUD_GEO_PREFIX = os.environ.get("RUD_GEO_PREFIX", "curated/rud_georreferenciado")
OUTPUT_PREFIX  = os.environ.get("OUTPUT_PREFIX", "analytics/mapa")

s3 = boto3.client("s3")


def get_latest_date(prefix):
    resp = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix, Delimiter="/")
    folders = [p["Prefix"] for p in resp.get("CommonPrefixes", [])]
    dates = [f.rstrip("/").split("/")[-1] for f in folders]
    dates = [d for d in dates if re.match(r"\d{4}-\d{2}-\d{2}", d)]
    return sorted(dates)[-1] if dates else None


def get_latest_file(prefix, extension):
    """Encuentra el archivo más reciente con la extensión dada."""
    resp = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
    files = [
        obj for obj in resp.get("Contents", [])
        if obj["Key"].endswith(extension)
    ]
    if not files:
        return None
    files.sort(key=lambda x: x["LastModified"], reverse=True)
    return files[0]["Key"]


def read_json_s3(key):
    obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
    return json.loads(obj["Body"].read().decode("utf-8"))


def read_csv_s3(key):
    obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
    return pd.read_csv(BytesIO(obj["Body"].read()), low_memory=False)


def lambda_handler(event, context):
    timestamp = datetime.now(timezone.utc)
    batch_date = get_latest_date(f"{CRUCES_PREFIX}/")
    if not batch_date:
        return {"statusCode": 500, "body": "No hay datos en curated/cruces/"}

    print(f"Batch date: {batch_date}")

    # ── Leer cruces existentes ──
    eval_rep = read_json_s3(f"{CRUCES_PREFIX}/{batch_date}/evaluacion_x_reporte.json")
    ciud_rud = read_json_s3(f"{CRUCES_PREFIX}/{batch_date}/ciudadano_x_rud_completo.json")
    rud_rep = read_json_s3(f"{CRUCES_PREFIX}/{batch_date}/rud_x_reporte_direccion.json")
    calidad = read_json_s3(f"{CRUCES_PREFIX}/{batch_date}/resumen_calidad.json")

    # Reportes completos
    rep_date = get_latest_date("raw/blend_instantdb/reporte/")
    reportes = read_json_s3(f"raw/blend_instantdb/reporte/{rep_date}/reporte.json")

    # ── Leer RUD georreferenciado IDECS ──
    rud_geo_key = get_latest_file(RUD_GEO_PREFIX, ".csv")
    rud_geo_data = []
    rud_geo_count = 0
    if rud_geo_key:
        print(f"Leyendo RUD georreferenciado: {rud_geo_key}")
        try:
            df_geo = read_csv_s3(rud_geo_key)
            # Filtrar solo los que tienen coordenadas
            df_geo = df_geo[df_geo["latitud"].notna() & df_geo["longitud"].notna()]
            rud_geo_count = len(df_geo)
            print(f"  RUD georreferenciado: {rud_geo_count:,} personas con coords")

            # Agrupar por dirección para no poner 45K marcadores
            for dir_bien, group in df_geo.groupby("direccion_bien"):
                row = group.iloc[0]
                estados = group["estado_bien"].value_counts().to_dict()
                peor = None
                for e in ["Destruido", "No Habitable", "Averiado", "Habitable"]:
                    if e in estados:
                        peor = e
                        break

                rud_geo_data.append({
                    "lat": float(row["latitud"]),
                    "lng": float(row["longitud"]),
                    "dir": str(dir_bien) if dir_bien else "",
                    "estado": peor or "",
                    "personas": len(group),
                    "hogares": int(group["numero_formulario"].nunique()),
                    "barrio": str(row.get("vereda_bien", "")) if pd.notna(row.get("vereda_bien")) else "",
                })
        except Exception as e:
            print(f"  ⚠️ Error leyendo RUD geo: {e}")
    else:
        print("  ⚠️ No se encontró RUD georreferenciado")

    print(f"Eval×Rep: {len(eval_rep)} | Ciud×RUD: {len(ciud_rud)} | "
          f"RUD×Rep: {len(rud_rep)} | Reportes: {len(reportes)} | "
          f"RUD IDECS: {len(rud_geo_data)}")

    # Stats
    ciud_en_rud = sum(1 for c in ciud_rud if c.get("en_rud"))
    rud_total = calidad.get("rud_cali", calidad.get("rud_filtrado", 0))
    eval_total = calidad.get("evaluaciones", 0)

    # Porcentajes de georreferenciación
    rud_sin_geo = rud_total - rud_geo_count
    pct_geo = round(100 * rud_geo_count / rud_total, 1) if rud_total > 0 else 0
    pct_sin = round(100 - pct_geo, 1)

    # Colores
    hab_colors = {
        "h": "#27AE60", "r1": "#F39C12", "r2": "#E67E22",
        "i1": "#E74C3C", "i2": "#C0392B", "i3": "#8B0000",
    }
    tipo_colors = {
        "A": "#27AE60", "B": "#3498DB", "C": "#F39C12",
        "D": "#E74C3C", "E": "#8B0000", "F": "#1C1C1C",
    }
    estado_colors = {
        "Destruido": "#8B0000", "No Habitable": "#C0392B",
        "Averiado": "#F39C12", "Habitable": "#27AE60",
    }

    # ── Preparar datos JS ──
    # Capa 1: Reportes
    reportes_js = []
    for r in reportes:
        if r.get("lat") and r.get("lng"):
            reportes_js.append({
                "lat": r["lat"], "lng": r["lng"],
                "dir": r.get("direccion", ""),
                "tipo": r.get("tipoAfectacion", "?"),
                "inm": r.get("tipoInmueble", ""),
                "nombre": r.get("nombreInmueble", ""),
                "apto": r.get("numeroApartamento", ""),
                "casa": r.get("numeroCasa", ""),
                "desc": (r.get("descripcion") or "")[:150],
            })

    # Capa 2: Evaluaciones
    eval_js = []
    for e in eval_rep:
        if e.get("lat") and e.get("lng"):
            eval_js.append({
                "lat": e["lat"], "lng": e["lng"],
                "hab": e.get("eval_habitabilidad", "?"),
                "dir": e.get("eval_direccion", ""),
                "dano": e.get("eval_danoMuros", ""),
                "evac": e.get("eval_evacuacion", ""),
                "com": e.get("comuna", ""),
                "bar": e.get("barrio", ""),
                "rep_tipo": e.get("rep_tipoAfectacion", ""),
                "concepto": e.get("eval_concepto", ""),
            })

    # Capa 3: RUD cruzado con reportes (cruces Lambda 1)
    rud_js = []
    for r in rud_rep:
        if r.get("lat") and r.get("lng"):
            rud_js.append({
                "lat": r["lat"], "lng": r["lng"],
                "dir_rud": r.get("dir_original", ""),
                "estado": r.get("peor_estado", ""),
                "personas": r.get("personas", 0),
                "hogares": r.get("hogares", 0),
                "barrio": r.get("barrio", ""),
                "rep_dir": r.get("rep_direccion", ""),
                "rep_tipo": r.get("rep_tipoAfectacion", ""),
            })

    # Capa 4: RUD georreferenciado IDECS (rud_geo_data ya está listo)

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mapa Emergencia Sísmica — Cali 2026 | CDO</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css"/>
<script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: 'Segoe UI', system-ui, sans-serif; }}
#map {{ width:100%; height:100vh; }}
.header {{
    position:absolute; top:0; left:50px; right:50px; z-index:1000;
    background:rgba(10,31,63,0.92); color:white; padding:10px 20px;
    border-radius:0 0 12px 12px; display:flex; align-items:center; gap:20px;
}}
.header h1 {{ font-size:16px; font-weight:600; }}
.header .sub {{ font-size:11px; color:#C9992D; }}
.stats {{
    position:absolute; bottom:20px; left:20px; z-index:1000;
    background:rgba(10,31,63,0.92); color:white; padding:15px 20px;
    border-radius:12px; font-size:12px; line-height:1.8; min-width:240px;
}}
.stats h3 {{ color:#C9992D; margin-bottom:5px; font-size:14px; }}
.stats .num {{ font-weight:700; color:#C9992D; font-size:14px; }}
.legend {{
    position:absolute; bottom:20px; right:20px; z-index:1000;
    background:rgba(10,31,63,0.92); color:white; padding:15px;
    border-radius:12px; font-size:11px; max-height:80vh; overflow-y:auto;
}}
.legend h4 {{ margin-bottom:8px; color:#C9992D; }}
.legend-item {{ display:flex; align-items:center; gap:8px; margin:4px 0; }}
.legend-dot {{ width:12px; height:12px; border-radius:50%; border:1px solid rgba(255,255,255,0.3); }}
.layer-control {{
    position:absolute; top:70px; right:20px; z-index:1000;
    background:rgba(10,31,63,0.92); color:white; padding:12px 15px;
    border-radius:10px; font-size:12px;
}}
.layer-control label {{ display:block; margin:4px 0; cursor:pointer; }}
.layer-control input {{ margin-right:6px; }}
.layer-control .sep {{ border-top:1px solid rgba(255,255,255,0.2); margin:6px 0; }}
</style>
</head>
<body>

<div class="header">
    <div>
        <h1>Emergencia Sísmica — Consolidación de Datos · Cali 2026</h1>
        <div class="sub">Oficina del CDO · Despacho del Alcalde · Corte {batch_date}</div>
    </div>
</div>

<div class="stats">
    <h3>Resumen</h3>
    Reportes ciudadanos: <span class="num">{len(reportes):,}</span><br>
    Evaluaciones técnicas: <span class="num">{len(eval_rep)}</span><br>
    Ciudadanos en RUD: <span class="num">{ciud_en_rud:,}</span> / {len(ciud_rud):,}<br>
    RUD cruzado (reportes): <span class="num">{len(rud_rep):,}</span> dirs<br>
    <hr style="border-color:rgba(255,255,255,0.2);margin:8px 0">
    <h3>Georreferenciación RUD Cali</h3>
    <div style="display:flex;justify-content:space-between;margin:4px 0">
        <span>Con coordenadas:</span>
        <span class="num">{rud_geo_count:,}</span>
    </div>
    <div style="display:flex;justify-content:space-between;margin:4px 0">
        <span>Sin coordenadas:</span>
        <span style="color:#E74C3C;font-weight:700">{rud_sin_geo:,}</span>
    </div>
    <div style="display:flex;justify-content:space-between;margin:4px 0">
        <span>Total RUD Cali:</span>
        <span style="font-weight:700">{rud_total:,}</span>
    </div>
    <div style="background:rgba(255,255,255,0.15);border-radius:6px;height:18px;margin:8px 0;overflow:hidden;position:relative">
        <div style="background:#C9992D;height:100%;width:{pct_geo}%;border-radius:6px;transition:width 0.5s"></div>
        <span style="position:absolute;top:0;left:0;right:0;text-align:center;font-size:10px;line-height:18px;font-weight:700">{pct_geo}% georreferenciado</span>
    </div>
    <hr style="border-color:rgba(255,255,255,0.2);margin:8px 0">
    <span style="font-size:10px;color:#888">Fuentes: InstantDB (Blend) + FURE (UNGRD) + IDECS (Cali)</span>
</div>

<div class="layer-control">
    <strong style="color:#C9992D">Capas</strong><br>
    <label><input type="checkbox" id="chk_rep" checked onchange="toggleLayer('rep')"> Reportes ({len(reportes_js):,})</label>
    <label><input type="checkbox" id="chk_eval" checked onchange="toggleLayer('eval')"> Evaluaciones ({len(eval_js)})</label>
    <div class="sep"></div>
    <label><input type="checkbox" id="chk_rud" onchange="toggleLayer('rud')"> RUD × Reportes ({len(rud_js):,})</label>
    <label><input type="checkbox" id="chk_idecs" checked onchange="toggleLayer('idecs')"> RUD IDECS ({len(rud_geo_data):,})</label>
</div>

<div class="legend">
    <h4>Habitabilidad (EDE)</h4>
    <div class="legend-item"><div class="legend-dot" style="background:#27AE60"></div> H — Habitable</div>
    <div class="legend-item"><div class="legend-dot" style="background:#F39C12"></div> R1 — Uso restringido</div>
    <div class="legend-item"><div class="legend-dot" style="background:#E67E22"></div> R2 — Entrada limitada</div>
    <div class="legend-item"><div class="legend-dot" style="background:#E74C3C"></div> I1 — Riesgo</div>
    <div class="legend-item"><div class="legend-dot" style="background:#C0392B"></div> I2 — No habitable</div>
    <div class="legend-item"><div class="legend-dot" style="background:#8B0000"></div> I3 — Colapso</div>
    <h4 style="margin-top:10px">Estado bien (RUD)</h4>
    <div class="legend-item"><div class="legend-dot" style="background:#8B0000"></div> Destruido</div>
    <div class="legend-item"><div class="legend-dot" style="background:#C0392B"></div> No Habitable</div>
    <div class="legend-item"><div class="legend-dot" style="background:#F39C12"></div> Averiado</div>
    <div class="legend-item"><div class="legend-dot" style="background:#27AE60"></div> Habitable</div>
    <h4 style="margin-top:10px">Tipo afectación</h4>
    <div class="legend-item"><div class="legend-dot" style="background:#27AE60"></div> A — Sin daño</div>
    <div class="legend-item"><div class="legend-dot" style="background:#3498DB"></div> B — Menor</div>
    <div class="legend-item"><div class="legend-dot" style="background:#F39C12"></div> C — Moderado</div>
    <div class="legend-item"><div class="legend-dot" style="background:#E74C3C"></div> D — Significativo</div>
    <div class="legend-item"><div class="legend-dot" style="background:#8B0000"></div> E — Severo</div>
    <div class="legend-item"><div class="legend-dot" style="background:#1C1C1C"></div> F — Colapso</div>
</div>

<div id="map"></div>

<script>
const map = L.map('map').setView([3.42, -76.53], 13);

L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    attribution: '&copy; OSM | CDO Alcaldía de Cali',
    maxZoom: 19
}}).addTo(map);

const tipoColors = {json.dumps(tipo_colors)};
const habColors = {json.dumps(hab_colors)};
const estadoColors = {json.dumps(estado_colors)};

// ═══ Capa 1: Reportes ═══
const repData = {json.dumps(reportes_js)};
const repCluster = L.markerClusterGroup({{
    maxClusterRadius: 40, spiderfyOnMaxZoom: true, showCoverageOnHover: false,
    iconCreateFunction: function(cluster) {{
        const n = cluster.getChildCount();
        let r = n < 50 ? 25 : n < 200 ? 35 : 45;
        return L.divIcon({{
            html: '<div style="background:rgba(52,152,219,0.8);color:white;border-radius:50%;width:'+r*2+'px;height:'+r*2+'px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;border:2px solid rgba(255,255,255,0.4)">'+n+'</div>',
            className: '', iconSize: [r*2, r*2]
        }});
    }}
}});
repData.forEach(r => {{
    const c = tipoColors[r.tipo] || '#888';
    const m = L.circleMarker([r.lat, r.lng], {{
        radius:4, fillColor:c, color:'rgba(255,255,255,0.3)', weight:1, fillOpacity:0.8
    }});
    m.bindPopup(`<b>Reporte ciudadano</b><br>${{r.dir}}<br>Tipo: <b>${{r.tipo}}</b><br>Inmueble: ${{r.inm}}${{r.nombre?'<br>'+r.nombre:''}}${{r.desc?'<br><small>'+r.desc+'</small>':''}}`);
    repCluster.addLayer(m);
}});
map.addLayer(repCluster);

// ═══ Capa 2: Evaluaciones ═══
const evalData = {json.dumps(eval_js)};
const evalGroup = L.layerGroup();
evalData.forEach(e => {{
    const c = habColors[e.hab] || '#888';
    const m = L.circleMarker([e.lat, e.lng], {{
        radius:8, fillColor:c, color:'white', weight:2, fillOpacity:0.9
    }});
    m.bindPopup(
        `<b>Evaluación técnica</b><br>${{e.dir}}<br>` +
        `Comuna: <b>${{e.com}}</b> | Barrio: <b>${{e.bar}}</b><br>` +
        `Habitabilidad: <b style="color:${{c}}">${{e.hab.toUpperCase()}}</b><br>` +
        `Daño muros: <b>${{e.dano}}</b><br>Evacuación: <b>${{e.evac}}</b><br>` +
        `<hr style="margin:4px 0"><small>${{e.concepto}}</small>`
    );
    evalGroup.addLayer(m);
}});
map.addLayer(evalGroup);

// ═══ Capa 3: RUD cruzado con reportes ═══
const rudData = {json.dumps(rud_js)};
const rudCluster = L.markerClusterGroup({{
    maxClusterRadius: 30,
    iconCreateFunction: function(cluster) {{
        const n = cluster.getChildCount();
        let r = n < 20 ? 20 : n < 100 ? 30 : 40;
        return L.divIcon({{
            html: '<div style="background:rgba(155,89,182,0.8);color:white;border-radius:50%;width:'+r*2+'px;height:'+r*2+'px;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;border:2px solid rgba(255,255,255,0.4)">'+n+'</div>',
            className: '', iconSize: [r*2, r*2]
        }});
    }}
}});
rudData.forEach(r => {{
    const c = estadoColors[r.estado] || '#9B59B6';
    const m = L.circleMarker([r.lat, r.lng], {{
        radius:5, fillColor:c, color:'rgba(255,255,255,0.4)', weight:1, fillOpacity:0.7
    }});
    m.bindPopup(
        `<b>RUD × Reporte</b><br>` +
        `${{r.dir_rud}}<br>` +
        `Estado: <b style="color:${{c}}">${{r.estado}}</b><br>` +
        `Personas: <b>${{r.personas}}</b> | Hogares: <b>${{r.hogares}}</b><br>` +
        `Barrio: ${{r.barrio}}<br>` +
        `Reporte: ${{r.rep_dir}}<br>Tipo: <b>${{r.rep_tipo}}</b>`
    );
    rudCluster.addLayer(m);
}});

// ═══ Capa 4: RUD georreferenciado IDECS ═══
const idecsData = {json.dumps(rud_geo_data)};
const idecsCluster = L.markerClusterGroup({{
    maxClusterRadius: 35,
    iconCreateFunction: function(cluster) {{
        const n = cluster.getChildCount();
        let r = n < 30 ? 22 : n < 150 ? 32 : 42;
        return L.divIcon({{
            html: '<div style="background:rgba(211,84,0,0.85);color:white;border-radius:50%;width:'+r*2+'px;height:'+r*2+'px;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;border:2px solid rgba(255,255,255,0.4)">'+n+'</div>',
            className: '', iconSize: [r*2, r*2]
        }});
    }}
}});
idecsData.forEach(r => {{
    const c = estadoColors[r.estado] || '#D35400';
    const m = L.circleMarker([r.lat, r.lng], {{
        radius:6, fillColor:c, color:'rgba(255,255,255,0.5)', weight:1.5, fillOpacity:0.85
    }});
    m.bindPopup(
        `<b>Damnificado RUD (IDECS)</b><br>` +
        `${{r.dir}}<br>` +
        `Estado: <b style="color:${{c}}">${{r.estado}}</b><br>` +
        `Personas: <b>${{r.personas}}</b> | Hogares: <b>${{r.hogares}}</b><br>` +
        `Barrio: ${{r.barrio}}`
    );
    idecsCluster.addLayer(m);
}});
map.addLayer(idecsCluster);

// ═══ Control de capas ═══
const layers = {{
    rep: repCluster,
    eval: evalGroup,
    rud: rudCluster,
    idecs: idecsCluster
}};

function toggleLayer(name) {{
    const chk = document.getElementById('chk_' + name);
    if (chk.checked) map.addLayer(layers[name]);
    else map.removeLayer(layers[name]);
}}
</script>
</body>
</html>"""

    # Guardar HTML
    html_key = f"{OUTPUT_PREFIX}/mapa_emergencia_cali.html"
    s3.put_object(
        Bucket=S3_BUCKET, Key=html_key,
        Body=html.encode("utf-8"), ContentType="text/html",
    )
    print(f"Mapa guardado: s3://{S3_BUCKET}/{html_key}")

    # URL pre-firmada (7 días)
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": html_key},
        ExpiresIn=604800,
    )

    return {
        "statusCode": 200,
        "body": {
            "mensaje": (
                f"Mapa generado: {len(reportes_js):,} reportes, "
                f"{len(eval_js)} evaluaciones, {len(rud_js):,} RUD×rep, "
                f"{len(rud_geo_data):,} RUD IDECS"
            ),
            "s3_key": html_key,
            "url": url,
        },
    }

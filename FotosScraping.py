import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse

# Página principal
base_url = "https://froilanpaez.com/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
}

# Subpáginas relevantes encontradas manualmente
subpaginas = [
    base_url,
    "https://froilanpaez.com/perfectamente-natural/",
    "https://froilanpaez.com/equipo-medico-de-especialistas/",
    "https://froilanpaez.com/servicio-estadia/",
    "https://froilanpaez.com/bichectomia/",
    "https://froilanpaez.com/tratamiento-papada/",
]

# Crear carpetas
os.makedirs("imagenes_froilan", exist_ok=True)
os.makedirs("videos_froilan", exist_ok=True)

descargadas = set()
contador = 0
contador_videos = 0

def descargar_archivo(url_archivo, carpeta, prefijo):
    global contador, contador_videos

    url_archivo = urljoin(base_url, url_archivo)
    nombre = os.path.basename(urlparse(url_archivo).path)
    if not nombre:
        return

    if url_archivo in descargadas:
        return

    ruta = os.path.join(carpeta, f"{prefijo}_{nombre}")
    try:
        contenido = requests.get(url_archivo, headers=headers).content
        with open(ruta, "wb") as f:
            f.write(contenido)
        descargadas.add(url_archivo)
        if carpeta == "imagenes_froilan":
            print(f"[IMG ✓] {url_archivo}")
            contador += 1
        else:
            print(f"[VIDEO ✓] {url_archivo}")
            contador_videos += 1
    except Exception as e:
        print(f"[✗] Error al descargar {url_archivo}: {e}")

def procesar_pagina(pagina_url):
    try:
        response = requests.get(pagina_url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Error en {pagina_url}: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, "html.parser")

        # Imágenes <img>, <source>, srcset, data-src
        for img in soup.find_all(["img", "source"]):
            for attr in ["src", "data-src", "srcset"]:
                src = img.get(attr)
                if src:
                    if " " in src:
                        src = src.split(" ")[0]
                    if src.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
                        descargar_archivo(src, "imagenes_froilan", f"{contador}")
                    elif src.endswith((".mp4", ".webm", ".ogg")):
                        descargar_archivo(src, "videos_froilan", f"{contador_videos}")

        # background-image en estilos inline
        for tag in soup.find_all(style=True):
            style = tag["style"]
            if "background-image" in style:
                start = style.find("url(")
                end = style.find(")", start)
                if start != -1 and end != -1:
                    url_fondo = style[start + 4:end].strip('\'"')
                    if url_fondo.endswith((".jpg", ".jpeg", ".png", ".webp")):
                        descargar_archivo(url_fondo, "imagenes_froilan", f"{contador}")

        # Etiquetas <video> con src o <source>
        for video in soup.find_all("video"):
            if video.get("src"):
                descargar_archivo(video["src"], "videos_froilan", f"{contador_videos}")
            for source in video.find_all("source"):
                if source.get("src"):
                    descargar_archivo(source["src"], "videos_froilan", f"{contador_videos}")
    except Exception as e:
        print(f"❌ Error en procesar_pagina({pagina_url}): {e}")

# Ejecutar scraping en cada subpágina
for pagina in subpaginas:
    print(f"\n🌐 Procesando: {pagina}")
    procesar_pagina(pagina)

print(f"\n✅ Total imágenes descargadas: {contador}")
print(f"✅ Total videos descargados: {contador_videos}")

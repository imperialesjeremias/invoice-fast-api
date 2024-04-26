from PyPDF2 import PdfReader, PdfWriter
from fpdf import FPDF
from pdf2image import convert_from_path
from io import BytesIO
import os
import base64
import shutil
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, UploadFile, File
from num2words import num2words
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import tempfile
import re
# from openai import OpenAI
# from fastapi.middleware.cors import CORSMiddleware
# from dotenv import load_dotenv

# load_dotenv()

# # Obtener la variable de entorno API_URL
# opnai_key = os.getenv("OPENAI_KEY")


app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:3000", 
]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE"],
#     allow_headers=["*"],
# )

# client = OpenAI(api_key=opnai_key)

app = FastAPI(
    title="Invoice Arartiri", 
    openapi_url="/api/v1/openapi.json",  
    version="1.0.0", 
    description="API para Aratiri",
    docs_url="/docs",
    redoc_url="/redoc"

)

output_folder = "output"


def thousandSeparator(number):
    number = round(number, 3)
    n = f"{number}".split(".")
    number_formatted = f"{int(n[0]):,}".replace(",", ".")
    if len(n) > 1:
        decimal = int(n[1])
        if decimal != 0:
            number_formatted = f"{number_formatted},{decimal}"
    return number_formatted

@app.post("/invoice/")
async def get_invoice(file: UploadFile = File(...)):
    # Guardar el archivo en el sistema de archivos temporal
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        shutil.copyfileobj(file.file, tmpfile)
    print('tmpfile', file)
    # Obtener la ruta del archivo temporal
    tmpfile_path = tmpfile.name

    # Procesar el archivo PDF
    data = factura2(tmpfile_path)
    print(data)
    # os.remove(tmpfile_path)
    # _total_items = 0
    # _total_iva_10 = 0
    # _total_iva_5 = 0
    # _total_exentas = 0
    # for item in data["items"]:
    #     _total_items += item["cantidad"]
    #     _total_iva_10 += item["total_10"]
    #     _total_iva_5 += item["total_5"]
    #     _total_exentas += item["total_0"]

    # _iva_10 = round(_total_iva_10 / 11)
    # _iva_5 = 0
    # if _total_iva_5 > 0:
    #     _iva_5 = round(_total_iva_5 / 21)
    # _total_iva = _iva_10 + _iva_5
    # _total_general = _total_iva_10 + _total_iva_5 + _total_exentas


    # pdf = FPDF(orientation='P', unit='mm', format='A4')
    # pdf.add_page()
    # #ocupar toda la pagina
    # # pdf.image('output/page_1.jpg', x=1, y=1, w=216, h=356)
    # pdf.set_font("Arial", size=12)
    # pos_y_range = 0
    # post_x = 38.5
    # for i in range(0, 2):
    #     pdf.rect(6.5, post_x + pos_y_range, 193.5, 21) # pdf.rect(x, y, w, h)
    #     pdf.set_font("Arial", size=10)
    #     pdf.text(9, 5 + post_x + pos_y_range, txt=f"FECHA DE EMISIÓN: {data['ruc']}")
    #     pdf.text(90, 5 + post_x  + pos_y_range, txt="CONDICIÓN DE VENTA: CONTADO   (X)  Crédito ( )  DÍAS: ....")
    #     pdf.ln(4)
    #     pdf.text(9, 10 + post_x  + pos_y_range, txt=f"NOMBRE O RAZÓN SOCIAL: {data['razon_social']}")
    #     pdf.text(150, 10 + post_x  + pos_y_range, txt=f"RUC: {data['ruc']}")
    #     pdf.ln(4)
    #     pdf.text(9, 15 + post_x  + pos_y_range, txt="DIRECCIÓN: -")
    #     pdf.text(150, 15 + post_x  + pos_y_range, txt="EMAIL: -")
    #     pdf.ln(4)
    #     pdf.text(9, 20 + post_x  + pos_y_range, txt="NOTA DE REMISIÓN NRO: -")
    #     pdf.text(150, 20  + post_x  + pos_y_range, txt="TELÉFONO: -")

    #     #lineas horizontales 
    #     pdf.line(6.5, 6.5 + post_x  + pos_y_range, 199.5, 6.5 + post_x  + pos_y_range)
    #     pdf.line(6.5, 11.5 + post_x  + pos_y_range, 199.5, 11.5 + post_x  + pos_y_range)
    #     pdf.line(6.5, 16.5 + post_x  + pos_y_range, 199.5, 16.5 + post_x  + pos_y_range)


    #     pdf.line(6.5, 27 + post_x  + pos_y_range, 199.5, 27 + post_x  + pos_y_range)
    #     pdf.line(125, 24 + post_x  + pos_y_range, 199.5, 24 + post_x  + pos_y_range)

    #     pdf.line(6.5, 75.5 + post_x  + pos_y_range, 199.5, 75.5 + post_x  + pos_y_range)
    #     pdf.line(6.5, 80 + post_x  + pos_y_range, 199.5, 80 + post_x  + pos_y_range)#sub total?
    #     pdf.line(6.5, 84 + post_x  + pos_y_range, 175, 84 + post_x  + pos_y_range)

        
    #     #lineas verticales
    #     pdf.line(30, 21 + post_x  + pos_y_range, 30, 75.5 + post_x  + pos_y_range)#OK
    #     pdf.line(100, 21 + post_x  + pos_y_range, 100, 75.5 + post_x  + pos_y_range)
    #     pdf.line(125, 21 + post_x  + pos_y_range, 125, 80 + post_x  + pos_y_range)
    #     pdf.line(151, 24 + post_x  + pos_y_range, 151, 80 + post_x  + pos_y_range)
    #     pdf.line(175, 24 + post_x  + pos_y_range, 175, 88 + post_x  + pos_y_range)

    #     pdf.rect(6.5, 21 + post_x  + pos_y_range, 193.5, 67)

    #     pdf.text(10, 25.5 + post_x  + pos_y_range, txt="CANTIDAD")
    #     pdf.text(35, 25.5 + post_x  + pos_y_range, txt="DESCRIPCIÓN",)
    #     pdf.text(102, 25.5 + post_x  + pos_y_range, txt="P UNIT.")
    #     pdf.set_font("Arial", size=8)
    #     pdf.text(145, 23.5 + post_x  + pos_y_range, txt="   VALOR DE VENTA")
    #     pdf.ln(2)
    #     pdf.set_font("Arial", size=8)
    #     pdf.text(127, 26.3 + post_x  + pos_y_range, txt="EXENTAS")
    #     pdf.text(158, 26.3 + post_x  + pos_y_range,  txt="   5%")
    #     pdf.text(190, 26.3 + post_x  + pos_y_range, txt="   10%")

    #     count = 0
    #     y_position = 96
    #     pdf.ln(4)
    #     data["items"] = list(data["items"])
    #     for item in data["items"]:
    #         cantidad = item['cantidad'] if item['cantidad'] > 0 else '1'
    #         pdf.text(20, 30 + post_x +count + pos_y_range, txt=f"   {cantidad}")
    #         pdf.text(32, 30 + post_x +count + pos_y_range, txt=f"   {item['descripcion']}")
    #         pdf.text(107, 30 + post_x +count + pos_y_range, txt=thousandSeparator(item['precio_unitario']))
    #         pdf.text(127, 30 + post_x +count + pos_y_range, txt=f"   {item['total_0'] if item['total_0'] > 0 else ''}")
    #         pdf.text(154, 30 + post_x +count + pos_y_range, txt=f"   {item['total_5'] if item['total_5'] > 0 else ''}")
    #         pdf.text(187, 30 + post_x +count + pos_y_range, txt=f"   {thousandSeparator(item['total_10']) if item['total_10'] > 0 else ''}")
    #         count += 3.4 
    #         y_position += 3 
    #     pdf.ln(6)
    #     pdf.text(9, 79 + post_x + pos_y_range, txt="   SUBTOTALES")
    #     pdf.text(110, 79 + post_x + pos_y_range, txt=f"{thousandSeparator(_total_exentas) if _total_exentas > 0 else ''}")
    #     pdf.text(140, 79 + post_x + pos_y_range, txt=f"{thousandSeparator(_total_iva_5) if _total_iva_5 > 0 else ''}")
    #     pdf.text(184, 79 + post_x + pos_y_range, txt=f"{thousandSeparator(_total_iva_10) if _total_iva_10 > 0 else ''}")
    #     pdf.ln(4)
    #     pdf.text(9, 83 + post_x + pos_y_range, txt=f"   TOTAL A PAGAR GUARANIES: {num2words(_total_general, lang='es')}")
    #     pdf.set_font("Arial", size=12)
    #     pdf.text(180, 85 + post_x + pos_y_range, txt=f"{thousandSeparator(_total_general)}")
    #     pdf.ln(2)
    #     pdf.set_font("Arial", size=8)
    #     pdf.text(9, 87 + post_x + pos_y_range, txt=f"   LIQUIDACION DEL IVA (10%): {thousandSeparator(_iva_10)}                           (5%): {thousandSeparator(_iva_5)}                     TOTAL IVA: {thousandSeparator(_total_iva)}")
    #     pdf.ln(4)
    #     pos_y_range = 148

    # pdf.output(dest="S").encode("latin1")
    # pdf_bytes = pdf.output(dest="S").encode("latin1")
    # headers = {"Content-Disposition": 'attachment; filename="plantilla-factura.pdf"'}
    
    # # Devolver la respuesta como una StreamingResponse
    # return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    clear_folder(output_folder)
    # Crear una ruta temporal para guardar el archivo cargado
    temp_file_path = f"temp/{file.filename}"  # Considera usar un directorio temporal adecuado
    os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)

    # Guardar el archivo cargado temporalmente
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Ahora que el archivo está guardado en el sistema de archivos, puedes usar su ruta
    convert_pdf_to_images(temp_file_path, output_folder)
    # process_images(output_folder)
    

    # Opcional: eliminar el archivo temporal después de convertirlo
    os.remove(temp_file_path)


    return 'Procesado con éxito'

@app.get("/hello")
async def hello():
    return {"message": "Hello World"}

def convert_pdf_to_images(pdf_path, output_folder):

    os.makedirs(output_folder, exist_ok=True)

    # Convertir el PDF a una lista de objetos de imagen
    images = convert_from_path(pdf_path, dpi=600)  # Puedes ajustar el dpi según tus necesidades

    # Guardar cada página como una imagen en el directorio de salida
    for i, image in enumerate(images):
        filename = f"{output_folder}/page_{i + 1}.jpg"
        image.save(filename, 'JPEG')

    print(f"Conversión completada. {len(images)} imágenes guardadas en {output_folder}.")



def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Eliminar archivos y enlaces
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Eliminar directorios y su contenido
        except Exception as e:
            print(f'Error al eliminar {file_path}. Razón: {e}')



def preprocess(image):
    # Convertir a escala de grises
    img = image.convert('L')  

    # Aumentar contraste
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)

    # Reducir ruido 
    img = img.filter(ImageFilter.MedianFilter())
    # Mejora del contraste
    img = np.array(img)
    img = cv2.equalizeHist(img)

    # Eliminación de artefactos y manchas
    edges = cv2.Canny(img, 30, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 100:
            cv2.drawContours(img, [contour], -1, (0, 0, 0), -1)

    # Umbralizar
    thresh = 200
    img = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY)[1]

    return img


# def process_with_gpt(file):
#     pages = convert_from_path(file)
#     texto_completo = ''
#     for page in pages:
#         image = preprocess(page)
#         texto_pagina = pytesseract.image_to_string(image)
#         texto_completo += texto_pagina + '\n\n'
    
#     completion = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=[{ "role": "system", "content": "Ordena el texto que recibiras de esta manera {'fecha': '01/01/2024', 'condicion': 'Efectivo', 'razon_social': 'FREDY RUMILDO', 'ruc': '4146518-0', 'direccion': '', 'telefono': '', 'items': [{'descripcion': 'TRAPO SECADO TWISTED GENERICO', 'cantidad': 1, 'precio_unitario': 35000, 'total_0': 0, 'total_5': 0, 'total_10': 35000}, {'descripcion': 'APLICADOR DE ESPUMA X2', 'cantidad': 1, 'precio_unitario': 15000, 'total_0': 0, 'total_5': 0, 'total_10': 15000}, {'descripcion': 'VONIXX LAVA AUTO 1.5L', 'cantidad': 1, 'precio_unitario': 30000, 'total_0': 0, 'total_5': 0, 'total_10': 30000}, {'descripcion': 'GUANTE LAVADO PREMIUN', 'cantidad': 1, 'precio_unitario': 30000, 'total_0': 0, 'total_5': 0, 'total_10': 30000}, {'descripcion': 'VONIXX PNEU PRETINHO 1.5L', 'cantidad': 1, 'precio_unitario': 40000, 'total_0': 0, 'total_5': 0, 'total_10': 40000}]}, debes podes ordenar el texto que recibiras en ese formato y formatea la fecha as DD/MM/YY" },
#                   {"role": "user", "content": texto_completo}
#                  ]
#     )
        
#     print(completion.choices[0].message.content)
#     return eval(completion.choices[0].message.content)


         
def process_pdf(file):
    pages = convert_from_path(file)
    texto_completo = ''
    data = {
        "fecha": "",
        "condicion": "",
        "razon_social": "",
        "ruc": "",
        "direccion": "",
        "telefono": "",
        "items": []
    }
    for page in pages:
        image = preprocess(page)
        texto_pagina = pytesseract.image_to_string(image)
        texto_completo += texto_pagina + '\n\n'

    cabecera_match = re.search(r"Fecha de transaccién (.*?)Contacto (.*?)NIT del Contacto (.*?)Vendedor (.*?)Método de pago (.*?)\n", texto_completo, re.DOTALL)
    if cabecera_match:
        fecha_transaccion = cabecera_match.group(1).strip()
        contacto = cabecera_match.group(2).strip()
        nit_contacto = cabecera_match.group(3).strip()
        vendedor = cabecera_match.group(4).strip()
        metodo_pago = cabecera_match.group(5).strip()

        data["fecha"] = fecha_transaccion
        data["condicion"] = metodo_pago
        data["razon_social"] = contacto
        data["ruc"] = nit_contacto
        
    else:
        print("Información de la cabecera no encontrada.")

    # Extraer toda la información de productos
    productos_info_match = re.search(r"Productos Cantidad Precio unitario Valor\n([\s\S]+?)(?=\nTotal:)", texto_completo)

    if productos_info_match:
        productos_info = productos_info_match.group(1).strip().split("\n")
        productos = []
        for producto_info in productos_info:
            # Asumiendo el formato: [Nombre] [Cantidad] $[Precio unitario] $[Valor]
            # Se ajusta para manejar mejor los espacios inesperados
            match = re.match(r"(.*?)\s+(\d+)\s*\$\s*([\d,]+)\s*\$\s*([\d,]+)", producto_info)
            if match:
                descripcion = match.group(1)
                cantidad = int(match.group(2))
                precio_unitario = int(match.group(3).replace(",", "").replace("$", ""))
                total = int(match.group(4).replace(",", "").replace("$", ""))
                items = {
                    "descripcion": descripcion,
                    "cantidad": cantidad,
                    "precio_unitario": precio_unitario,
                    "total_10": precio_unitario,  # 10% si no hay enviar 0 pero enviar
                    "total_5": 0,  # 5% si no hay enviar 0 pero enviar
                    "total_0": 0  # exentas
                }
                productos.append(items)
                
        data["items"] = productos
        # Imprimir detalles de productos
    else:
        print("Información de productos no encontrada.")
    return data

# procesa la factura 6
def factura6(file):
    pages = convert_from_path(file)
    texto_completo = ''
    data = {
        "fecha": "",
        "Contacto": "",
        "razon_social": "",
        "vendedor": "",
        "metodo de pago": "",
        "estado": "",
        "numero de transacción": "",
        "direccion": "",
        "telefono": "",
        "items": [],
    }

    for page in pages:
        image = preprocess(page)
        texto_pagina = pytesseract.image_to_string(image)
        texto_completo += texto_pagina
        

    # # buscar fecha
    fecha = re.search(r"(\d{1,2}\s(?:|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{4}\s-\s(\d{1,2}:\d{2}))", texto_completo)
    data["fecha"] = fecha.group(1)

    match = re.search(r"\n([\w\.\s]*)\n([\d\-]*)\n*([\w\s\é]*)\n(Efectivo)\n*([\w]+)\n*([\d]+)", texto_completo, re.IGNORECASE)
    data["Contacto"] = match.group(1)
    data['razon_social'] = match.group(2)
    data["vendedor"] = match.group(3)
    data['metodo de pago'] = match.group(4)
    data['estado'] = match.group(5)
    data['numero de transacción'] = match.group(6)

    productos_y_precios = re.search(r"Productos\n([\s\S]+?)(?=\nTotal:)[\s\S]*?(?:Precio unitario|Precio)\s[\w]*\n((?:[$?\d]*\s)*[$?\d]*)\s\n?([$?\d]+)", texto_completo, re.IGNORECASE)
    items = {"Productos": "", "Precio": ""}
    items["Productos"] = productos_y_precios.group(1)
    items["Precio"] = productos_y_precios.group(2)
   
    if productos_y_precios:
        productos = productos_y_precios.group(1).strip().split("\n")
        for producto in productos:
            if producto == "":
                productos.remove(producto)
            else:
                continue
        
        precios = productos_y_precios.group(2).strip().split("\n")
        for precio in precios:
            if precio == "":
                precios.remove(precio)
            else:
                continue

        productos_descripcion_y_precio = []
        for i in range(len(productos)):
            productos_descripcion_y_precio.append(productos[i] + " " + precios[i])
    if productos_descripcion_y_precio:
        productos = []
        for producto_info in productos_descripcion_y_precio:
            match = re.match(r"([\w\s\/]+)([\d\$\s]+)", producto_info)
            if match:
                descripcion = match.group(1)
                precio_unitario = match.group(2).replace(",", "").replace("$", "")
                items = {
                    "descripcion": descripcion,
                    "cantidad": 0,
                    "precio_unitario": precio_unitario,
                    "total_10": precio_unitario,  # 10% si no hay enviar 0 pero enviar
                    "total_5": 0,  # 5% si no hay enviar 0 pero enviar
                    "total_0": 0  # exentas
                }
                productos.append(items)
                
        data["items"] = productos
    return data

#factura 3
def factura3(file):
    pages = convert_from_path(file)
    texto_completo = ''
    data = {
        "fecha": "",
        "Contacto": "",
        "razon_social": "",
        "vendedor": "",
        "metodo de pago": "",
        "estado": "",
        "numero de transacción": "",
        "direccion": "",
        "telefono": "",
        "items": [],
    }

    for page in pages:
        image = preprocess(page)
        texto_pagina = pytesseract.image_to_string(image)
        texto_completo += texto_pagina
        

    # # buscar fecha
    fecha = re.search(r"(\d{1,2}\s(?:|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{4}\s-\s(\d{1,2}:\d{2}))", texto_completo)
    data["fecha"] = fecha.group(1)

    match = re.search(r"(Contacto)\s([\w\s]*)\n(NIT del Contacto)\s([\d\-]+)\n(Vendedor)\s([\w\s\é]*)\n*(Método de pago)\s([\w]*)\n*(Estado)\s([\w]+)\n(Ndmero de transaccién|número de transacción)\s([\d]+)\n", texto_completo, re.IGNORECASE)
    data["Contacto"] = match.group(2)
    data['razon_social'] = match.group(4)
    data["vendedor"] = match.group(6)
    data['metodo de pago'] = match.group(8)
    data['estado'] = match.group(10)
    data['numero de transacción'] = match.group(12)

    productos_y_precios = re.search(r"unitario\n*([\w\s\d]*)\s\$([\d]*\s\$[\d]*)\n*\w*\n*(Total:)\n*([\d\$]+)", texto_completo, re.IGNORECASE)
    items = {"Productos": "", "Precio": ""}
    items["Productos"] = productos_y_precios.group(1)
    items["Precio"] = productos_y_precios.group(2)
   
    if productos_y_precios:
        productos = productos_y_precios.group(1).strip().split("\n")
        for producto in productos:
            if producto == "":
                productos.remove(producto)
            else:
                continue
        
        precios = productos_y_precios.group(2).strip().split("\n")
        for precio in precios:
            if precio == "":
                precios.remove(precio)
            else:
                continue

        productos_descripcion_y_precio = []
        for i in range(len(productos)):
            productos_descripcion_y_precio.append(productos[i] + " " + precios[i])

        print(productos_descripcion_y_precio)
    if productos_descripcion_y_precio:
        productos = []
        for producto_info in productos_descripcion_y_precio:
            match = re.search(r"([\w\s\/]+)([\d\$\s]+)", producto_info)
            if match:
                descripcion = match.group(1)
                precio_unitario = match.group(2).replace(",", "").replace("$", "")
                items = {
                    "descripcion": descripcion,
                    "cantidad": 0,
                    "precio_unitario": precio_unitario,
                    "total_10": precio_unitario,  # 10% si no hay enviar 0 pero enviar
                    "total_5": 0,  # 5% si no hay enviar 0 pero enviar
                    "total_0": 0  # exentas
                }
                productos.append(items)
                
        data["items"] = productos
    text = f'''
    Fecha de transacción: {data["fecha"]}
    Contacto: {data["Contacto"]}
    Razon Social: {data["razon_social"]}
    Vendedor: {data["vendedor"]}
    Metodo de pago: {data["metodo de pago"]}
    Estado: {data["estado"]}
    Numero de transacción: {data["numero de transacción"]}
    '''
    total = 0
    for item in data["items"]:
        text += f"{item['descripcion']} - {item['precio_unitario']}"
        for precio in precios:
            precio_total = precio.split()[-1]
            if precio_total.replace(",", "").replace("$", "").isdigit():
               total += int(precio_total.replace(",", "").replace("$", ""))
            text += f"\nTotal: {total}"

    
    print(text)
    return data

# factura 2 y test3
def factura2(file):
    pages = convert_from_path(file)
    texto_completo = ''
    data = {
        "fecha": "",
        "Contacto": "",
        "razon_social": "",
        "vendedor": "",
        "metodo de pago": "",
        "estado": "",
        "numero de transacción": "",
        "direccion": "",
        "telefono": "",
        "items": [],
    }

    for page in pages:
        image = preprocess(page)
        texto_pagina = pytesseract.image_to_string(image)
        texto_completo += texto_pagina

    # # buscar fecha
    fecha = re.search(r"(\d{1,2}\s(?:|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{4}\s-\s(\d{1,2}:\d{2}))", texto_completo)
    data["fecha"] = fecha.group(1)

    match = re.search(r"\n([\w\s]*)\n([\d\-\s]+)\n*([\w\s\é\á\í\ú\ó\ñ]+)\n(Transferencia Bancaria|Efectivo)\n*(Pagada)\n*([\d]+)", texto_completo, re.IGNORECASE)
    data["Contacto"] = match.group(1)
    data['razon_social'] = match.group(2)
    data["vendedor"] = match.group(3)
    data['metodo de pago'] = match.group(4)
    data['estado'] = match.group(5)
    data['numero de transacción'] = match.group(6)

    productos_y_precios = re.search(r"Productos\n([\s\S]+?)(?=\nTotal:)[\s\S]*?(?:Precio unitario|Precio)\s[\w]*\n((?:[$?\d]*\s)*[$?\d]*)\s\n?([$?\d]+)", texto_completo, re.IGNORECASE)
    items = {"Productos": "", "Precio": ""}
    items["Productos"] = productos_y_precios.group(1)
    items["Precio"] = productos_y_precios.group(2)

    if productos_y_precios:
        productos = productos_y_precios.group(1).strip().split("\n")
        for producto in productos:
            if producto == "":
                productos.remove(producto)
            else:
                continue
        
        precios = productos_y_precios.group(2).strip().split("\n")
        for precio in precios:
            if precio == "":
                precios.remove(precio)
            else:
                continue

        productos_descripcion_y_precio = []
        for i in range(len(productos)):
            productos_descripcion_y_precio.append(productos[i] + " " + precios[i])

    if productos_descripcion_y_precio:
        productos = []
        for producto_info in productos_descripcion_y_precio:
            match = re.search(r"([\w\s\/\d]*)([\$\d\s]*)", producto_info)
            if match:
                descripcion = match.group(1)
                precio_unitario = match.group(2).replace(",", "").replace("$", "")
                items = {
                    "descripcion": descripcion,
                    "cantidad": 0,
                    "precio_unitario": precio_unitario,
                    "total_10": precio_unitario,  # 10% si no hay enviar 0 pero enviar
                    "total_5": 0,  # 5% si no hay enviar 0 pero enviar
                    "total_0": 0  # exentas
                }
                productos.append(items)
                
        data["items"] = productos
    text = f'''
    Fecha de transacción: {data["fecha"]}
    Contacto: {data["Contacto"]}
    Razon Social: {data["razon_social"]}
    Vendedor: {data["vendedor"]}
    Metodo de pago: {data["metodo de pago"]}
    Estado: {data["estado"]}
    Numero de transacción: {data["numero de transacción"]}
    '''
    total = 0
    for item in data["items"]:
        text += f"{item['descripcion']} - {item['precio_unitario']}\n"
        for precio in precios:
            precio_total = precio.split()[-1]
            total += int(precio_total.replace(",", "").replace("$", ""))
    text += f"Total: {total}"
    print(text)

    return data
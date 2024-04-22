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


app = FastAPI()

app = FastAPI(
    title="Invoice Arartiri", 
    openapi_url="/api/v1/openapi.json",  
    version="1.0.0", 
    description="API para la Aratiri",
    docs_url="/docs",
    redoc_url="/redoc"

)

output_folder = "output"  # Asegúrate de que este directorio existe o crea uno dinámicamente


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

    # Obtener la ruta del archivo temporal
    tmpfile_path = tmpfile.name

    # Procesar el archivo PDF
    data = process_pdf(tmpfile_path)
    # print('datas', data)
    # Eliminar el archivo temporal
    os.remove(tmpfile_path)

    # Crear un PDF nuevo usando FPDF
    #formato a4
    # data = {
    #     "fecha": "18-02-2024",
    #     "condicion": "Contado",
    #     "razon_social": "JomaTech Co",
    #     "ruc": "5708247-2",
    #     "direccion": "Cnel Toledo c/ Gral Bruguez",
    #     "telefono": "0984266644",
    #     "items": [
    #         {
    #             "descripcion": "Producto 1",
    #             "cantidad": 2,
    #             "precio_unitario": 100000,
    #             "total_10": 200000, #10% si no hay enviar 0 pero enviar
    #             "total_5": 0,#5% si no hay enviar 0 pero enviar
    #             "total_0": 0 #exentas
                
    #         },
    #     ],
    # }
  
    
    _total_items = 0
    _total_iva_10 = 0
    _total_iva_5 = 0
    _total_exentas = 0
    for item in data["items"]:
        _total_items += item["cantidad"]
        _total_iva_10 += item["total_10"]
        _total_iva_5 += item["total_5"]
        _total_exentas += item["total_0"]

    _iva_10 = round(_total_iva_10 / 11)
    _iva_5 = 0
    if _total_iva_5 > 0:
        _iva_5 = round(_total_iva_5 / 21)
    _total_iva = _iva_10 + _iva_5
    _total_general = _total_iva_10 + _total_iva_5 + _total_exentas


    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    #ocupar toda la pagina
    # pdf.image('output/page_1.jpg', x=1, y=1, w=210, h=295)
    pdf.set_font("Arial", size=12)
    pdf.rect(11, 48, 190.2, 20) # pdf.rect(x, y, w, h)
    pdf.set_font("Arial", size=10)
    pdf.cell(70, 85, txt="   Fecha: 18-02-2024", ln=0, align="L")
    pdf.cell(70, 85, txt="   Condición: Contado   X  Crédito", ln=0, align="L")
    pdf.ln(4)
    pdf.cell(70, 88, txt="   Razón Social: JomaTech Co", ln=0, align="L")
    pdf.cell(70, 88, txt="   RUC: 5708247-2", ln=0, align="L")
    pdf.ln(4)
    pdf.cell(70, 91, txt="   Dirección: Cnel Toledo c/ Gral Bruguez", ln=0, align="L")
    pdf.cell(70, 91, txt="   Teléfono: 0984266644", ln=0, align="L")
    pdf.ln(6)

    #lineas horizontales 
    pdf.line(11, 75, 201.2, 75)
    pdf.line(110, 72.2, 201.2, 72.2)
    pdf.line(11, 113, 201.2, 113)
    pdf.line(11, 117, 201.2, 117)
    pdf.line(11, 122, 165, 122)

    
    #lineas verticales
    pdf.line(30, 69, 30, 113)
    pdf.line(85, 69, 85, 113)
    pdf.line(110, 69, 110, 117)
    pdf.line(140, 72.5, 140, 117)
    pdf.line(170, 72.5, 170, 117)
    pdf.line(165, 117, 165, 126)

    pdf.cell(30, 94, txt="   Cantidad", ln=0, align="L")
    pdf.cell(45, 94, txt="   Descripción", ln=0, align="L")
    pdf.cell(30, 94, txt="   Precio Unit.", ln=0, align="L")
    pdf.set_font("Arial", size=8)
    pdf.cell(80, 92.5, txt="   Valor de Venta", ln=0, align="C")
    pdf.ln(2)
    pdf.set_font("Arial", size=8)
    pdf.cell(120, 95, txt="Exentas", ln=0, align="R")
    pdf.cell(45, 95, txt="   5%", ln=0, align="C")
    pdf.cell(30, 95, txt="   10%", ln=0, align="L")
    pdf.rect(11, 69, 190.2, 57)
    count = 0
    y_position = 96
    pdf.ln(4)
    for item in data["items"]:
        cantidad = item['cantidad'] if item['cantidad'] > 0 else '1'
        pdf.text(20, 78.2+count, txt=f"   {cantidad}")
        pdf.text(30, 78.2+count, txt=f"   {item['descripcion']}")
        pdf.text(97, 78.2+count, txt=f"   {thousandSeparator(item['precio_unitario'])}")
        pdf.text(110, 78.2+count, txt=f"   {item['total_0'] if item['total_0'] > 0 else ''}")
        pdf.text(140, 78.2+count, txt=f"   {item['total_5'] if item['total_5'] > 0 else ''}")
        pdf.text(187, 78.2+count, txt=f"   {thousandSeparator(item['total_10']) if item['total_10'] > 0 else ''}")
        count += 4 
        y_position += 3 
    pdf.ln(12)
    pdf.cell(100, 147, txt="   SUBTOTALES", ln=0, align="L")
    pdf.cell(30, 147, txt=f"{thousandSeparator(_total_exentas) if _total_exentas > 0 else ''}", ln=0, align="R")
    pdf.cell(30, 147, txt=f"{thousandSeparator(_total_iva_5) if _total_iva_5 > 0 else ''}", ln=0, align="R")
    pdf.cell(31, 147, txt=f"{thousandSeparator(_total_iva_10) if _total_iva_10 > 0 else ''}", ln=0, align="R")
    pdf.ln(4)
    pdf.cell(150, 149, txt=f"   TOTAL A PAGAR Gs: {num2words(_total_general, lang='es')}", ln=0, align="L")
    pdf.set_font("Arial", size=12)
    pdf.cell(60, 151, txt=f"{thousandSeparator(_total_general)}", ln=0, align="C")
    pdf.ln(2)
    pdf.set_font("Arial", size=8)
    pdf.cell(120, 152, txt=f"   LIQUIDACION DEL IVA (10%): {thousandSeparator(_iva_10)}                           (5%): {thousandSeparator(_iva_5)}                     TOTAL IVA: {thousandSeparator(_total_iva)}" , ln=0, align="L")
    pdf.ln(4)
    ## segunda factura 
    pdf.rect(11, 180, 190.2, 20)
    pdf.set_font("Arial", size=10)
    pdf.text(12, 185, txt="   Fecha: 18-02-2024")
    pdf.text(90, 185, txt="   Condición: Contado   X  Crédito")
    pdf.ln(4)
    pdf.text(12, 192, txt="   Razón Social: JomaTech Co")
    pdf.text(90, 192, txt="   RUC: 5708247-2")
    pdf.ln(4)
    pdf.text(12, 198, txt="   Dirección: Cnel Toledo c/ Gral Bruguez")
    pdf.text(90, 198, txt="   Teléfono: 0984266644")
    pdf.ln(6)

    #lineas horizontales 
    pdf.line(11, 75+132, 201.2, 75+132)
    pdf.line(110, 72.2+132, 201.2, 72.2+132)
    pdf.line(11, 113+132, 201.2, 113+132)
    pdf.line(11, 117+132, 201.2, 117+132)
    pdf.line(11, 122+132, 165, 122+132)
    pdf.rect(11, 201, 190.2, 57)
    #lineas verticales
    pdf.line(30, 69+132, 30, 113+132)
    pdf.line(85, 69+132, 85, 113+132)
    pdf.line(110, 69+132, 110, 117+132)
    pdf.line(140, 72.5+132, 140, 117+132)
    pdf.line(170, 72.5+132, 170, 117+132)
    pdf.line(165, 117+132, 165, 126+132)

    pdf.text(12, 94+111.5, txt="   Cantidad")
    pdf.text(40, 94+111.5, txt="   Descripción")
    pdf.text(88, 94+111.5, txt="   Precio Unit.")
    pdf.set_font("Arial", size=8)
    pdf.text(140, 92+111.5, txt="   Valor de Venta")
    pdf.ln(2)
    pdf.set_font("Arial", size=8)
    pdf.text(120, 95+111.5, txt="Exentas")
    pdf.text(145, 95+111.5, txt="   5%")
    pdf.text(180, 95+111.5, txt="   10%")
    count = 0
    y_position = 96
    pdf.ln(4)
    for item in data["items"]:
        pdf.text(20, 98+111.5+count, txt=f"   {item['cantidad']}")
        pdf.text(30, 98+111.5+count, txt=f"   {item['descripcion']}")
        pdf.text(97, 98+111.5+count, txt=f"   {thousandSeparator(item['precio_unitario'])}")
        pdf.text(110, 98+111.5+count, txt=f"   {item['total_0'] if item['total_0'] > 0 else ''}")
        pdf.text(140, 98+111.5+count, txt=f"   {item['total_5'] if item['total_5'] > 0 else ''}")
        pdf.text(187, 98+111.5+count, txt=f"   {thousandSeparator(item['total_10']) if item['total_10'] > 0 else ''}")
        count += 4 
        y_position += 3  
    pdf.text(12, 137+111.5, txt="   SUBTOTALES")
    pdf.text(110, 137+111.5, txt=f"{thousandSeparator(_total_exentas) if _total_exentas > 0 else ''}")
    pdf.text(140, 137+111.5, txt=f"{thousandSeparator(_total_iva_5) if _total_iva_5 > 0 else ''}")
    pdf.text(189, 137+111.5, txt=f"{thousandSeparator(_total_iva_10) if _total_iva_10 > 0 else ''}")
    pdf.ln(4)
    pdf.text(12, 141+111.5, txt=f"   TOTAL A PAGAR Gs: {num2words(_total_general, lang='es')}")
    pdf.set_font("Arial", size=12)
    pdf.text(180, 143+111.5, txt=f"{thousandSeparator(_total_general)}")
    pdf.ln(2)
    pdf.set_font("Arial", size=8)
    pdf.text(12, 146+111.5, txt=f"   LIQUIDACION DEL IVA (10%): {thousandSeparator(_iva_10)}                           (5%): {thousandSeparator(_iva_5)}                     TOTAL IVA: {thousandSeparator(_total_iva)}")
    pdf.ln(4)

    # Guardar el PDF generado en un archivo temporal
    pdf.output(dest="S").encode("latin1")
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    headers = {"Content-Disposition": 'attachment; filename="tuto1.pdf"'}
    return StreamingResponse(
        BytesIO(pdf_bytes), media_type="application/pdf", headers=headers
    )  

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
    nombres_productos = []

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
        # print('dataaa', data)
        # Imprimir detalles de productos
    else:
        print("Información de productos no encontrada.")
    
    return data

def case_two(file):
    pages = convert_from_path(file)
    texto_completo = ''
    data = {
        "fecha": "",
        "condicion": "",
        "razon_social": "",
        "ruc": "",
        "direccion": "",
        "telefono": "",
        "items": [],
    }

    for page in pages:
        image = preprocess(page)
        texto_pagina = pytesseract.image_to_string(image)
        texto_completo += texto_pagina
        print(texto_completo)

    # # buscar fecha
    fecha = re.search(r"(\d{1,2}\s(?:|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{4}\s-\s(\d{1,2}:\d{2}))", texto_completo)
    data["fecha"] = fecha.group(1)

    # # condicion
    metodo_pago = re.search(r"(Efectivo|Transferencia Bancaria)", texto_completo)
    data["condicion"] = metodo_pago.group(1)

    # # razon social y ruc
    razon_and_ruc = re.search(r"(\d{8}-\d{1})\n*(.*)", texto_completo)
    data["razon_social"] = razon_and_ruc.group(2)
    data["ruc"] = razon_and_ruc.group(1)

    productos_y_precios = re.search(r"Productos\n([\s\S]+?)(?=\nTotal:)[\s\S]*?(?:Precio unitario|Precio)\s[\w]*\n((?:[$?\d]*\s)*[$?\d]*)\s\n?([$?\d]+)", texto_completo)
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
            # Asumiendo el formato: [Nombre] [Cantidad] en este caso no hay $[Precio unitario] $[Valor]
            # Match directo a los valores esperados
            match = re.match(r"(.*?)([\w\s\/]*)\s*\$\s*([\d,]+)\s\$\s*([\d,]+)", producto_info)
            if match:
                descripcion = match.group(2)
                # cantidad = int(match.group(2))
                precio_unitario = int(match.group(3).replace(",", "").replace("$", ""))
                # total = int(match.group(4).replace(",", "").replace("$", ""))
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
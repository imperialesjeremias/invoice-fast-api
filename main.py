from PyPDF2 import PdfReader, PdfWriter
from fpdf import FPDF
from io import BytesIO
import os
from fastapi.responses import StreamingResponse
from fastapi import FastAPI
from num2words import num2words


app = FastAPI()

app = FastAPI(
    title="Invoice Arartiri", 
    openapi_url="/api/v1/openapi.json",  
    version="1.0.0", 
    description="API para la Aratiri",
    docs_url="/docs",
    redoc_url="/redoc"

)


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
async def get_invoice(data: dict):
    """Agrega el contenido a la factura"""
    # Crear un PDF nuevo usando FPDF
    #formato a4
    data = {
        "fecha": "18-02-2024",
        "condicion": "Contado",
        "razon_social": "JomaTech Co",
        "ruc": "5708247-2",
        "direccion": "Cnel Toledo c/ Gral Bruguez",
        "telefono": "0984266644",
        "items": [
            {
                "descripcion": "Producto 1",
                "cantidad": 2,
                "precio_unitario": 100000,
                "total_10": 200000, #10% si no hay enviar 0 pero enviar
                "total_5": 0,#5% si no hay enviar 0 pero enviar
                "total_0": 0 #exentas
                
            },
            {
                "descripcion": "Producto 2",
                "cantidad": 1,
                "precio_unitario": 150000,
                "total_10": 150000, #10% si no hay enviar 0 pero enviar
                "total_5": 0,#5% si no hay enviar 0 pero enviar
                "total_0": 0 #exentas
            },
            {
                "descripcion": "Producto 2",
                "cantidad": 1,
                "precio_unitario": 150000,
                "total_10": 150000, #10% si no hay enviar 0 pero enviar
                "total_5": 0,#5% si no hay enviar 0 pero enviar
                "total_0": 0 #exentas
            }
        ],
    }

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
    pdf.image("factura_template.jpg", x=1, y=1, w=210, h=295)
    pdf.set_font("Arial", size=12)
    pdf.rect(11, 48, 190.2, 20) # pdf.rect(x, y, w, h)
    pdf.set_font("Arial", size=10)
    pdf.cell(70, 85, txt="   Fecha: 18-02-2024", ln=0, align="L")
    pdf.cell(70, 85, txt="   Condición: Contado   X  Crédito", ln=0, align="L")
    pdf.ln(4)
    pdf.cell(70, 88, txt="   Razón Social: JomaTech Co", ln=0, align="L")
    pdf.cell(70, 88, txt="   RUC: 5708247-2", ln=0, align="L")
    pdf.ln(4)
    pdf.cell(100, 91, txt="   Dirección: Cnel Toledo c/ Gral Bruguez", ln=0, align="L")
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
        pdf.text(20, 78.2+count, txt=f"   {item['cantidad']}")
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
    pdf.text(110, 198, txt="   Teléfono: 0984266644")
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

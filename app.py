import io, os, base64
import psycopg2, qrcode
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from cryptography.fernet import Fernet

PG_HOST = os.getenv("PG_HOST")
PG_DB = os.getenv("PG_DB")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
FERNET_KEY = Fernet.generate_key().decode()
fernet = Fernet(FERNET_KEY.encode())

FONT_REG = "/usr/share/fonts/TTF/DejaVuSans.ttf"
FONT_BOLD= "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
LOGO_FN = "logo.png"

conn = psycopg2.connect(host=PG_HOST, dbname=PG_DB, user=PG_USER, password=PG_PASSWORD)
with conn.cursor() as cur:
    cur.execute("CREATE TABLE IF NOT EXISTS receipts (id SERIAL PRIMARY KEY, data TEXT);")
    conn.commit()

app = FastAPI()

class Party(BaseModel):
    name: str
    document: str
    bank: str
    agency: str
    account: str

class GenerateRequest(BaseModel):
    date: str
    time: str
    from_: Party = Field(..., alias="from")
    to: Party
    amount: str
    qr_payload: str
    transaction_id: str

def create_receipt_image(data: dict) -> Image.Image:
    W, pad, header_h, section_h, qr_h, bottom_h = 600, 20, 100, 160, 180, 50
    height = header_h + section_h*2 + qr_h + bottom_h + pad*5

    img = Image.new("RGBA", (W, height), "#2b2b2b")
    draw = ImageDraw.Draw(img)
    f_b = ImageFont.truetype(FONT_BOLD, 22)
    f_r = ImageFont.truetype(FONT_REG, 18)

    logo = Image.open(LOGO_FN).convert("RGBA").resize((100, 30))

    logo_mask = logo.split()[3]  # canal alpha da imagem RGBA
    img.paste(logo, (pad, pad), logo_mask)
    draw.text((pad, 50), "Comprovante de pagamento", font=f_b, fill="white")
    draw.text((pad, 80), f"{data['date']} • {data['time']}", font=f_r, fill="white")

    def section(title, y, info):
        draw.text((pad,y), title, font=f_b, fill="gray")
        draw.rectangle([pad,y+30,pad+4,y+140],fill="#2ecc71")
        draw.text((pad+10,y+35),info['name'],font=f_r,fill="white")
        for i,field in enumerate(['document','bank','agency','account']):
            draw.text((pad+10,y+65+i*20),f"{field.title()}: {info[field]}",font=f_r,fill="gray")

    section("DE",120,data['from'])
    section("PARA",300,data['to'])

    qr = qrcode.make(data['qr_payload']).resize((120,120))
    img.paste(qr, (pad,480))

    draw.text((150,480), "Compartilhe a magia", font=f_b, fill="#2ecc71")
    draw.text((150,510), "Use o código ao lado para começar!", font=f_r, fill="white")
    draw.text((pad,height-40), f"ID: {data['transaction_id']}", font=f_r, fill="gray")

    return img.convert("RGB")

@app.post("/generate")
def generate(req: GenerateRequest):
    img = create_receipt_image(req.dict(by_alias=True))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    enc = fernet.encrypt(base64.b64encode(buf.getvalue())).decode()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO receipts (data) VALUES (%s) RETURNING id;",(enc,))
        rid = cur.fetchone()[0]
        conn.commit()
    return {"id":rid,"url":f"http://localhost:8000/receipt/{rid}"}

@app.get("/receipt/{rid}")
def receipt(rid:int):
    with conn.cursor() as cur:
        cur.execute("SELECT data FROM receipts WHERE id=%s;",(rid,))
        row = cur.fetchone()
    if not row: raise HTTPException(404)
    dec=base64.b64decode(fernet.decrypt(row[0]))
    return StreamingResponse(io.BytesIO(dec),media_type="image/png")
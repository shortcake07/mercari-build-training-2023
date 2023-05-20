import os
import logging
import pathlib
import json
import hashlib
import sqlite3
from fastapi import FastAPI, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.DEBUG
images = pathlib.Path(__file__).parent.resolve() / "images"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)
DB_PATH = pathlib.Path(__file__).parent.resolve() / "db" / "mercari.sqlite3"

def save_image(image: UploadFile):
    image_file = image.file.read()
    hash_image = hashlib.sha256(image_file).hexdigest()
    hash_name = hash_image + ".jpg"
    path = images / hash_name
    try:
         with open(path, "wb")as f:
              f.write(image_file)
    except FileNotFoundError:
         return ''
    return hash_name

def list_items():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    sql = "select items.id, items.name, category.name, items.image_filename\
        from items INNER JOIN category ON items.category_id = category.id"
    cur.execute(sql)
    items = cur.fetchall()
    con.commit()
    con.close()
    return items

def save_item(name:str, category:str, image_filename:str):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("INSERT OR IGNORE INTO category(name) values(?)", (category, ))

    cur.execute(f"select * from category where name = '{category}'")
    category_id = cur.fetchone()[0]
    receive_items = [(name, category_id, image_filename)]
    cur.executemany("INSERT INTO items(name, category_id, image_filename) values(?, ?, ?)", receive_items)
    con.commit()
    con.close()

def search_items(keyword:str):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    
    cur.execute(f"select * from items where name = '{keyword}'")
    items = cur.fetchall()
    con.commit()
    con.close()
    
    return items

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
def add_item(name: str = Form(...), category: str = Form(...), image: UploadFile = Form(...)):
    logger.info(f"Receive item: {name}, category: {category}, image:{image.filename}")
    
    hash_name = save_image(image)
    save_item(name, category, hash_name)
 
    return {"message": f"item received: {name}"}

@app.get("/items")
def read_items():
    items = list_items()
    return items

@app.get("/items/{item_id}")
def get_item(item_id: int):
    try:
        item = list_items()[item_id - 1]
    except IndexError:
        return {"message":"item not found"}
    except ValueError:
        return {"message":"ValueError"}
    except FileNotFoundError:
        return {"message":"FileNotFoundError"}
    return item

@app.get("/image/{image_filename}")
async def get_image(image_filename):
    # Create image path
    image = images / image_filename

    if not image_filename.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)

@app.get("/search")
def get_items(keyword: str):
    items = search_items(keyword)
    if items is None:
        return {"message":"item not found"}

    return items
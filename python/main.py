import os
import logging
import pathlib
import json
import hashlib
from fastapi import FastAPI, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "images"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

def save_image(image: UploadFile):
    image_file = image.file.read()
    hash_image = hashlib.sha256(image_file).hexdigest()
    hash_name = hash_image + ".jpg"
    path = images / hash_name
    try:
         with open(path, "wb")as f:
              f.write(image_file)
    except FileNotFoundError:
         return ;
    return hash_name

def list_items():
	with open("./items.json", "r")as f:
            items = json.load(f)
            return items

def save_item(name:str, category:str, image_filename:str):
     try:
          items_data = list_items()
     except (FileNotFoundError, json.decoder.JSONDecodeError):
          items_data = {'items':[]}

     item = {'name':name, 'category':category, 'image_filename':image_filename}
     items_data['items'].append(item)
     with open("items.json", "w")as f:
          json.dump(items_data, f)

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
def get_items():
     return list_items()

@app.get("/items/{item_id}")
def get_item(item_id: int):
    try:
         item = list_items()['items'][item_id - 1]
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

from fastapi import File, Form, UploadFile, FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.responses import JSONResponse
from utils import analyze_video, process_video

# from PIL import Image
# from utils import get_som_labeled_img, check_ocr_box, get_caption_model_processor, get_yolo_model
# import torch
# from ultralytics import YOLO
# from PIL import Image
import json
import base64
from pydantic import BaseModel
from io import BytesIO
import tempfile
import os

# device = 'cuda'

# som_model = get_yolo_model(model_path='weights/icon_detect/best.pt')
# som_model.to(device)
# # two choices for caption model: fine-tuned blip2 or florence2

# # caption_model_processor = get_caption_model_processor(model_name="blip2", model_name_or_path="weights/icon_caption_blip2", device=device)
# caption_model_processor = get_caption_model_processor(model_name="florence2", model_name_or_path="weights/icon_caption_florence", device=device)

# som_model.device, type(som_model)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cnt = 0
# image_path = 'imgs/google_page.png'
# image_path = 'imgs/windows_home.png'
draw_bbox_config = {
    'text_scale': 0.8,
    'text_thickness': 2,
    'text_padding': 3,
    'thickness': 3,
}
BOX_TRESHOLD = 0.03
image_path = ""

# TODO: Properly write those
# def prelucrate_photo(image: str):
#     image_path = image
#     ocr_bbox_rslt, is_goal_filtered = check_ocr_box(image_path, display_img = False, output_bb_format='xyxy', goal_filtering=None,    easyocr_args={'paragraph': False, 'text_threshold':0.9})
#     text, ocr_bbox = ocr_bbox_rslt

#     dino_labled_img, label_coordinates, parsed_content_list = get_som_labeled_img(image_path, som_model, BOX_TRESHOLD = BOX_TRESHOLD, output_coord_in_ratio=False, ocr_bbox=ocr_bbox,draw_bbox_config=draw_bbox_config, caption_model_processor=caption_model_processor, ocr_text=text,use_local_semantics=True, iou_threshold=0.1)
#     return dino_labled_img, label_coordinates, parsed_content_list


# class ImageData(BaseModel):
#     image: str

# @app.post("/file")
# def upload_file(file: ImageData):
#     data = base64.b64decode(file.image)
#     im = Image.open(BytesIO(data))
#     im.save("input.png")
#     dino_labled_img, label_coordinates, parsed_content_list = prelucrate_photo("input.png")
#     # coords = [npa.tolist() for npa in label_coordinates.values()]
#     output = Image.open(BytesIO(base64.b64decode(dino_labled_img)))
#     output.save("output.png")
#     coords = {}
#     for key,value in label_coordinates.items():
#         coords[key] = value.tolist()
#     return {
#         "photo": dino_labled_img,
#         "coords": json.dumps(coords),
#         "content_list": json.dumps(parsed_content_list)
#     }

@app.post("/video-to-frames/")
async def video_to_frames(file: UploadFile = File(...), api_key: str = Form(...), model: str = Form(...)):
    print("Received video file")

    # Read video file into bytes
    video_data = await file.read()

    # Use a temporary file to store the video
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_file.write(video_data)
        temp_file_path = temp_file.name
    
    print("Read video file into bytes")
    frames = process_video(temp_file_path)
    output = analyze_video(frames, api_key, model)

    return {"frames": frames, "output": output.choices[0].message.content}
    

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

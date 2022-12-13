import ast
import base64

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from flask import Flask
from flask_restful import Resource, Api, reqparse, fields, marshal

def drawLogo(base, image, size_x, size_y, pos_x, pos_y):
    data = BytesIO(base64.b64decode(image))
    the_image = Image.open(data)
    the_image = the_image.resize((size_x,size_y))
    base.paste(the_image,(pos_x,pos_y))

def drawText(base, text, font, size, pos_x, pos_y, text_r, text_g, text_b,):
    anchor = (pos_x, pos_y)
    use_font = ImageFont.truetype(font, size) 
    base.text(anchor, text, font=use_font, fill=(text_r, text_g, text_b))


def imageGenerate(api_json, buffer):
    config = ast.literal_eval(api_json.config)
    xsize = config['sizeX']
    ysize = config['sizeY']
    img = Image.new("RGB", (xsize,ysize), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    blocks = (api_json.blocks)
    for block in blocks:
        block = ast.literal_eval(block)
        if block["type"] == "image":
            drawLogo(
                img, 
                block["image"], 
                block["size_x"], 
                block["size_y"],
                block["pos_x"],
                block["pos_y"]
            )
        if block["type"] == "text":
            drawText(
                draw,
                block["text"],
                block["font"],
                block["size"],
                block["pos_x"],
                block["pos_y"],
                block["text_r"],
                block["text_g"],
                block["text_b"]
            )
        if block["type"] == "line":
            draw.line(
                (
                    block["start_x"], 
                    block["start_y"], 
                    block["end_x"], 
                    block["end_y"]
                ), 
                fill=(
                    block["line_r"], 
                    block["line_g"], 
                    block["line_b"]
                    ), width=block["width"])

    img.save(buffer, "PNG", optimize=True, quality=65)

class ImageReturn(Resource):
    def get(self):
        data = parser.parse_args()
        buffer = BytesIO()
        imageGenerate(data, buffer)
        encoded_string = base64.b64encode(buffer.getvalue())
        data['image64'] = encoded_string.decode("utf-8")
        data['ext'] = 'png'
        return marshal(data, resource_fields)


app = Flask(__name__)
api = Api(app)
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

resource_fields = {
    'image64': fields.String(default='none'),
    'ext': fields.String(default='png'),
}
parser = reqparse.RequestParser()
parser.add_argument('config')
parser.add_argument('blocks', action='append')

api.add_resource(ImageReturn, '/')
if __name__ == '__main__':
    app.run(debug=True)

import sys
import os
import json
import io
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file

# --- 라이브러리 import ---
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import fitz
from PIL import Image

# --- 파일 경로를 위한 함수 ---
def resource_path(relative_path):
    base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

# --- PDF 생성 로직 ---
def register_fonts():
    try:
        pdfmetrics.registerFont(TTFont('Malgun', resource_path('malgun.ttf')))
        pdfmetrics.registerFont(TTFont('Malgun-Bold', resource_path('malgunbd.ttf')))
    except Exception as e:
        print(f"폰트 파일 로드 경고: {e}")

def draw_full_detail_label(c, data, x, y, width, height, seller_info):
    c.saveState()
    store_logo_path = resource_path('logo.png')
    product_name_x = x + 10
    if os.path.exists(store_logo_path):
        logo_height, logo_width = 35, 35
        logo_y = y + height - 35
        c.drawImage(store_logo_path, x + 10, logo_y, width=logo_width, height=logo_height, mask='auto')
        product_name_x = x + 10 + logo_width + 5
    
    product_name = data.get('name', '')
    font_size = 14
    if len(product_name) > 8: font_size = 12
    c.setFont('Malgun-Bold', font_size)
    c.drawString(product_name_x, y + height - 20, product_name)
    
    right_margin = x + width - 10
    c.setFont('Malgun-Bold', 9)
    c.drawRightString(right_margin, y + height - 20, f"원산지: {data.get('origin', '')}")
    c.line(x + 5, y + height - 32, x + width - 5, y + height - 32)
    
    c.setFont('Malgun-Bold', 8)
    c.drawString(x + 10, y + height - 45, f"가공(포장)일: {data.get('date', '')}")
    c.drawRightString(right_margin, y + height - 45, f"중량(Kg): {data.get('weight', 0.0)} ±20g")

    details_text = data.get('details', '')
    details_font_size = 8
    if len(details_text) > 130: details_font_size = 6.5
    elif len(details_text) > 100: details_font_size = 8
    
    text_object = c.beginText(x + 10, y + height - 65)
    text_object.setFont('Malgun-Bold', details_font_size)
    text_object.setLeading(details_font_size + 2)
    for line in details_text.split('\n'):
        text_object.textLine(line)
    c.drawText(text_object)
    
    font_size, line_height = 7, 8
    c.setFont('Malgun-Bold', font_size)
    if isinstance(seller_info, list) and len(seller_info) == 2:
        c.drawCentredString(x + width / 2, y + line_height + 5, seller_info[0])
        c.drawCentredString(x + width / 2, y + 5, seller_info[1])
    else:
        c.drawCentredString(x + width / 2, y + 10, str(seller_info))

    recycle_logo_path = resource_path('recycle.png')
    if os.path.exists(recycle_logo_path):
        img_reader = ImageReader(recycle_logo_path)
        img_width, img_height = img_reader.getSize()
        logo_height_rc = 0.35 * inch
        logo_width_rc = logo_height_rc * (img_width / img_height)
        c.drawImage(recycle_logo_path, x + width - logo_width_rc - 5, y + 5, width=logo_width_rc, height=logo_height_rc, mask='auto')
    
    c.restoreState()

def draw_simple_label(c, data, x, y, width, height):
    c.saveState()
    product_name = data.get('name', '')
    origin = f"({data.get('origin', '')})"
    y_offset = 0
    
    if len(product_name) > 6: product_font_size = 15
    elif len(product_name) > 4: 
        product_font_size = 17
        y_offset = 2
    elif len(product_name) > 3:
        product_font_size = 20
        y_offset = 3
    else: 
        product_font_size = 28
        y_offset = 8
        
    origin_font_size = 8
    center_x = x + width / 2
    
    c.setFont('Malgun-Bold', product_font_size)
    c.drawCentredString(center_x, y + height / 2 - y_offset, product_name)
    
    c.setFont('Malgun', origin_font_size)
    c.drawCentredString(center_x, y + height / 2 - product_font_size+y_offset, origin)
    
    c.restoreState()

# --- Flask 앱 설정 ---
app = Flask(__name__)

with open(resource_path('labels_config.json'), 'r', encoding='utf-8') as f:
    config_data = json.load(f)

register_fonts()

# --- 라우트 (웹 주소) 정의 ---
@app.route('/')
def index():
    products = list(config_data['products'].keys())
    return render_template('index.html', products=products, config_data=config_data)

@app.route('/generate_preview', methods=['POST'])
def generate_preview():
    request_data = request.get_json()
    label_data = request_data.get('label_data', {})
    paper_size_name = request_data.get('paper_size')
    
    if not paper_size_name:
        return "Paper size not specified", 400
    paper_info = config_data.get("paper_sizes", {}).get(paper_size_name)
    if not paper_info:
        return "Paper size definition not found", 400

    label_width, label_height = paper_info['width_mm'] * mm, paper_info['height_mm'] * mm
    
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=(label_width, label_height))
    seller_info = config_data.get("seller_info", "")
    
    # --- ★★★ 주요 변경점: 라벨 타입에 따라 다른 그리기 함수 호출 ★★★ ---
    if paper_info['type'] == 'simple':
        draw_simple_label(c, label_data, 0, 0, label_width, label_height)
    else: # 'full_detail' 또는 기본값
        draw_full_detail_label(c, label_data, 0, 0, label_width, label_height, seller_info)
        
    c.save()
    pdf_buffer.seek(0)

    doc = fitz.open(stream=pdf_buffer, filetype="pdf")
    page = doc.load_page(0)
    pix = page.get_pixmap(dpi=150)
    doc.close()

    img_buffer = io.BytesIO()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    
    return send_file(img_buffer, mimetype='image/png')

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    request_data = request.get_json()
    queue = request_data.get('queue', [])
    paper_size_name = request_data.get('paper_size')

    if not paper_size_name: return "Paper size not specified", 400
    paper_info = config_data.get("paper_sizes", {}).get(paper_size_name)
    if not paper_info: return "Paper size definition not found", 400

    label_width, label_height = paper_info['width_mm'] * mm, paper_info['height_mm'] * mm
    
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=(label_width, label_height))
    
    seller_info = config_data.get("seller_info", "")
    
      # --- ★★★ 주요 변경점: 인쇄 보정값(음수 여백) 적용 ★★★ ---
    x_offset = -2.8  # 약 1mm를 왼쪽으로 이동 (필요시 이 값을 미세 조정)
    y_offset = 0


    for i, data in enumerate(queue):
        if paper_info['type'] == 'simple':
            draw_simple_label(c, data, x_offset, y_offset, label_width, label_height)
        else:
            draw_full_detail_label(c, data, x_offset, y_offset, label_width, label_height, seller_info)
        if i < len(queue) - 1:
            c.showPage()
    c.save()
    pdf_buffer.seek(0)
    
    return send_file(pdf_buffer, mimetype='application/pdf')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

# 이 파일은 UI가 없으므로 tkinter 관련 import는 모두 제거합니다.

def resource_path(relative_path):
    # 웹 서버에서는 이 함수가 필요 없지만, 로컬 테스트를 위해 유지
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def register_font():
    # 폰트 등록은 한 번만 하면 되므로 app.py에서 관리
    try:
        pdfmetrics.registerFont(TTFont('Malgun', resource_path('malgun.ttf')))
        pdfmetrics.registerFont(TTFont('Malgun-Bold', resource_path('malgunbd.ttf')))
    except:
        print("폰트 파일을 찾을 수 없습니다. malgun.ttf와 malgunbd.ttf가 필요합니다.")

def draw_single_label(c, data, x, y, width, height, seller_info, is_preview=False):
    c.saveState()
    
    # 가게 로고
    store_logo_path = resource_path('logo.png')
    product_name_x = x + 10 
    if os.path.exists(store_logo_path):
        logo_height = 14; logo_width = 14
        logo_y = y + height - 21
        c.drawImage(store_logo_path, x + 10, logo_y, width=logo_width, height=logo_height, mask='auto')
        product_name_x = x + 10 + logo_width + 5
    
    # 라벨 내용 그리기 (볼드체 적용)
    c.setFont('Malgun-Bold', 14)
    c.drawString(product_name_x, y + height - 20, data['name'])
    
    right_margin = x + width - 10
    c.setFont('Malgun-Bold', 10)
    c.drawRightString(right_margin, y + height - 20, f"원산지: {data.get('origin', '')}")
    
    c.line(x + 5, y + height - 32, x + width - 5, y + height - 32)
    
    c.setFont('Malgun-Bold', 20) # 일반 폰트로 변경
    c.drawString(x + 10, y + height - 45, f"가공(포장)일: {data.get('date', '')}")
    c.drawRightString(right_margin, y + height - 45, f"중량(Kg): {data.get('weight', 0.0)} ±20g")

    # 상세 정보 동적 폰트 크기 적용
    details_text = data.get('details', '')
    details_font_size = 8
    if len(details_text) > 130: details_font_size = 7
    elif len(details_text) > 100: details_font_size = 7.5

    current_y = y + height - 65
    for line in details_text.split('\n'):
        if ":" in line:
            title, content = line.split(":", 1)
            title += ":"
            c.setFont('Malgun-Bold', details_font_size)
            c.drawString(x + 10, current_y, title)
            title_width = c.stringWidth(title, 'Malgun-Bold', details_font_size)
            c.setFont('Malgun', details_font_size)
            c.drawString(x + 10 + title_width, current_y, content)
        else:
            c.setFont('Malgun', details_font_size)
            c.drawString(x + 10, current_y, line)
        current_y -= (details_font_size + 2)

    # 판매처 정보 (두 줄)
    font_size = 7
    line_height = 8
    c.setFont('Malgun', font_size)
    if isinstance(seller_info, list) and len(seller_info) == 2:
        c.drawCentredString(x + width / 2, y + line_height + 5, seller_info[0])
        c.drawCentredString(x + width / 2, y + 5, seller_info[1])
    else:
        c.drawCentredString(x + width / 2, y + 10, str(seller_info))

    # 재활용 로고
    recycle_logo_path = resource_path('recycle.png')
    if os.path.exists(recycle_logo_path):
        img_reader = ImageReader(recycle_logo_path)
        img_width, img_height = img_reader.getSize()
        logo_height_rc = 0.35 * inch 
        logo_width_rc = logo_height_rc * (img_width / img_height)
        c.drawImage(recycle_logo_path, x + width - logo_width_rc - 5, y + 5, 
                    width=logo_width_rc, height=logo_height_rc, mask='auto')

    c.restoreState()
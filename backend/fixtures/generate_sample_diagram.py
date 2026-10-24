"""
Generates a clear architecture diagram PNG for testing upload and model visual inspection.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent / "sample_architecture_diagram.png"


def create_diagram():
    img = Image.new("RGB", (900, 500), color=(248, 249, 250))
    draw = ImageDraw.Draw(img)

    # Box styling
    def draw_box(x, y, w, h, text, fill=(255, 255, 255), outline=(50, 50, 50)):
        draw.rectangle([x, y, x + w, y + h], fill=fill, outline=outline, width=2)
        draw.text((x + 15, y + (h // 2) - 8), text, fill=(20, 20, 20))

    def draw_arrow(x1, y1, x2, y2, label=""):
        draw.line([(x1, y1), (x2, y2)], fill=(40, 40, 40), width=2)
        # Arrowhead
        draw.polygon([(x2, y2), (x2 - 8, y2 - 5), (x2 - 8, y2 + 5)], fill=(40, 40, 40))
        if label:
            mid_x = (x1 + x2) // 2
            mid_y = ((y1 + y2) // 2) - 15
            draw.text((mid_x - 30, mid_y), label, fill=(100, 100, 100))

    # Components
    draw_box(40, 200, 160, 60, "Web Client", fill=(230, 242, 255), outline=(0, 102, 204))
    draw_box(260, 200, 160, 60, "API Gateway", fill=(230, 255, 240), outline=(0, 153, 76))
    draw_box(480, 120, 170, 60, "Auth Service", fill=(255, 245, 230), outline=(204, 102, 0))
    draw_box(480, 280, 170, 60, "Order Service", fill=(255, 245, 230), outline=(204, 102, 0))
    draw_box(720, 280, 150, 60, "Postgres DB", fill=(245, 230, 255), outline=(102, 0, 204))

    # Connectors
    draw_arrow(200, 230, 260, 230, "HTTPS")
    draw_arrow(420, 215, 480, 150, "JWT Verify")
    draw_arrow(420, 245, 480, 310, "Order Placed")
    draw_arrow(650, 310, 720, 310, "SQL")

    img.save(OUTPUT_PATH)
    print(f"Sample architecture diagram saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    create_diagram()

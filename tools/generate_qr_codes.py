"""Generate QR codes for presentation materials.

Usage:
    python3 tools/generate_qr_codes.py

Generates PNG QR codes in the qr_codes/ directory.
"""

import os
import qrcode

QR_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "qr_codes")

QR_CODES = [
    ("repo_qr.png", "https://github.com/kyle-chalmers/azure-sql-patent-intelligence"),
    ("linkedin_qr.png", "https://www.linkedin.com/in/kylechalmers/"),
    ("youtube_qr.png", "https://www.youtube.com/channel/UCkRi29nXFxNBuPhjseoB6AQ"),
    ("kclabs_qr.png", "https://kclabs.ai/"),
    ("aztechweek_workshop_qr.png", "https://partiful.com/e/VPy2EpNYQFppO6ZQA17n"),
    ("aztechweek_hike_qr.png", "https://partiful.com/e/vMiPKyrTML8yf8Gnf618"),
]


def generate_all():
    os.makedirs(QR_DIR, exist_ok=True)

    for filename, url in QR_CODES:
        filepath = os.path.join(QR_DIR, filename)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filepath)
        print(f"  Generated: {filename}")

    print(f"\nAll {len(QR_CODES)} QR codes saved to qr_codes/")


if __name__ == "__main__":
    generate_all()

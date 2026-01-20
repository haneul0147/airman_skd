import qrcode

url = "https://airmankorea.com/?page_id=5576&lang=en"

qr = qrcode.QRCode(
    version=3,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
)

qr.add_data(url)
qr.make(fit=True)

qr_img = qr.make_image(fill_color="black", back_color="white")
qr_img.save("airman_ENG_qr_black.png")

print("✅ 검은색 QR 코드가 저장되었습니다!")

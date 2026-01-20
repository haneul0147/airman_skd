import qrcode

# QR 코드에 넣을 URL
url = "https://www.facebook.com/koreanhospitalss/?locale=mn_MN"

# QR 코드 생성
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)

# QR 이미지 생성 (검은색 QR, 흰 배경)
img = qr.make_image(fill_color="black", back_color="white")

# 이미지 저장
img.save("korean_hospitals_qr.png")
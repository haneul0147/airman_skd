from PIL import Image

# 이미지 열기
img_path = "slide.png"  # 이미지 파일 경로로 수정
img = Image.open(img_path)

# 제공된 좌표로 크기 조정
left, top, right, bottom = 3, 163, 185, 344
cropped_img = img.crop((left, top, right, bottom))

# 크기 조정 후 이미지 저장
cropped_img_path = "cropped_image.png"  # 원하는 저장 경로로 수정
cropped_img.save(cropped_img_path)

# 결과 확인을 위해 이미지 출력
cropped_img.show()

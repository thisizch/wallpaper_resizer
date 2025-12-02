import streamlit as st
from PIL import Image, ImageFilter
import io
from collections import Counter

TARGET_WIDTH = 1200
TARGET_HEIGHT = 2600


def extract_background_color(img: Image.Image):
    """이미지 네 모서리 색상 중 가장 빈도가 높은 색을 추출 (배경색 근사)."""
    img = img.convert("RGB")
    w, h = img.size

    corners = [
        img.getpixel((0, 0)),          # 좌상단
        img.getpixel((w - 1, 0)),      # 우상단
        img.getpixel((0, h - 1)),      # 좌하단
        img.getpixel((w - 1, h - 1))   # 우하단
    ]

    return Counter(corners).most_common(1)[0][0]


def make_wallpaper(image: Image.Image, method: str = "Blurred background") -> Image.Image:
    """비율은 그대로 두고, 1200x2600 안에 최대한 크게 맞춰서 배경화면 생성."""
    img = image.convert("RGB")
    w, h = img.size

    # ---- foreground: 비율 유지 + 필요하면 확대/축소
    scale = min(TARGET_WIDTH / w, TARGET_HEIGHT / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    foreground = img.resize((new_w, new_h), Image.LANCZOS)

    # ---- background
    if method == "Blurred background":
        background = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)
        background = background.filter(ImageFilter.GaussianBlur(radius=50))
    else:
        bg_color = extract_background_color(img)
        background = Image.new("RGB", (TARGET_WIDTH, TARGET_HEIGHT), bg_color)

    # ---- 가운데에 붙이기
    x = (TARGET_WIDTH - foreground.width) // 2
    y = (TARGET_HEIGHT - foreground.height) // 2
    background.paste(foreground, (x, y))

    return background


def main():
    st.set_page_config(page_title="배경화면 리사이저 1200x2600", layout="centered")
    st.title("📱 휴대폰 배경화면 리사이저 (1200 x 2600)")
    st.write(
        "사진을 업로드하면 **비율은 그대로** 두고, "
        "빈 부분만 채워서 1200×2600 사이즈로 만들어 줍니다.\n"
        "원본은 잘리지 않고, 찌그러지지 않습니다."
    )

    method = st.radio(
        "배경 확장 방식",
        ["Blurred background", "Solid color (extract from original)"],
        index=0,
        horizontal=True
    )

    uploaded_file = st.file_uploader(
        "이미지를 업로드하세요 (JPG, JPEG, PNG)",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file:
        image = Image.open(uploaded_file)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📎 원본")
            st.image(image, use_container_width=True)
            st.text(f"원본 해상도: {image.width} x {image.height}")

        result = make_wallpaper(image, method)

        with col2:
            st.subheader("📱 변환된 배경화면")
            st.image(result, use_container_width=True)
            st.text(f"결과 해상도: {TARGET_WIDTH} x {TARGET_HEIGHT}")

        buf = io.BytesIO()
        result.save(buf, format="PNG")
        buf.seek(0)

        st.download_button(
            "📥 PNG 다운로드",
            data=buf,
            file_name="wallpaper_1200x2600.png",
            mime="image/png"
        )
    else:
        st.info("이미지를 업로드하세요.")


if __name__ == "__main__":
    main()

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 1. 제목 및 설명 추가
st.title("🌊 나만의 파형 시뮬레이터")
st.write("슬라이더를 움직여 파형의 진동수와 진폭을 조절해보세요.")

# 2. 사이드바에 입력 위젯(Slider) 만들기
# 사용자에게 값을 입력받는 부분입니다.
freq = st.sidebar.slider("주파수 (Frequency)", 1.0, 10.0, 5.0)  # 최소, 최대, 기본값
amp = st.sidebar.slider("진폭 (Amplitude)", 0.1, 2.0, 1.0)

# 3. 데이터 생성 (NumPy 활용)
t = np.linspace(0, 10, 500)
y = amp * np.sin(freq * t)

# 4. 데이터 시각화 (Matplotlib 활용)
# 평소 쓰시던 코드 그대로 사용 가능합니다.
fig, ax = plt.subplots()
ax.plot(t, y)
ax.set_title(f"Frequency: {freq}, Amplitude: {amp}")
ax.grid(True)

# 5. 웹 화면에 그래프 출력
st.pyplot(fig)

# 6. 데이터 표로 보여주기
st.write("### 생성된 데이터 미리보기")
st.dataframe({"시간": t[:5], "값": y[:5]}) # 상위 5개 데이터만 표로 출력
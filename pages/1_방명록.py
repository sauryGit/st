import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("📝 나만의 무료 DB 방명록")

# 1. 구글 시트 연결 (Secrets에 있는 정보로 자동 연결)
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. 데이터 읽어오기 (TTL=0으로 설정해야 새로고침 시 즉시 반영됨)
# 기존 데이터가 있으면 가져오고, 없으면 빈 DataFrame 생성
try:
    existing_data = conn.read(worksheet="Sheet1", usecols=[0, 1], ttl=0)
    existing_data = existing_data.dropna(how="all") # 빈 줄 제거
except:
    existing_data = pd.DataFrame(columns=["이름", "메시지"])

# 3. 데이터 입력 폼 만들기
with st.form(key="guestbook_form"):
    name = st.text_input("이름")
    message = st.text_area("남길 말")
    submit_button = st.form_submit_button("등록하기")

    if submit_button:
        if name and message:
            # 새로운 데이터 생성
            new_data = pd.DataFrame([{"이름": name, "메시지": message}])
            
            # 기존 데이터와 합치기
            updated_df = pd.concat([existing_data, new_data], ignore_index=True)
            
            # 구글 시트에 업데이트 (쓰기)
            conn.update(worksheet="Sheet1", data=updated_df)
            
            st.success("성공적으로 저장되었습니다!")
            st.rerun() # 화면 새로고침해서 리스트 갱신
        else:
            st.warning("이름과 메시지를 모두 입력해주세요.")

# 4. 저장된 데이터 보여주기
st.divider()
st.subheader("📋 방명록 목록")
st.dataframe(existing_data)
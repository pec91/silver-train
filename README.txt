
# 중고차 최신시세조회 - Streamlit 앱

이 앱은 중고차 시세 데이터를 기준으로 필터(브랜드, 연식, 가격, 키로수)를 적용해 원하는 차량을 조회할 수 있도록 도와줍니다.

## 설치 및 실행 방법

1. Python 설치: https://www.python.org/downloads/
2. 필요한 라이브러리 설치:
```
pip install streamlit pandas openpyxl
```
3. `used_cars.xlsx` 파일을 현재 폴더에 저장
4. 앱 실행:
```
streamlit run app.py
```

## 배포 방법 (Streamlit Cloud)

1. GitHub 계정 생성 및 코드 업로드
2. [https://streamlit.io/cloud](https://streamlit.io/cloud) 접속 후 GitHub 저장소와 연동
3. 앱 설정 시 `app.py`를 메인 파일로 지정
4. 배포 후 공유 링크 확인

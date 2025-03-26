import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import streamlit as st

# 한글 폰트 설정
# plt.rcParams['font.family'] = "AppleGothic"
# Windows, 리눅스 사용자
plt.rcParams['font.family'] = "NanumGothic"
# plt.rcParams['axes.unicode_minus'] = False

class PensionData():
    def __init__(self, filepath):
        self.df = pd.read_csv(os.path.join(filepath), encoding='cp949')
        self.pattern1 = r'(\([^)]+\))'
        self.pattern2 = r'(\[[^)]+\])'
        self.pattern3 = r'[^A-Za-z0-9가-힣]'
        self.preprocess()
          
    def preprocess(self):
        self.df.columns = [
            '자료생성년월', '사업장명', '사업자등록번호', '가입상태', '우편번호',
            '사업장지번상세주소', '주소', '고객법정동주소코드', '고객행정동주소코드', 
            '시도코드', '시군구코드', '읍면동코드', 
            '사업장형태구분코드 1 법인 2 개인', '업종코드', '업종코드명', 
            '적용일자', '재등록일자', '탈퇴일자',
            '가입자수', '금액', '신규', '상실'
        ]
        df = self.df.drop(['자료생성년월', '우편번호', '사업장지번상세주소', '고객법정동주소코드', '고객행정동주소코드', '사업장형태구분코드 1 법인 2 개인', '적용일자', '재등록일자'], axis=1)
        df['사업장명'] = df['사업장명'].apply(self.preprocessing)
        df['탈퇴일자_연도'] =  pd.to_datetime(df['탈퇴일자']).dt.year
        df['탈퇴일자_월'] =  pd.to_datetime(df['탈퇴일자']).dt.month
        df['시도'] = df['주소'].str.split(' ').str[0]
        df = df.loc[df['가입상태'] == 1].drop(['가입상태', '탈퇴일자'], axis=1).reset_index(drop=True)
        df['인당금액'] = df['금액'] / df['가입자수']
        df['월급여추정'] =  df['인당금액'] / 9 * 100
        df['연간급여추정'] = df['월급여추정'] * 12
        self.df = df

        
    def preprocessing(self, x):
        x = re.sub(self.pattern1, '', x)
        x = re.sub(self.pattern2, '', x)
        x = re.sub(self.pattern3, ' ', x)
        x = re.sub(' +', ' ', x)
        return x
    
    def find_company(self, company_name):
        return self.df.loc[self.df['사업장명'].str.contains(company_name), ['사업장명', '월급여추정', '연간급여추정', '업종코드', '가입자수']]\
                  .sort_values('가입자수', ascending=False)
    

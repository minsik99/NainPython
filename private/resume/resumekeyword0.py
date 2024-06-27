# 텍스트 파일 테스트 사용 빈도 테스트

# 공공데이터포털(https://www.data.go.kr)에서 csv 파일 다운받기
# csv 파일을 읽어 들이기
# 읽어 들인 데이터에서 가장 많이 사용된 명사 찾기

import codecs
import csv
from konlpy.tag import Kkma

kkma = Kkma()
word_dic = {}  # dict()
lines = []  # list()

# 불용어 리스트
stopwords = set(['이', '그', '저', '것', '수', '때', '등', '들', '및', '의', '를', '에', '가', '은', '는', '로', '에게', '에서', '와', '과', '도', '으로', '그리고', '하지만', '그래서',
                 '글자수', '경험', '프로젝트', '질문', '답변', '글자수', '작성', '자소', '카드', '신한', '본인', '인턴', '지원'])

# CSV 파일에서 데이터를 읽어오기
def read_csv_file(file_path):
    with open(file_path, 'r') as raws:
        reader = csv.reader(raws)
        for raw in reader:
            lines.append(raw)  # raw (한 줄의 데이터)를 리스트에 저장함
            print(raw)

# 텍스트 파일에서 데이터를 읽어오기
def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            lines.append([line.strip()])  # 줄바꿈을 제거하고 리스트에 저장
            print(line.strip())

# CSV 파일 읽기
# read_csv_file('./sample2.csv')

# 텍스트 파일 읽기
read_text_file('./sample.txt')

# 저장 구조 : [[], [], ...]
for line in lines:
    mal_list = kkma.pos(' '.join(line))  # '구분자'.join(리스트) => str 타입으로 변환
    print(mal_list)

    # 명사들을 수집해서 반복되는 명사를 count 를 진행 처리
    for word in mal_list:
        print(word)  # (단어, 태그) => 튜플 : (인덱스 0, 인덱스1) > 단어, 품사 출력 함
        if word[1] == 'NNG' or word[1] == 'NNP':
            # 불용어에 포함되지 않은 단어만 처리
            if word[0] not in stopwords:
                # 해당 단어가 추출된 단어가 저장되어 있는 사전(dictionary)에 저장되어 있지 않다면, 사전(word_dic)에 추가함
                if not word[0] in word_dic:
                    word_dic[word[0]] = 0  # {단어 :0} 저장
                word_dic[word[0]] += 1  # 단어 (key)의 카운트를 1증가 처리함

# print(word_dic)
# 단어 빈도수에 대해 내림차순 정렬 처리
keys = sorted(word_dic.items(), key=lambda x: x[1], reverse=True)  # x의 1번째(사용빈도)를 기준으로 True(내림차순) 정렬

# 상위 10개까지만 정렬 결과 출력
for word, count in keys[:30]:
    print(f'{word}: {count}', end=', ')
# !/usr/bin/env python3
# -*- codig: utf-8 -*-
import requests
import json
import whisper
import connection.dbConnectTemplate as dbtemp


def calculate_vscore(positive, negative):
    neutral = 1 - positive + negative
    score = positive * 60 - negative * 60 + neutral * 30
    return score

# def stt(source):
def voice_analysis(itvNo, qNo, filename):

    model = whisper.load_model("base")
    file_path = itvNo + "/" + filename
    # 감지된 언어가 한국어('ko')가 아닐 경우, 명시적으로 한국어로 설정하여 다시 전사합니다.
    detected_lang = model.transcribe(file_path, fp16=False)['language']
    if detected_lang != 'ko':
        result = model.transcribe(file_path, fp16=False, language='ko')
    else:
        result = model.transcribe(file_path, fp16=False)

    # print(result)
    start_point = result['segments'][0]['start']        # 답변 시작 시간
    end_point = result['segments'][-1]['end']         # 답변 종료 시간
    print(f"시작 시간 : {start_point}, 종료 시간 : {end_point}")
    print(result["text"])

    content = result["text"]       # STT 문자열

    client_id = "exhnc4vqhw"
    client_secret = "C82anCAZex9PK4XktQLYlUBYwmTodghxMTBwHHCb"
    url="https://naveropenapi.apigw.ntruss.com/sentiment-analysis/v1/analyze"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
        "Content-Type": "application/json"
    }

    data = {
      "content": content
    }

    response = requests.post(url, data=json.dumps(data), headers=headers)
    results = json.loads(response.text)

    voice_list = list()
    rescode = response.status_code
    if (rescode == 200):
        for result in results['sentences']:
            sentence = result['content']

            offset, length = None, None
            for h in result['highlights']:
                offset = h['offset']
                length = h['length']
            highlight = result['content'][offset:offset + length]
            sentiment = result['sentiment']
            negative = result['confidence']['negative']
            positive = result['confidence']['positive']
            neutral = result['confidence']['neutral']

            print(f"  답변 문장: {sentence}")
            print(f"  강조된 분석 구문: {highlight}")
            print("분석 결과:")
            print(f"  문장 경향성: {sentiment}")
            print(f"  수치:")
            print(f"    부정: {negative}")
            print(f"    긍정: {positive}")
            print(f"    중립: {neutral}")
            print()
            each_sentence = ['', sentence, positive, negative]
            # TB_VOICE_SENTENCE 각 행 저장 list
            voice_list.append(each_sentence)
    else:
        print("Error : " + response.text)
    voice_content = (itvNo, qNo, content)

    print(voice_content)

    # dbtemp.oracle_init()
    conn = dbtemp.connect()
    cursor = conn.cursor()

    # "insert into TB_VOICE (VOICE_CONTENT) values (:1)"
    voice_query = "INSERT INTO TB_VOICE (VOICE_NO, ITV_NO, Q_NO, VOICE_CONTENT) VALUES (SEQ_VOICE_NO.NEXTVAL, :1, :2, :3)"
    voice_no_q = "SELECT VOICE_NO FROM TB_VOICE WHERE ITV_NO = :1 AND Q_NO = :2"
    sentence_query = "INSERT INTO TB_VOICE_SENTENCE VALUES (SEQ_VS_NO.NEXTVAL, :1, :2, :3, :4)"
    interview_query = "UPDATE TB_INTERVIEW SET VOICE_SCORE = :1 WHERE ITV_NO = :2"

    try:
        print("try catch 진입")
        cursor.execute(voice_query, voice_content)
        conn.commit()
        print("voice insert문")

        cursor.execute(voice_no_q, (itvNo, qNo))
        voice_no = cursor.fetchone()[0]
        print("voice_no select문")

        pCount = 0
        nCount = 0
        pSum = 0
        nSum = 0

        for s in voice_list:
            s[0] = voice_no
            if s[2] >= 60:
                pSum += s[2]
                pCount += 1
            elif s[3] >= 60:
                nSum += s[3]
                nCount += 1

            row = tuple(s)
            print("row", row)
            cursor.execute(sentence_query, row)
            print("voice_sentence insert")

        cal = calculate_vscore(pSum / pCount if pCount else 0, nSum / nCount if nCount else 0)
        cursor.execute(interview_query, (cal, itvNo))
        print("interview 테이블 점수 update")

        conn.commit()
        print("커밋 성공")
    except Exception as e:
        conn.rollback()
        print(f"커밋 실패: {e}")
    finally:
        cursor.close()
        dbtemp.close(conn)
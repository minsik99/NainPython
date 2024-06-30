import cx_Oracle

from connection.dbConnectTemplate import connect, close, commit, rollback

cx_Oracle.init_oracle_client(lib_dir='D:\\instantclient_18_5')


def insert_score(answer_no, itvNo, itv_type, score):

    conn = connect()  # 데이터베이스 연결 생성

    if conn:
        try:
            cursor = conn.cursor()
            # 점수 계산
            # 데이터 삽입 쿼리 작성 (시퀀스 사용)
            insert_query = """
                    INSERT INTO TB_VIDEO (VIDEO_NO, ITV_NO, ANSWER_NO, RESULT_DATA, ITV_TYPE)
                    VALUES (SEQ_VIDEO_NO.NEXTVAL, :1, :2, :3, :4)
            """
            # 데이터 삽입 실행
            cursor.execute(insert_query, (itvNo, answer_no, score, itv_type))
            commit(conn)  # 변경 사항 커밋
            print(f"데이터 삽입 성공: 인터뷰 {itvNo}, 답변 {answer_no}, 점수 {score}, 타입 {itv_type}, 점수 {score}")
        except Exception as e:
            rollback(conn)  # 오류 발생 시 롤백
            print('데이터 삽입 실패: ', e)
        finally:
            cursor.close()  # 커서 닫기
            close(conn)  # 연결 닫기


def insert_emotion(answer_no, itvNo, avg_prob, emotion):
    conn = connect()  # 데이터베이스 연결 생성

    if conn:
        try:
            cursor = conn.cursor()
            query = """
             INSERT INTO TB_EMOTION (EMOTION_NO, ITV_NO, ANSWER_ENO, ERESULT_DATA, EMOTION_NAME)
             VALUES (SEQ_EMOTION_NO.NEXTVAL, :1, :2, :3, :4)
             """
            # 데이터 삽입 실행
            cursor.execute(query, (itvNo, answer_no, avg_prob, emotion))
            commit(conn)  # 변경 사항 커밋
            print(f"데이터 삽입 성공: 인터뷰 {itvNo}, 답변 {answer_no}, 점수 {avg_prob}, 감정명{ emotion}")
            
        except Exception as e:
            rollback(conn)  # 오류 발생 시 롤백
            print('감정데이터 삽입 실패: ', e)
        finally:
            cursor.close()  # 커서 닫기
            close(conn)  # 연결 닫기


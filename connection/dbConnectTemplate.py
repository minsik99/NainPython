# path : common\\dbConnectTemplate.py
# module : common.dbConnectTemplate
# 데이터베이스 연결 관리용 공통 모듈 (변수와 함수 정의만으로 구성)

# 1. 사용할 패키지 모듈 import
import cx_Oracle


# 오라클 연결을 위한 값들을 전역변수로 지정
url = 'localhost:1521/xe'
user = 'c##NAIN'
passwd = 'NAIN'

def oracle_init():      # 애플리케이션에서 단 한 번 구동
    cx_Oracle.init_oracle_client(lib_dir='C:\\instantclient_18_5')
    # Mac 에서는 필요 없음

def connect():
    try:
        conn = cx_Oracle.connect(user, passwd, url)
        # Mac 에서는 아래 구문 사용
        # conn = cx_Oracle.connect('c##testweb/testweb@localhost:1521/xe)
        conn.autocommit = False
        print("db 연결 성공")
        return conn
    except Exception as msg:
        print('Oracle 연결 에러 : ', msg)

def close(conn):
    try:
        if conn:        # conn != null
            conn.close()
    except Exception as msg:
        print('Oracle close 실패 : ', msg)

def commit(conn):
    try:
        if conn:        # conn != null
            conn.commit()
    except Exception as msg:
        print('Oracle commit 실패 : ', msg)

def rollback(conn):
    try:
        if conn:        # conn != null
            conn.rollback()
    except Exception as msg:
        print('Oracle rollback 실패 : ', msg)

import paramiko

# Google Colab의 SSH 주소 및 비밀번호 (ngrok 링크 및 비밀번호로 설정)
host = "0.tcp.ngrok.io"  # ngrok 링크에서 제공된 호스트 주소
port = 22  # ngrok 링크에서 제공된 포트 번호
username = "root"
password = "sophia4352"  # 설정한 비밀번호

# SSH 클라이언트 객체 생성
client = paramiko.SSHClient()

# 서버의 키를 자동으로 추가 (처음 연결 시 확인 메시지 발생을 방지)
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# SSH 연결
client.connect(host, port=port, username=username, password=password)

# 명령어 실행 (예: 모델 실행을 위한 Python 코드)
stdin, stdout, stderr = client.exec_command('python3 /content/your_model.py')

# 출력 결과 받기
print("STDOUT:")
print(stdout.read().decode())  # 명령어 실행 결과
print("STDERR:")
print(stderr.read().decode())  # 오류 메시지

# SSH 연결 종료
client.close()

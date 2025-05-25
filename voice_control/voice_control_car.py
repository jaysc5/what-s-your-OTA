# SSAFY 13 embedded proj.

# 모듈 로드
from Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor
import asyncio
import websockets

# 모터 초기설정
mh = Raspi_MotorHAT(addr = 0x6f)
motor1 = mh.getMotor(2) # M1단자에 모터연결
speed = 125 # 모터 속도 0~255
motor1.setSpeed(speed)

# 서보 초기설정
servo = mh._pwm
servo.setPWMFreq(60)

servoCH = 0 # 서보 연결된 핀
SERVO_PULSE_MAX = 400   # 서보 작동 범위
SERVO_PULSE_MIN = 200

# 웹소켓 서버(차량) ip
ServerIP = '192.168.137.205'
WebsocketPort = 7890

# 앞으로
def go():
    motor1.run(Raspi_MotorHAT.BACKWARD)

# 뒤로
def back():
    motor1.run(Raspi_MotorHAT.FORWARD)

# 모터 정지
def stop():
    motor1.run(Raspi_MotorHAT.RELEASE)

# 빠르게
def speed_up():
    global speed
    speed = 255 if speed >= 235 else speed + 20 # 최대 255, 20단위로 증가
    motor1.setSpeed(speed)

# 느리게
def speed_down():
    global speed
    speed = 0 if speed <= 20 else speed - 20 # 최하 0
    motor1.setSpeed(speed)

# 각도만큼 핸들 틀기
def steer(angle = 0):   
    if angle < -90:
        angle = -90
    elif angle > 90:
        angle = 90
    pulse_time = int(SERVO_PULSE_MIN + (SERVO_PULSE_MAX - SERVO_PULSE_MIN) * (angle + 90) / 180)
    print(f"[STEER] angle: {angle} → pulse_time: {pulse_time}")
    servo.setPWM(servoCH, 0, pulse_time)

# 우회전
def steer_right():
    steer(90)

# 좌회전
def steer_left():
    steer(-90)

# 핸들 중앙
def steer_center():
    steer(0)

# 클라이언트로부터 받을 수 있는 명령과 대응하는 function
command = ['앞으로', '뒤로', '정지', '빠르게', '느리게', '오른쪽', '왼쪽', '중앙']
func = [go, back, stop, speed_up, speed_down, steer_right, steer_left, steer_center]

async def voice_drive(websocket):
    try:
        loop = asyncio.get_running_loop()   # asyncio 이벤트루프

        while True:
            # 클라이언트로부터 메시지 받음
            message = await websocket.recv()
            print(f'[RX] 클라이언트로부터 수신된 메시지: "{message}"')

            # 메시지에 해당하는 index의 func 실행
            if message in command:
                print(f'[EXEC] 명령 일치: "{message}" → 동작 실행')
                await loop.run_in_executor(None, func[command.index(message)])  # 명령 실행
                response = f'"{message}" 동작 완료'
            else:
                print(f'[WARN] 알 수 없는 명령어: "{message}"')
                response = f'"{message}"는 인식되지 않은 명령입니다'

            # 응답 보냄
            await websocket.send(response)

    except websockets.ConnectionClosed:
        print('네크워크 확인')

async def main():
    try:
        # websocket 서버 작동
        server = await websockets.serve(voice_drive, host = ServerIP, port = WebsocketPort)
        print('server ready!')
        await server.wait_closed()

    except KeyboardInterrupt:
        print('\n사용자의 요청으로 종료합니다...')
    except:
        print('\n확인되지 않은 오류입니다...')
    finally:
        motor1.run(Raspi_MotorHAT.RELEASE)  # 종료시 모터 멈춤
    
if __name__ == '__main__':
    asyncio.run(main())

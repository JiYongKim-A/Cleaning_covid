# 0. 모듈 import
#-*-coding:utf-8-*-
import pygame  # pygame 모듈 사용
import random  # random이 필요함
import pymysql  # MYSQL 서버 모듈
import time  # 시간측정을 위해 time
import os # 파일경로 사용을 위한 os 모듈 사용
from dotenv import load_dotenv
load_dotenv();


# 1. 게임 초기화
pygame.init()  # 초기화 시켜주지 않을 시 라이브러리가 정상 작동 안할 수 도 있음

# 변경사항@@@
conn = pymysql.connect(host= os.environ.get('host'), user= os.environ.get('user'), password= os.environ.get('password'), db= os.environ.get('db'), charset="utf8") # LOCAL DB 연결
curs = conn.cursor()
sql = "select * from "+ os.environ.get('table') #SQL문

curs.execute(sql)
rows = curs.fetchall()
sql = ""


# 2. 게임 창 옵션 설정
game_size = [1400,800] #  게임 창 크기
screen = pygame.display.set_mode(game_size) # 게임 창 크기 적용

nowdirectory ="{0}/image/".format(os.getcwd()) # 현재 디렉토리 경로
background = pygame.image.load(nowdirectory+"covid19.png").convert_alpha() # 배경화면 로드
background = pygame.transform.scale(background,(game_size)) # 배경화면 사이즈 조정

title = 'shooting game'# 제목 설정
pygame.display.set_caption(title) # 제목 적용


# 3. 게임 내 필요한 설정들
# 변수 파트 --------------------------------------------------------------
clock = pygame.time.Clock() #fps 설정시 필요한 시간
    # moving_left,right , shot 은 지속 눌렀을때 끊기지 않고 자연스레 움직이게 하기 위해 사용 및 기본 False 로 지정
moving_left = False
moving_right = False
moving_up = False
moving_down = False
shot = False
bullet_MKlist=[] # 총알이 생성된 리스트

bulletTik = 0 # 총알 발사시 직선처럼 나가지 않게 하기 위해 사용
virus_MKlist = [] # 바이러스 생성 list
virus2_MKlist= [] # 바이러스2 생성 list
bossvirus_MKlist = [] # 보스 바이러스 생성 list
littlevirus_MKlist = []
score = 0 # 점수
text1=""; #텍스트입력
finishpage =0
level = 1
bosspart =0 # 0 일때 일반 , 1일때 보스등장 ,
Little = 0
#클래스&함수 파트------------------------------------------------------------------------

class obj : # 이미지사용할 객체의 클래스
    def __init__(self):
        self.location_x = 0  # 이미지 폭 (x좌표)
        self.location_y = 0 # 이미지 높이(y좌표)
        self.speed = 0 # 이미지 속도
        self.state = 0 # 맞은 함수ㄱㄹㄹㄹㄹㄹㄹㄹㄹ
    def apply_image(self,imgName): # 이미지 적용
        loadAddress = nowdirectory+imgName
        if imgName[-3:] =="png":
            self.img = pygame.image.load(loadAddress).convert_alpha()
        else:
            self.img = pygame.image.load(loadAddress)
        self.width_x, self.height_y = self.img.get_size() #이미지의 x좌표 크기 =width_x, y좌표 크기=height_y

    def change_size(self,width_x,height_y): # 이미지 크기 변경
        self.img = pygame.transform.scale(self.img, (width_x,height_y))
        self.width_x, self.height_y = self.img.get_size()

    def located(self): # 이미지의 location_x,y 위치로 위치시키기
        screen.blit(self.img,(self.location_x,self.location_y))

def crush (a,b):
    if(a.location_x - b.width_x  <= b.location_x) and(b.location_x <= a.location_x+a.width_x):
        if(a.location_y - b.height_y <= b.location_y) and (b.location_y <= a.location_y+a.height_y):
            return True
        else:
            return False
    else:
        return False


# 3-1) 사용할 객체 생성
    # 간호사 캐릭터
nurse =obj() #간호사 캐릭터 객체 생성
nurse.apply_image("nurse.png")
nurse.change_size(70,90)
nurse.location_x = round(game_size[0]/2 - nurse.width_x/2)
nurse.location_y = game_size[1] - nurse.height_y -20
nurse.speed = 10 # 초당 80번 while 반복중 10픽셀씩 움직인다.


#3-2 시작 대기화면
#(1)시작 대기
terminateVar = 0 # terminateVar을 통해 메인 이벤트 while 종료
while terminateVar ==0:
    clock.tick(80)
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            terminateVar=1
    startbackground = pygame.image.load(nowdirectory + "1background.png").convert_alpha()  # 배경화면 로드
    startbackground = pygame.transform.scale(startbackground, (game_size))  # 배경화면 사이즈 조정
    screen.blit(startbackground,(0,0))
    pygame.display.flip()
#3-3 시작 대기화면
#(2) 시작 대기

while terminateVar ==1:
    clock.tick(80)
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                terminateVar=2
    start2background = pygame.image.load(nowdirectory + "2background.png").convert_alpha()  # 배경화면 로드
    start2background = pygame.transform.scale(start2background, (game_size))  # 배경화면 사이즈 조정
    screen.blit(start2background, (0, 0))
    pygame.display.flip()


# 4. 메인 이벤트 (전체를 while로 메인 이벤트를 돌림)
while terminateVar==2: #terminateVar가 0이 아닐시 종료

    if(score > 1500*level):
        level+=1

    if 1000*level<=score<1000*level+500:
        if bosspart ==0:
            bosspart =1 # 이때 보스 생성

        elif bosspart == 2:
            bosspart = 2


    # 4-1). fps 설정
    clock.tick(80) # 초당 80번 화면이 변경된다
    # 4-2) 각종 입력감지
    for event in pygame.event.get(): # x 클릭시 종료
        if event.type == pygame.QUIT:
            terminateVar=3

        if event.type == pygame.KEYDOWN: # ESC 클릭시 종료
            if event.key == pygame.K_ESCAPE:
                terminateVar=3
            elif event.key == pygame.K_RIGHT:
                moving_right = True
            elif event.key == pygame.K_LEFT:
                moving_left = True
            elif event.key == pygame.K_UP:
                moving_up = True
            elif event.key == pygame.K_DOWN:
                moving_down = True
            elif event.key == pygame.K_SPACE:
                shot = True
                bulletTik = 0 # 스페이스 한번 눌렀을 시 안나가는것 방지를 위해 누를때마다 0 으로 초기화


        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                moving_right = False
            elif event.key == pygame.K_LEFT:
                moving_left = False
            elif event.key == pygame.K_UP:
                moving_up = False
            elif event.key == pygame.K_DOWN:
                moving_down = False
            elif event.key == pygame.K_SPACE:
                shot = False


    # 4-3) 입력 시간에 따른 변화
        # 키입력시 이미지가 움직이게 하는것을 구현
    if moving_right == True:
        nurse.location_x += nurse.speed  # speed 크기에 맞춰 이미지 x좌표 커짐
        if nurse.location_x >= game_size[0] - nurse.width_x:  # x좌표가 창의 크기-이미지 x좌표 보다 넘어가지 못하게 그자리 유지하도록 만듬
            nurse.location_x = game_size[0] - nurse.width_x
    elif moving_left == True:
        nurse.location_x -= nurse.speed
        if nurse.location_x <= 0:
            nurse.location_x = 0
    elif moving_up == True:
        nurse.location_y -= nurse.speed
        if nurse.location_y <= 0:
            nurse.location_y = 0
    elif moving_down == True:
        nurse.location_y += nurse.speed
        if nurse.location_y >=  game_size[1] - nurse.height_y:
            nurse.location_y = game_size[1] - nurse.height_y

        # space 눌렀을 때 bullet 생성
    if shot == True and bulletTik%8 ==0: # bulletTik을 총알 발생 빈도를 1/8로 낮춤
        bullet = obj()
        bullet.apply_image("bullets.png")
        bullet.change_size(20, 25)
        bullet.location_x = round(nurse.location_x + nurse.width_x / 2 - bullet.width_x / 2) # 캐릭터 위치 중앙에서 BULLET 출력
        bullet.location_y = nurse.location_y - bullet.height_y - 10
        bullet.speed = 15
        bullet_MKlist.append(bullet) # 스페이스 누를시 동안 리스트에 객체 저장
    bulletTik += 1  # bulletTik이 1씩 증가

        # 창 밖으로 나갈시 지우는 용도 리스트
    del_bullet_list =[]
    for i in range(len(bullet_MKlist)):
        bul = bullet_MKlist[i] #차레로 리스트에서 사용
        bul.location_y -= bul.speed
        if bul.location_y <= -bul.height_y: # 창 밖으로 나갈시 지우기 리스트에 idex 번호 저장
            del_bullet_list.append(i)
    del_bullet_list.reverse()

    for j in del_bullet_list:
        del bullet_MKlist[j]


        # 바이러스 생성 및 랜덤으로 떨어지는 구간
    if (random.random() > 0.98)and(bosspart == 0):
        virus = obj()
        virus.apply_image("virus.png")
        virus.change_size(50,50)
        virus.location_x = random.randrange(0, game_size[0]-virus.width_x-round(nurse.width_x/2))
        virus.location_y = 10
        virus.speed = 1
        virus_MKlist.append(virus)
        # 바이러스2 생성 및 랜덤으로 떨어지는 구간
    if (random.random() > 0.99)and(bosspart == 0):
        virus2 = obj()
        virus2.apply_image("virus2.png")
        virus2.change_size(70,70)
        virus2.location_x = random.randrange(0, game_size[0]-virus2.width_x-round(nurse.width_x/2))
        virus2.location_y = 10
        virus2.speed = 0.9
        virus2_MKlist.append(virus2)
        # 보스 바이러스 생성
    if(bosspart==1):
        bossvirus = obj()
        bossvirus.apply_image("bossvirus1.png")
        bossvirus.change_size(350,400)
        bossvirus.location_x = 300
        bossvirus.location_y = 10
        bossvirus.speed = 0.1
        bossvirus_MKlist.append(bossvirus)
        bosspart=2 # boss는 1개만 나오도록
    # 유도 바이러스 생성 랜덤
    if(level>=2)and(random.random()>0.95)and(bosspart ==0):
        littlevirus = obj()
        littlevirus.apply_image("littlevirus.png")
        littlevirus.change_size(150, 170)

        littlevirus.location_x = random.randrange(0, game_size[0]-littlevirus.width_x-round(nurse.width_x/2))
        littlevirus.location_y = 10
        littlevirus.speed = 2
        littlevirus_MKlist.append(littlevirus)


    # 바이러스 제거 리스트 index번호가 들어있음.
    del_virus_list=[]
    del_virus2_list=[]
    del_bossvirus_list=[]
    del_littlevirus_list=[]

     # 바이러스1
    for i in range(len(virus_MKlist)):
        virus = virus_MKlist[i]
        virus.location_y += virus.speed
        if virus.location_y >= game_size[1]:
            del_virus_list.append(i)
    del_virus_list.reverse()

    # 바이러스2
    for i in range(len(virus2_MKlist)):
        virus2 = virus2_MKlist[i]
        virus2.location_y += virus2.speed
        if virus2.location_y >= game_size[1]:
            del_virus2_list.append(i)
    del_virus2_list.reverse()

    # 보스 바이러스
    for i in range(len(bossvirus_MKlist)):
        bossvirus = bossvirus_MKlist[i]
        bossvirus.location_y += bossvirus.speed
        if bossvirus.location_y > game_size[1]/2+200:
            del_bossvirus_list.append(i)
    del_bossvirus_list.reverse()

    # 유도 바이러스
    for i in range(len(littlevirus_MKlist)):
        littlevirus = littlevirus_MKlist[i]
        littlevirus.location_y += littlevirus.speed

        if littlevirus.location_x<nurse.location_x:
            littlevirus.location_x+=littlevirus.speed

        else:littlevirus.location_x -=littlevirus.speed

        if littlevirus.location_y > game_size[1]/2+200:
            del_littlevirus_list.append(i)
    del_littlevirus_list.reverse()


    # 바이러스1 제거
    for j in del_virus_list:
        del virus_MKlist[j]
    # 바이러스2 제거
    for k in del_virus2_list:
        del virus2_MKlist[k]
    # 보스 바이러스 제거
    for l in del_bossvirus_list:
        del bossvirus_MKlist[l]

    # 유도 바이러스 제거
    for m in del_littlevirus_list:
        del littlevirus_MKlist[m]

    # 충돌 판정된 요소 리스트
    crush_virus_list = []
    crush_virus2_list = []
    crush_bossvirus_list =[]
    crush_bullet_list = []
    crush_littlevirus_list=[]

    # 충돌시 총알+바이러스1
    for i in range(len(bullet_MKlist)):
        for j in range(len(virus_MKlist)):
            crush_bullet = bullet_MKlist[i]
            crush_virus = virus_MKlist[j]

            if crush(crush_bullet, crush_virus) == True:
                crush_bullet_list.append(i)
                crush_virus_list.append(j)
    # 충돌시 총알+바이러스 2
    for i in range(len(bullet_MKlist)):
        for j in range(len(virus2_MKlist)):
            crush_bullet = bullet_MKlist[i]
            crush_virus2 = virus2_MKlist[j]

            if crush(crush_bullet, crush_virus2) == True:
                if crush_virus2.state == 0:
                    crush_virus2.apply_image("virus2_1.png")
                    crush_virus2.change_size(70, 70)
                    crush_virus2.state += 1
                    crush_bullet_list.append(i)
                elif crush_virus2.state == 1:
                    crush_virus2.apply_image("virus2_2.png")
                    crush_virus2.change_size(70, 70)
                    crush_virus2.state += 1
                    crush_bullet_list.append(i)
                elif crush_virus2.state == 2:
                    crush_virus2_list.append(j)
                    crush_bullet_list.append(i)

    # 충돌시 총알 + 보스 바이러스
    for i in range(len(bullet_MKlist)):
        for j in range(len(bossvirus_MKlist)):
            crush_bullet = bullet_MKlist[i]
            crush_bossvirus = bossvirus_MKlist[j]

            if crush(crush_bullet, crush_bossvirus) == True:
                if crush_bossvirus.state < 10:
                    crush_bossvirus.state+=1
                    crush_bullet_list.append(i)
                elif (10<= crush_bossvirus.state <20):
                    crush_bossvirus.state += 1
                    crush_bossvirus.apply_image("bossvirus2_2.png")
                    crush_bossvirus.change_size(350,400)
                    crush_bullet_list.append(i)
                elif crush_bossvirus.state ==20:
                    crush_bossvirus_list.append(j)
                    crush_bullet_list.append(i)
                    bosspart=0


    # 충돌시 총알 + 리틀 바이러스
    for i in range(len(bullet_MKlist)):
        for j in range(len(littlevirus_MKlist)):
            crush_bullet = bullet_MKlist[i]
            crush_virus = littlevirus_MKlist[j]

            if crush(crush_bullet, crush_virus) == True:
                crush_bullet_list.append(i)
                crush_littlevirus_list.append(j)

    # 한바이러스가 두번 맞았을시 등 같은 객체index 번호의 중복을 제거
    crush_bullet_list = list(set(crush_bullet_list))
    crush_virus_list = list(set(crush_virus_list))
    crush_virus2_list = list(set(crush_virus2_list))
    crush_bossvirus_list = list(set(crush_bossvirus_list))
    crush_littlevirus_list = list(set(crush_littlevirus_list))

    # 제거 대상 리스트 요소 역으로 돌려
    crush_bullet_list.reverse()
    crush_virus_list.reverse()
    crush_virus2_list.reverse()
    crush_bossvirus_list.reverse()
    crush_littlevirus_list.reverse()

    # 충돌 판정 True 객체 제거 + !!!점수획득구간!!!
    for RM_bul in crush_bullet_list:
        del bullet_MKlist[RM_bul]
    for RM_vr in crush_virus_list:
        del virus_MKlist[RM_vr]
        score +=50
    for RM_vr2 in crush_virus2_list:
        del virus2_MKlist[RM_vr2]
        score +=60
    for RM_BV in crush_bossvirus_list:
        del bossvirus_MKlist[RM_BV]
        score+= 500
    for RM_LV in crush_littlevirus_list:
        del littlevirus_MKlist[RM_LV]
        score +=60

    # 바이러스 객체와 캐릭터 충돌시 종료 변수 변경하여 종료화면으로 넘김
    for i in range(len(virus_MKlist)):
        virus = virus_MKlist[i]
        if crush(virus, nurse) == True:
            terminateVar=3
            time.sleep(1)
            finishpage = 1

    for j in range(len(virus2_MKlist)):
        virus2 = virus2_MKlist[j]
        if crush(virus2, nurse) == True:
            terminateVar=3
            finishpage = 1

    for k in range(len(bossvirus_MKlist)):
        bossvirus = bossvirus_MKlist[k]
        if crush(bossvirus, nurse) == True:
            terminateVar=3
            time.sleep(1)
            finishpage = 1

    for l in range(len(littlevirus_MKlist)):
        littlevirus = littlevirus_MKlist[l]
        if crush(littlevirus, nurse) == True:
            terminateVar=3
            time.sleep(1)
            finishpage = 1




    # 4-4)  # 배경,캐릭터,이미지 위치시키기
    screen.blit(background,(0,0))
    # 캐릭터 화면에 출력
    nurse.located()
    # 바이러스 화면에 출력
    for i in bullet_MKlist:
        i.located()
    for j in virus_MKlist:
        j.located()
    for k in virus2_MKlist:
        k.located()
    for l in bossvirus_MKlist:
        l.located()
    for m in littlevirus_MKlist:
        m.located()
    # 게임 종료시 "Gave Over"파트
    font = pygame.font.Font("{0}/font/arial.ttf".format(os.getcwd()), 25)
    text_score = font.render("Score : {0}".format(score), True, (255, 255, 255))
    screen.blit(text_score, (game_size[0] - 150, 5))

    # 4-5) 업데이트
    pygame.display.flip() # 업데이트 해줘야 창 업데이트가 된다

# 5. 게임 종료화면

while finishpage == 1:
    clock.tick(80)
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            pygame.quit()  # 게임 종료

    font_finish = pygame.font.Font("{0}/font/arial.ttf".format(os.getcwd()), 70)
    text_finish = font_finish.render("GAME OVER", True, (255, 0, 0))
    screen.blit(text_finish, (500, 350))
    pygame.display.flip()  # 업데이트 필수!!
    time.sleep(1) # 1초간 멈춤
    finishpage =2

while finishpage ==2:
    clock.tick(80)
    SIZE = width, height = 640, 240

    screen = pygame.display.set_mode(game_size)

    font1 = pygame.font.SysFont('malgungothic', 36)
    img1 = font1.render(text1, True, (255, 0, 0))
    rect1 = img1.get_rect()
    rect1.topleft = (game_size[0] - 300, 600)
    cursor1 = pygame.Rect(rect1.topright, (3, rect1.height))
    
    finishbackground = pygame.image.load(nowdirectory + "Recording.png").convert_alpha()  # 배경화면 로드
    finishbackground = pygame.transform.scale(finishbackground, (game_size))  # 배경화면 사이즈 조정

    screen.blit(finishbackground, (0, 0))

    font = pygame.font.SysFont('malgungothic', 36)
    text_score = font.render("Score : {0}".format(score), True, (0, 0, 0))
    screen.blit(text_score, (game_size[0] - 400, 350))

    pygame.display.flip()  # 업데이트 필수!!
    
    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if len(text1) > 0:
                    text1 = text1[:-1]
                    
            elif event.key == pygame.K_RETURN:
                
                curs = conn.cursor()
                sql = """insert into """ + os.environ.get('table')+ """ (name,score)  
                    values(%s,%s)"""
                # 쿼리문 sql 문에 넣기
                curs.execute(sql, (text1, score))
                # 벨류값 넣기 컬럼에맞게 순서대로 넣어야함
                conn.commit()
                finishpage = 3  # 게임 종료

            else:
                text1 += event.unicode
                
            img1 = font1.render(text1, True, (0, 0, 0))
            rect1.size = img1.get_size()
            cursor1.topleft = rect1.topright
            
        img1 = font1.render(text1, True, (0, 0, 0))
        rect1.size = img1.get_size()
        cursor1.topleft = rect1.topright
        screen.blit(img1, rect1)
    
    pygame.display.update()

    if time.time() % 1 > 0.5:
        pygame.draw.rect(screen, (255, 0, 0), cursor1)
    
    pygame.display.update()
    


while finishpage == 3:
    clock.tick(80)
    finish2background = pygame.image.load(nowdirectory + "RecordScore.png").convert_alpha()  # 배경화면 로드
    finish2background = pygame.transform.scale(finish2background, (game_size))  # 배경화면 사이즈 조정
    screen.blit(finish2background, (0, 0))
    sql = ""
    sql = "select * from "+ os.environ.get('table')+ " where score>0  order by score desc limit 5"
    curs.execute(sql)
    rows = curs.fetchall()
    font = pygame.font.SysFont('malgungothic', 36)
    
    
    if len(rows) > 5:
        text = ""
        for i in range(5):
            if i==0 :
                text = "1st"+" : " + rows[i][1] + " (" + format(rows[i][2]) + '  score' + ")"
            elif i==1 :
                text = "2nd"+" : " + rows[i][1] + " (" + format(rows[i][2]) + '  score' + ")"
            elif i ==2 :
                text = "3rd"+" : " + rows[i][1] + " (" + format(rows[i][2]) + '  score' + ")"
            else :
                text = str(i+1)+"th"+" : " + rows[i][1] + " (" + format(rows[i][2]) + '  score' + ")"
            text_score = font.render(text, True, (0, 0, 0))
            # text_score = font.render((i+1)+str+" : " + rows[i][1] + " (" + format(rows[i][2]) + '  score' + ")", True, (0, 0, 0))
            screen.blit(text_score, (game_size[0] - 500, 200+ (i*100)))

    else :
        text = ""
        for i in range(len(rows)):
            if i==0 :
                text = "1st"+" : " + rows[i][1] + " (" + format(rows[i][2]) + '  score' + ")"
            elif i==1 :
                text = "2nd"+" : " + rows[i][1] + " (" + format(rows[i][2]) + '  score' + ")"
            elif i ==2 :
                text = "3rd"+" : " + rows[i][1] + " (" + format(rows[i][2]) + '  score' + ")"
            else :
                text = str(i+1)+"th"+" : " + rows[i][1] + " (" + format(rows[i][2]) + '  score' + ")"
            text_score = font.render(text, True, (0, 0, 0))
            # text_score = font.render((i+1)+str+" : " + rows[i][1] + " (" + format(rows[i][2]) + '  score' + ")", True, (0, 0, 0))
            screen.blit(text_score, (game_size[0] - 500, 200+ (i*100)))
    
    pygame.display.flip()


    for event in pygame.event.get():
        if (event.type == pygame.KEYDOWN):
            finishpage = 4  # 게임 종료

pygame.quit()  # 게임 종료
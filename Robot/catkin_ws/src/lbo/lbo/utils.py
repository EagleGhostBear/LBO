import socket
import numpy as np
import cv2

# -	utils_skeleton.py : 

def xyh2mat2D(vec):
    euler_rad = vec[2] * np.pi / 180
    rot = np.array([np.cos(euler_rad), -np.sin(euler_rad), np.sin(euler_rad), np.cos(euler_rad)])
    trans = vec[0:2]

    T = np.identity(3)
    T[0:2, 0:2] = rot.reshape(2, 2)
    T[0:2, 2] = trans.reshape(-1)

    # print('vec', vec)
    # print('T', T)

    return T

def mat2D2xyh(T):
    vec = np.array([0.0, 0.0, 0.0])
    t = T[:2, 2]
    rot = T[:2, :2]
    vec[0] = t[0]
    vec[1] = t[1]
    vec[2] = np.arctan2(rot[1,0], rot[0,0])*180.0/np.pi

    return vec


# radian
def limit_angular_range(rad):

    if rad > np.pi:
        rad -= 2*np.pi

    if rad < -np.pi:
        rad += 2*np.pi

    if rad > np.pi:
        rad -= 2*np.pi

    if rad < -np.pi:
        rad += 2*np.pi

    return rad

def createLineIterator(P1, P2, img):

    # Bresenham's line algorithm을 구현해서 이미지에 직선을 그리는 메소드입니다.
    
    # 로직 순서
    # 1. 두 점을 있는 백터의 x, y 값과 크기 계산
    # 2. 직선을 그릴 grid map의 픽셀 좌표를 넣을 numpy array 를 predifine
    # 3. 직선 방향 체크
    # 4. 수직선의 픽셀 좌표 계산
    # 5. 수평선의 픽셀 좌표 계산
    # 6. 대각선의 픽셀 좌표 계산
    # 7. 맵 바깥 픽셀 좌표 삭제

   
    imageH = img.shape[0] #height
    imageW = img.shape[1] #width
    P1Y = P1[1] #시작점 y 픽셀 좌표
    P1X = P1[0] #시작점 x 픽셀 좌표
    P2X = P2[0] #끝점 x 픽셀 좌표
    P2Y = P2[1] #끝점 y 픽셀 좌표

    
    # 로직 1 : 두 점을 있는 백터의 x, y 값과 크기 계산
    
    dX = P2X - P1X
    dY = P2Y - P1Y
    dXa = abs(dX)
    dYa = abs(dY)

    # 로직 2 : 직선을 그릴 grid map의 픽셀 좌표를 넣을 numpy array 를 predifine

    itbuffer = np.empty(shape=(max(dXa, dYa) + 1, 3), dtype=np.float32)
    itbuffer.fill(np.nan)


    # 로직 3 : 직선 방향 체크
 
    negY = P1Y > P2Y
    negX = P1X > P2X
    
    # 로직 4 : 수직선의 픽셀 좌표 계산
    if P1X == P2X:
        itbuffer[:,0] = P1X
        if negY:
            itbuffer[:,1] = np.arange(P1Y, P2Y - 1, -1)
        else:
            itbuffer[:,1] = np.arange(P1Y, P2Y + 1)


    # 로직 5 : 수평선의 픽셀 좌표 계산
    elif P1Y == P2Y:
        itbuffer[:,1] = P1Y
        if negX:
          itbuffer[:, 0] = np.arange(P1X, P2X - 1, -1)
        else:
          itbuffer[:, 0] = np.arange(P1X, P2X + 1)

    # 로직 6 : 대각선의 픽셀 좌표 계산  

    else:        
        steepSlope = dYa > dXa 
        if steepSlope:
            slope = dX / float(dY)
            if negY:
                itbuffer[:,1] = np.arange(P1Y, P2Y - 1, -1)
            else:
                itbuffer[:,1] = np.arange(P1Y, P2Y + 1)
            itbuffer[:,0] = (slope * (itbuffer[:, 1] - P1Y)).astype(np.int) + P1X
        else:
            slope = dY / float(dX)
            if negX:
                itbuffer[:, 0] = np.arange(P1X, P2X - 1, -1)
            else:
                itbuffer[:, 0] = np.arange(P1X, P2X + 1)
            itbuffer[:, 1] = (slope * (itbuffer[:, 0] - P1X)).astype(np.int) + P1Y

    # 로직 7 : 맵 바깥 픽셀 좌표 삭제.
    colX = itbuffer[:, 0]
    colY = itbuffer[:, 1]
    itbuffer = itbuffer[(colX >= 0) & (colY >= 0) & (colX < imageW) & (colY < imageH)]
    
    # itbuffer = []
    itbuffer[:,2] = img[itbuffer[:,1].astype(np.uint),itbuffer[:,0].astype(np.uint)]

    return itbuffer
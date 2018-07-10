#-*- coding: UTF-8 -*-

import os
import sys
import cv2
import collections
images_path="D:/check_data/img/beijing_bill"
rotation_result_path='./rotation_result/'
if not os.path.exists(rotation_result_path):
    os.mkdir(rotation_result_path)
import numpy as np
PI=3.1415926
def paintOutskirt(img):
    # 转为黑白图
    row, col,c= img.shape
    edgePos = []
    for i in range(col):
        edgePos.append((0, i))
        edgePos.append((row - 1, i))
    for i in range(1, row):
        edgePos.append((i, 0))
        edgePos.append((i, col - 1))
    offset = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    tempImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    th, tempImg = cv2.threshold(tempImg, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 计算发票颜色均值，只算白色的部分像素
    means =[0.0,0.0,0.0]
    # 从最外一圈的点遍历找出黑色区域并填入平均色
    pixelCount=0
    for i in range(0, row, 20):
        for j in range(0, col, 20):
            if tempImg[i, j] != 0:
                for k in range(3):
                    means[k] += img[i, j, k]
                pixelCount += 1
    for k in range(3):
        means[k] /= float(pixelCount)
    visitedPos = set()
    for initPos in edgePos:
        i, j = initPos
        if tempImg[i, j] == 0 and initPos not in visitedPos:
            q = collections.deque([initPos])
            visitedPos.add(initPos)
            img[i, j] = means
            while q:
                posX, posY = q.popleft()
                for ox, oy in offset:
                    newX = ox + posX
                    newY = oy + posY
                    if newX >= 0 and newX < row and newY >= 0 and newY < col:
                        if (newX, newY) not in visitedPos and tempImg[newX, newY] == 0:
                            visitedPos.add((newX, newY))
                            img[newX, newY] = means
                            q.append((newX, newY))
    return img
i=1
for image in os.listdir(images_path):
    print(i)
    image_path=os.path.join(images_path,image)
    img1=cv2.imread(image_path,1)
    cv2.imwrite(rotation_result_path+image,img1)
    height,width,channel=img1.shape
    img2 = paintOutskirt(img1)    #把图片周围的黑色空隙填上图片的背景均值
    img=img2[0:int(height/2),:,2] #利用半张图做霍夫变换，防止出现太多的竖直线
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    img=cv2.Canny(img,10,500)
    output=cv2.HoughLines(img,rho=1,theta=0.1*PI/180,threshold=100)
    num=output.shape[0]
    output=output[0:int(num/3)]
    #for line in output:
    rho,theta=output[0][0]
    a = np.cos(theta)
    b = np.sin(theta)
    if a!=0 and b!=0:
        x1=0
        y1=int(rho/b)
        x2=1000
        y2=int((rho-x2*a)/b)
        #print(x1,y1,x2,y2)
        cv2.line(img1, (x1, y1), (x2, y2), (0, 255, 0), 1)
    angle=(theta-PI/2)/PI*180
    rotation_mat=cv2.getRotationMatrix2D((width/2,height/2),angle=angle,scale=1)
    img2=cv2.warpAffine(img2,rotation_mat,(width,height))
    name=image.split('.')[0]
    suffix=image.split('.')[1]
    cv2.imwrite(rotation_result_path+name+'_1.'+suffix,img2)
    i=i+1

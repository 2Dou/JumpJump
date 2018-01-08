#!/usr/bin/python
#encoding: utf-8

import os, math, time
from random import randint
from image import Image


def parse(file):
    img = Image(file)

    cur_pos = find_cur_pos(img)
    assert(cur_pos != None)

    next_pos = find_next_pos(img, cur_pos)
    assert(next_pos != None)

    img.line(cur_pos, next_pos)
    jump(img.width, img.height, cur_pos, next_pos)

    img.save()
    img.close()

def find_next_pos(img, cur):
    return find_by_circle(img, cur) or find_by_platform(img, cur)

def find_cur_pos(img):
    '''
    查找棋子当前位置
    通过棋子底部颜色范围，搜索棋子左右点，以中点作为棋子当前位置
    '''
    width, height = img.width, img.height

    local = [(width, 0), (0, 0)]
    def put_in(x, y):
        left, right = local[0], local[1]
        if x < left[0]:
            left = (x, y)
            local[0] = left
        if x >= right[0]:
            right = (x, y)
            local[1] = right

    for x in range(int(width * 0.1), int(width * 0.9)):
        for y in range(int(height * 0.52), int(height * 0.62)):
            pixel = img.getpixel((x, y))
            r, g, b = pixel[0], pixel[1], pixel[2]
            if r < 45 and r > 40 and \
                g < 45 and g > 40 and \
                b < 75 and b > 70:
                put_in(x, y)

            if r < 60 and r > 50 and \
                g < 60 and g > 50 and \
                b < 90 and b > 80:
                put_in(x, y)

    left, right = local[0], local[1]
    if left[0] == width:
        return None

    x = int((left[0] + right[0]) / 2)
    y = int((left[1] + right[1]) / 2)
    return (x, y)

def find_by_platform(img, cur):
    '''
    从上往下搜索第一个与背景不同的颜色，作为下一跳台顶点，然后有两种方式查找落点：
    1.根据相同颜色计算平台中心
    2.根据斜率、当前位置、顶点x算落点（当前位置偏太多可能导致跳跃失败）
    '''

    width, height = img.width, img.height

    ite = None

    if cur[0] < width * 0.5:
        #棋子在左边，落点在右边
        ite = range(int(width * 0.52), int(width * 0.9))
    else:
        #棋子在右边，落点在左边
        ite = range(int(width * 0.1), int(width * 0.48))

    next_top, top_pixel = None, None
    for y in range(int(height * 0.3), int(height * 0.52)):
        # 背景色，因为有渐变，所以每行重新获取背景色
        bg_pixel = img.getpixel((width - 1, y))

        for x in ite:
            pixel = img.getpixel((x, y))

            # 渐变问题，允许差值
            if abs(pixel[0] - bg_pixel[0]) > 8 \
                or abs(pixel[1] - bg_pixel[1]) > 8 \
                or abs(pixel[2] - bg_pixel[2]) > 8:
                next_top = (x, y)
                top_pixel = pixel
                break
        if next_top != None:
            break

    if next_top == None:
        return None

    '''
    搜索平台左右两点，通过左右两点计算中心点
    '''
    left, right = None, None

    # 搜索左顶点
    x, y = next_top
    while True:
        while True:
            # 向左查找相同颜色点
            if not same_color(img.getpixel((x - 1, y)), top_pixel):
                break
            x -= 1

        # 向下一个像素
        if not same_color(img.getpixel((x, y + 1)), top_pixel):
            break
        y += 1
    if x != next_top[0] and y != next_top[1]:
        left = (x, y)

    if left != None:
        x, y = next_top
        while True:
            while True:
                # 向右查找相同颜色点
                if not same_color(img.getpixel((x + 1, y)), top_pixel):
                    break
                x += 1

            # 向下查找相同颜色点
            if not same_color(img.getpixel((x, y + 1)), top_pixel):
                break
            y += 1
        if x != next_top[0] and y != next_top[1]:
            right = (x, y)

    img.mark(next_top, "top")
    if left != None and right != None:
        img.mark(left, "left")
        img.mark(right, "right")
        r = (int((left[0] + right [0]) / 2), int(left[1] + right [1]) / 2)
        print("查找到平台{}".format(r))
        return r

    '''
    这种情况通过斜率计算落点
    '''
    # 继续向右搜索相同颜色像素，以中间为顶点
    right = next_top
    for x in range(next_top[0] + 1, ite[len(ite) - 1]):
        pixel = img.getpixel((x, y))
        if pixel[0] == top_pixel[0] and \
            pixel[1] == top_pixel[1] and \
            pixel[2] == top_pixel[2]:
            right = (x, y)
        else:
            break

    x = int((next_top[0] + right[0]) / 2)
    y = int((next_top[1] + right[1]) / 2)

    k = 0.58 # 斜率
    y = cur[1] - k * float(x - cur[0])

    return (x, int(y))


def find_by_circle(img, cur):
    '''
    通过查找下一落点上的小圆点确定落点
    '''
    width, height = img.width, img.height

    ite = None

    if cur[0] < width * 0.5:
        #棋子在左边，落点在右边
        ite = range(int(width * 0.52), int(width * 0.9))
    else:
        #棋子在右边，落点在左边
        ite = range(int(width * 0.1), int(width * 0.48))

    '''
    通过斜率计算斜线上的点并判断颜色
    '''
    one_of_circle = None
    for x in ite:
        '''
        通过斜率计算斜线上的位置，并判断是否和圆点颜色一样
        '''
        y = int(cur[1] - 0.58 * abs(cur[0] - x))
        pixel = img.getpixel((x, y))
        r, g, b = pixel[0], pixel[1], pixel[2]
        if r == 245 and g == 245 and b == 245:
            one_of_circle = (x, y)
            break

    if one_of_circle == None:
        return None

    # 继续向左查找相同颜色，作为点A
    while True:
        x, y = one_of_circle
        if not same_color(img.getpixel((x - 1, y)), img.getpixel(one_of_circle)):
            break
        one_of_circle = (x - 1, y)

    # 向右查找相同颜色，作为点B
    anohter_of_circle = None
    for x in range(1, int(width * 0.1)):
        x = one_of_circle[0] + x
        y = one_of_circle[1]

        if not same_color(img.getpixel((x, y)), img.getpixel(one_of_circle)):
            break
        anohter_of_circle = (x, y)

    if anohter_of_circle == None:
        return None

    # 向下/上查找相同颜色点，作为点C，然后以BC中点作为圆心
    # ABC在圆点上大致位置如下：
    #    **
    #  A*  *B
    # *      *
    # *      *
    #  C*  **
    #    **
    bottom = None
    ite_y = range(1, int(width * 0.1))
    if cur[0] < width * 0.5:
        #落点在右边，one_of_circle在左下角，所以向上搜索
        ite_y = map(lambda x: -x, ite_y)
    for y1 in ite_y:
        x = one_of_circle[0]
        y = one_of_circle[1] + y1

        if not same_color(img.getpixel((x, y)), img.getpixel(one_of_circle)):
            break
        bottom = (x, y)

    if bottom == None:
        return None

    r = ((bottom[0] + anohter_of_circle[0]) / 2, (bottom[1] + anohter_of_circle[1]) / 2)
    print("查找到圆点{}".format(r))
    return r

def jump(width, height, cur, next):
    '''
    计算触摸时长、模拟触摸
    '''
    x, y = int(width * 0.7) + randint(0, 15), int(height * 0.3) + randint(0, 15)
    dis = int(math.sqrt((cur[0] - next[0])**2 + (cur[1] - next[1])**2))

    # 模拟误差
    dis += randint(-int(width*0.005), int(width*0.005))

    '''
    不同分辨率下，系数P不同，需要查找

    1600x2560机型推荐0.92
    1440x2560机型推荐1.039
    1080x1920机型推荐1.392
    720x1280机型推荐2.078
    '''
    P = 1.392
    os.system('adb shell input swipe %d %d %d %d %d'  % (x, y, x+randint(-2,2), y+randint(-2,2), int(dis * P)))

def same_color(p1, p2):
        return p1[0] == p2[0] \
                and p1[1] == p2[1] \
                and p1[2] == p2[2]

def abs(x):
    if x < 0:
        return -x
    return x


def main():
    while True:
        # 保留最后几跳图片
        for i in range(10):
            os.system("adb shell screencap -p | perl -pe 's/\\x0D\\x0A/\\x0A/g' > jump_tmp{}.png".format(i))
            parse('./jump_tmp{}.png'.format(i))
            time.sleep(1)

if __name__ == '__main__':
    main()
    # parse('jump_tmp1.png')

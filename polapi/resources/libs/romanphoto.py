#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  findrect.py
#
#  Copyright 2019 belese <belese@belese>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
import math
from PIL import Image, ImageDraw,ImageFont
import textwrap

STEP = 10
WIDTHMIN = 40
HEIGHTMIN = 30

class Dialogues :

    TITLE = ('t','T')
    NARRATOR = ('n','N')
    STARING = ('s','S')

    def __init__(self,data) :
        print ('init dialiogue',data)
        self.title = None
        self.narrator = None
        self.dialogues = []
        self.starring = []
        self.nbpersons = 0

        for line in data.split("|") :
            if not line[1:] :
                continue
            if line[0] in self.TITLE :
                self.title = line[1:]
            elif line[0] in self.NARRATOR :
                self.narrator = line[1:]
            elif line[0] in self.STARING :
                self.starring.append(line[1:])
            elif line[0].isdigit()  :
                self.dialogues.append((int(line[0]),line[1:]))
                self.nbpersons = max(int(line[0])+1,self.nbpersons)



class RomanPhoto :
    def __init__(self,img,resolution,faces,dialogues) :
        self.resolution = resolution
        self.faces = faces
        self.nbfaces = len(faces)
        self.dialogues = dialogues
        self.im = img
        print "Image size",self.im.size
        self.draw = ImageDraw.Draw(self.im)


    def getBubbles(self,font="resources/fonts/traveling-_typewriter.ttf",size=28) :
        squ = self.faces[:]
        print ('init squ',squ)
        #for rectangle in self.faces :
        #    self.draw.rectangle((rectangle[0],rectangle[1],rectangle[0]+rectangle[2],rectangle[1] +rectangle[3]),fill="blue")

        font = ImageFont.truetype(font,size)
        border = 10

        if self.dialogues.narrator :
            narrator = self.findNarrator(squ[:])
            square,n = self.getSquareBubble(self.dialogues.narrator,narrator,(0,0,0,0),font,wr=20)
            self.im.paste(n, (square[0],square[1]))
            squ.append((square[0],square[1],n.size[0]+border,n.size[1]+border))

        rects = self.findRectangle(squ[:])

        for faceid,text in self.dialogues.dialogues :
            print ('do dialogue',faceid,text)
            square,bull = self.getSquareBubble(text,rects,self.faces[faceid],font)
            if square :
                pos = self.findBestPlace(square,self.faces[faceid],bull.size)
                #self.draw.rectangle((square[0],square[1],square[0]+square[2],square[1] +square[3]))
                arrow = self.findArrow(self.faces[faceid],(pos[0],pos[1],bull.size[0],bull.size[1]))
                self.draw.polygon(arrow,fill="white")
                xb = pos[0] - border if pos[0] - border > 0 else 0
                yb = pos[1] - border if pos[1] - border > 0 else 0

                squ.append((xb,yb,bull.size[0]+2*border,bull.size[1]+2*border))
                if arrow[2][1] >   pos[1] + bull.size[1] + border:
                    xr = int(min(arrow[0][0],arrow[2][0]))
                    yr = arrow[0][1] + border
                    xr2 = int(max(arrow[1][0],arrow[2][0]))
                    squ.append((xr,yr,xr2-xr,arrow[2][1]-yr))
                    #self.draw.rectangle((xr,yr,xr2,arrow[2][1]))                
                self.im.paste(bull, pos)
                print ('*****************************Draw Bull',bull.size,pos)
                rects = self.findRectangle(squ[:],pos[1]+20)
            else :
                break
        return self.im

    def findNarrator(self,rects) :
        rect = self.findRectangle(rects)
        def key(val) :
            return val[1] == 0 or val[1] + val[3] >= self.resolution[1] - (self.resolution[1] % STEP)
        return filter(key,rect)

    def findRectangle(self,rects,starty=0) :
        print ('find rectangele',rects,starty)
        rects = sorted(rects,key = lambda x : (x[0],x[1]))
        rectangle = []
        lines = self.findLines(rects)
        lines = lines[starty/STEP:]
        #print ('after',lines)
        for i,line in enumerate(lines) :
            pos = 0
            for j,value in enumerate(line) :
                if value > 0 :
                    up = self.findUp(pos,value,lines[0:i]) if i > 0 else 0
                    down = self.findDown(pos,value,lines[i:]) if i < len(lines) else 0
                    pose = (pos,(i+starty/STEP-up)*STEP,value,(down + up)*STEP)
                    if pose[2] >= WIDTHMIN and pose[3] >= HEIGHTMIN :
                        rectangle.append(pose)
                pos+=abs(value)
        rectangle = set(rectangle)
        def key(val) :
            return (math.sqrt(val[0]*val[0]+val[1]*val[1]),-val[2]*val[3])
        rectangle = sorted(rectangle,key=key)
        print ('we have rectangles',rectangle)
        return rectangle

    def findLines(self,rects) :
        lines = []
        for line in range(0,self.resolution[1],STEP) :
            lines.append([])
            pos = 0
            for rect in rects :
                if line in range(rect[1],rect[1]+rect[3]) :
                    delta=0
                    if rect[0] + rect[2] < pos :
                        continue
                    if rect[0] >= 0 :
                        lines[line/STEP].append(rect[0] - pos)
                        if rect[0] > pos :
                            pos=rect[0]
                            lines[line/STEP].append(-rect[2])
                        else :
                            delta = pos - rect[0]
                            lines[line/STEP][-1]=lines[line/STEP][-1]-rect[2]+delta

                    pos+=rect[2]-delta
            lines[line/STEP].append(self.resolution[0] - pos)
        return lines

    def isinrect(self,start,lenght,line) :
        pos = 0
        for i,val in enumerate(line) :
            pos += abs(val)
            if start < pos :
                if val < 0 :
                    return True
                if start + lenght <= pos :
                    return False


    def findDown(self,start,lenght,lines) :
        for i,val in enumerate(lines) :
            if self.isinrect(start,lenght,val) :
                return  i
        return len(lines)

    def findUp(self,start,lenght,lines) :
        lines.reverse()
        return  self.findDown(start,lenght,lines)

    def findArrow(self,face,bull,border = 40,larger=40) :        
        xf,yf,wf,hf = face
        xb,yb,wb,hb = bull
        xc = xf + wf/2
        yc = yf + hf/2

        larger = larger if larger < wb else wb
        border = border if larger + 2* border < wb else (wb - larger) / 2

        print ('find arrow position',yb,hb,yf)

        #todo check with x instead
        if yb + hb < yf + 20 or yb > yf + hf - 20 :
            print ('arrow top or bottom')
            
            larger = larger if larger < wb else wb
            border = border if larger + 2* border < wb else (wb - larger) / 2
            
            #top or bottom
            if xb + wb < xf :
                #left
                print('left')
                x1 = xb + wb -border
                x0 = x1 - larger
            elif xb > xf + wf :
                print('right')
                #right
                x0 = xb + border
                x1 = x0 + larger
            else :
                #center
                print('center max',wf,xf-xb,xb+wb-xf-wf)
                if max(wf,xf-xb,xb+wb-xf-wf) == xf-xb :
                    #left center arrox
                    x1 = xf - border
                    x0 = x1 - larger
                elif max(wf,xb+wb-xf-wf) == wf  :
                    #center arrow
                    x0 = xc - larger/2
                else :
                    x0 = xf + wf + border

                x0 = xb + border if x0 - border < xb else x0
                x0 = xb + wb - border -larger if x0 + larger + border > xb + wb else x0
                x1 = x0 + larger

            x = x0 + (x1 - x0)/2

            if yb + hb < yf + 20:
                #top
                print ('top')
                y0 = yb + hb
                y1 = y0
                angle = math.atan2(yc-y0,xc-x)
                yprim = int(math.sin(angle) * larger)
                y2 = yb + hb + yprim
            else :
                print ('bottom')
                y0 = yb
                y1 = y0
                angle = math.atan2(y0-yc,xc - x)
                yprim = int(math.sin(angle) * larger)
                y2 = yb - yprim
            print angle
            xprim = int(math.cos(-angle) * larger)
            x2 = x + xprim

        else :
            #right or left
            
            larger = larger if larger < hb else hb
            border = border if larger + 2* border < hb else (hb - larger) / 2
            
            yc= yf + 2*hf/3
            y0 = yc - larger/2
            y0 = yb + border if y0 < yb +border else y0
            y0 = yb + hb - border - larger if y0 >yb + hb - larger - border else y0
            y1 = y0 + larger
            y = y0 + (y1 - y0)/2
            if xb  <= xf :
                #left
                print ('***************arrow left')
                x0 = xb + wb
                x1 = x0
                angle = math.atan2(xc-x0,yc-y)
                xprim = int(math.sin(angle) * larger)
                x2 = xb + wb + xprim
            else :
                x0 = xb
                x1 = x0
                angle = math.atan2(x0-xc,yc-y)
                xprim = int(math.sin(angle) * larger)
                x2 = xb  - xprim
            yprim = int(math.cos(-angle) * larger)
            y2 = y + yprim

        return ((x0,y0),(x1,y1),(x2,y2))

    def findBestPlace(self,rect,face,bull) :
        print ('rect = ',rect)
        xr,yr,wr,hr = rect
        xf,yf,wf,hf = face
        wb,hb = bull

        top = False
        left = False
        right = False

        #top
        if yf >= yr + hr :
            top = True

        if xf >= xr + wr :
            left = True

        if xf + wf <= xr :
            right = True
        
        if left or right :            
            y = yf - hb/2
            y = max(y,yr)
            y = y if y + hb <= yr + wr else yr + hr - hb            
            if left :
                x = max(xf - wb - 20,xr)                
            else :
                x = max(xf + wf + 20,xr)                
        else :            
            if xf <= self.resolution[0]/2 :                                
                x = xf -wb                
                x = max(x,xr)
                x = x if x + wb <= xr + wr else xr + wr - wb

            else :                                
                x = xf                
                x = max(x,xr)
                x = x if x + wb <= xr + wr else xr + wr - wb                
            if top :
                y = yr + hr/3 - hb/2 - 20                
                y = max(y,yr)
                y = y if y + hb <= yr + hr else yr
            else :
                y = yr + hb/3
                y = y if y + hb < yr + hr else yr + hr/2 - hb/2
    
        return (x,y)

    def getSquareBubble(self,text,square,face,font,wr=7,hr=3) :
        center = (face[0]+face[2]/2,face[1]+face[3]/2)
        text_size = font.getsize(text)
        area = (text_size[0]*1.4) * (text_size[1]*1.4)
        squares = filter(lambda x: (x[2] * x[3]) >= area,square)
        if not squares :
            return None,None
        else :
            def keysort(value) :
                x,y,w,h = value
                weight = 0
                proximityx = 0 if center[0] >= x and center[0] <= x+w else (min([abs(center[0] - x),abs(center[0] - x - w)]))
                proximityy = 0 if center[1] >= y and center[1] <= y+h else (min([abs(center[1] - y),abs(center[1] - y - h)]))
                weight += 3*(proximityy + proximityx)
                weight += y*4
                weight += float(text_size[0])/w*500
                return weight

            squares = sorted(squares,key=keysort)
            find = False
            for square in squares :
                x,y,w,h = square
                length = wr
                heigth = hr
                while True:
                    if length * heigth >= area:
                        find = True
                        break
                    if heigth == h and length == w :
                        break

                    if length >= w :
                        heigth+= 1
                    elif heigth >= h :
                        length += 1
                    else :
                        length+=wr
                        heigth+=hr
                    if length > w :
                        lentgh = w
                    if heigth > h :
                        heigth = h
                if find :
                    break
                else :
                    print ('second choice')
            if not find :
                length = squares[0][2]
                square = squares[0]
            return square,self.getBullText(text,length,font)


    def getBullText(self,text,length,font) :
            text_size = font.getsize(text)
            average_char_width =  1.2 * text_size[0]/len(text)
            text = textwrap.wrap(text, width=int(length/average_char_width))
            line_height = 0
            bull_width = 0
            for line in text  :
                size = font.getsize(line)
                bull_width = max(bull_width,size[0])
                line_height = max(line_height,size[1])
            bull_width+=20
            bull_height= (line_height*len(text)) + 20
            bull_img = Image.new('RGBA', (bull_width,bull_height), "white")
            bull_draw = ImageDraw.Draw(bull_img)
            y=10
            x=10
            for line in text  :
                bull_draw.text((x, y), line, font=font,fill="black")
                y+=line_height
            return bull_img


"""
faces = [[0,0,100,80],[480,16,200,180]]
texts = ["nUn vendredi soir a forest","1Bonjour gros, dis moi un peu comment va?","0Hello, ca va","0Bof pas grand chose de beau, tu sais","1ok, pourtant je n'y croyais pas de trop","0oui"]

a = RomanPhoto((640,383),faces,texts)
im = a.getBubbles()
im.show()
"""
"""
f = faces[:]
for rectangle in faces :
    draw.rectangle((rectangle[0],rectangle[1],rectangle[0]+rectangle[2],rectangle[1] +rectangle[3]),fill="blue")
rects = findRectangle((640,480),faces)


for i,text in enumerate(texts) :
    faceid = int(text[0])
    text = text[1:]
    square,bull = getSquareBubble(text,rects,faces[faceid])
    if square :
        pos = findBestPlace(square,faces[faceid],bull.size)
        draw.rectangle((square[0],square[1],square[0]+square[2],square[1] +square[3]))
        f.append((pos[0],pos[1],bull.size[0],bull.size[1]))
        im.paste(bull, pos)
        rects = findRectangle((640,480),f,pos[1]+20)
    else :
        break


    #im.show()

im.show()
"""

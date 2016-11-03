# Python program to find all  
# rectangles filled with 0 
  
def findend(i,j,a,output,index): 
    x = len(a) 
    y = len(a[0]) 
  
    # flag to check column edge case, 
    # initializing with 0 
    flagc = 0
  
    # flag to check row edge case, 
    # initializing with 0 
    flagr = 0
  
    for m in range(i,x):  
  
        # loop breaks where first 1 encounters 
        if a[m][j] == 1:  
            flagr = 1 # set the flag 
            break
  
        # pass because already processed 
        if a[m][j] == 5:  
            continue
  
        for n in range(j, y):  
  
            # loop breaks where first 1 encounters 
            if a[m][n] == 1: 
                flagc = 1 # set the flag 
                break
  
            # fill rectangle elements with any 
            # number so that we can exclude 
            # next time 
            a[m][n] = 5
  
    
    if flagc == 1: 
        output[index].append(n-1) 
    else: 
        # when end point touch the boundary 
        output[index].append(n)  
  
    if flagr == 1: 
        output[index].append( m-1) 
    else: 
        # when end point touch the boundary 
        output[index].append(m)  
  
  
def get_rectangle_coordinates(a): 
  
    # retrieving the column size of array 
    size_of_array = len(a)  
  
    # output array where we are going 
    # to store our output  
    output = []  
  
    # It will be used for storing start 
    # and end location in the same index 
    index = -1
  
    for i in range(0,size_of_array): 
        for j in range(0, len(a[0])): 
            if a[i][j] == 0: 
  
                # storing initial position  
                # of rectangle 
                output.append([j, i])  
  
                # will be used for the  
                # last position 
                index = index + 1        
                findend(i, j, a, output, index)
  
  
    print (output) 
  
# driver code 
tests = [ 
  
            [0, 0, 0, 0, 0, 0, 0,0], 
            [0, 0, 0, 0, 0, 0, 0,0], 
            [0, 0, 0, 0, 0, 0, 0,0], 
            [0, 0, 1, 1, 1, 0, 0,0], 
            [0, 0, 1, 1, 1, 0, 0,0],  
            [0, 0, 1, 1, 1, 0, 0,0],  
            [0, 0, 0, 0, 0, 0, 0,0], 
            [0, 0, 0, 0, 0, 0, 0,0],
  
        ] 
  

print tests
#get_rectangle_coordinates(tests) 


result = []
x=0
y=0
tmp = [x,y]
while True :
    lastx = x
    lasty = y
    x+=2
    y+=1    
    flag = True if x +2 < len(tests) and y + 1 < len(tests[0]) else False
    if flag :
        for i in range(x) :
            for j in range(y) :
                if tests[i][j] == 1 :
                    flag = False
                    break            
    if not flag  :
        tmp.append(lastx)
        tmp.append(lasty)
        result.append(tmp)
           
        if x +2 < len(tests):
            print ('here',x,y)
            x=lastx+1
            y=0
        else :
            print ('here2',x,y)
            x = 0            
            if y + 1 < len(tests[0]) :                    
                y = lasty+1            
            else :
                break                                    
            tmp = [x,y]
print result
def solveNqueen(chessboard,nth,result):
    if nth == len(chessboard):
        # print cbToStr(chessboard)+'\n'
        result.append(cbToStr(chessboard))
    else:
        for i in range(len(chessboard[0])):
            if(isValid(chessboard,nth,i)):
                chessboard[nth][i]='Q'
                solveNqueen(chessboard,nth+1,result)
                chessboard[nth][i]='.'
                
                
def isValid(chessboard,n,i):
    # print cbToStr(chessboard)
    l=len(chessboard[0])
    ## same column
    for j in range(0,len(chessboard)):
        if chessboard[j][i]=='Q':
            return False
    
    for j in range(1,l):
        locs=[(n+j,i+j),(n-j,i+j),(n+j,i-j),(n-j,i-j)]
        # print x,y,i,n,chessboard[y][x]
        for y,x in locs:            
            if y>=l or y<0 or x<0 or x>=l:
                continue
            if chessboard[y][x]=='Q':                
                # print x,y,i,n,'\n',cbToStr(chessboard)
                return False
    # print '[%s,%s]'%(n,i),'\n',cbToStr(chessboard)
    return True
   

def cbToStr(chessboard):
    st=''
    for row in chessboard:
        st += ' '.join(row)+'\n'
    return st.strip('\n')
    
def main():
    result=[]
    chessboard=[]
    order = 5
    for i in range(order):
        chessboard.append(['.' for i in range(order)])
     
    # print cbToStr(chessboard)+'\n' 
    solveNqueen(chessboard,0,result)
    print len(result),'solutions'
    raw_input('[puase]:')
    print '\n\n'.join( result)
    
if __name__=='__main__':
    main()
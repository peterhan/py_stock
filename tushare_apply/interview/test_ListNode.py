class ListNode():
    def __init__(self,value,next):
        self.value=value
        self.next=next
        
    def append(self,value):
        n=self
        while n.next is not None:
            n=n.next
        n.next = ListNode(value,None)
        
    def push(self,value):
        self.next=ListNode(self.value,self.next)
        self.value=value
    
    def __str__(self):
        n=self
        s=''
        while n is not None:
            s += '%s => '%n.value
            n = n.next
        return s.strip('=> ')
        
    def reverse(self):
        prev = None
        current = self
        while current is not None:
            next = current.next
            current.next = prev
            prev = current
            current = next
            # print prev,next
        return  prev 
            
        
def main():
    a=None
    for i in [1,2,3,2,1,4]:
        if not a:
            a=ListNode(i,None)
        else:            
            # a.push(i)
            a.append(i)
    print a
    print a.reverse()
    
    
    
if __name__ == '__main__':
    main()
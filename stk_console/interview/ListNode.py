class Node(object):
    def __init__(self,data):
        self.data=data
        self.next=None
        
class ListNode(object):
    def __init__(self):
        self.head = None
        
    def add(self,data):
        node = Node(data)
        node.next = self.head
        self.head = node
        
    def __str__(self):
        s=''
        nd = self.head
        while nd !=None:
            s+= '%s'%nd.data+'=>'            
            nd = nd.next
        return s
        
    def reverse(self):
        pre = self.head
        p = self.head.next
        next = None
        self.head.next=None
        while p!=None :
            next = p.next
            p.next = pre
            pre = p
            p = next
        self.head = pre
            
            
def main():
    ln = ListNode()
    for i in range(10):
        ln.add(i)
    print ln 
    ln.reverse()
    print ln
    
main()
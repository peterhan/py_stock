class TreeNode(object):
    def __init__(self,data):
        self.data=data
        self.left=None
        self.right=None
        
    def __str__(self):
        s= '%s '%self.data
        s+='%s %s'%(self.left,self.right)
        return s

        
def flipNode(root):
    if root == None:
        return root
    tmp = flipNode(root.left)
    root.left = flipNode(root.right)
    root.right = tmp
    return root
    

def main():
    tn=TreeNode(3)
    tn.left=TreeNode(2)
    tn.right=TreeNode(1)
    tn.left.left=TreeNode(0)
    print tn
    print flipNode(tn)

if __name__ =='__main__':
    main()
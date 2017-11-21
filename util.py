class ConfLoader(object):
    def __init__(self,conf_file_name=None):
        self.holding={}
        if conf_file_name is None:
            conf_file_name='holding.txt'
        for l in open(conf_file_name):
            if l.startswith('#'):
                continue
            row=l.strip().split()
            code=row.pop(0)
            self.holding[code]=row
            
if __name__=='__main__':
    conf = ConfLoader()
    print conf.holding
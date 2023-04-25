import os

def FindAndRemove(path,pattern,maxdepth=1):
    cpath=path.count(os.sep)
    for r,d,f in os.walk(path):
        if r.count(os.sep) - cpath <maxdepth:
            for file_3dm in f:
                if file_3dm.endswith(pattern):
                    try:
                        #print "Removing %s" % (os.path.join(r,file_3dm))
                        os.remove(os.path.join(r,file_3dm))
                    except Exception as e:
                        print e
                    else:
                        print "%s removed" % file_3dm # (os.path.join(r,file_3dm))
                        
if __name__ == "__main__":
    path = os.path.join("c:/Rhino3dm")
    print 'finding and deleteng ".3dmbak" files inside: \n', path, 'directory ...'
    FindAndRemove(path, ".3dmbak", 5)
    FindAndRemove(path, ".rhl", 5)
    print 'All done!'

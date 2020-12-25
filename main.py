import re,sys,subprocess
#
# # read and generate original path file
def readpath2dict(filename):
    with open(filename, 'r') as file:
        c = file.read()
        lines=re.split('\r?\n',c)
        res={}
        minlengthdict={1:0}
        now=0
        for i in lines:
            i=i.strip()
            if i:
                if i and i.startswith('Node'):
                    now = int(i.split()[1])
                    res[now]={}
                else:
                    res[now][int(i.split()[0])]=int(i.split()[1])
                    minlengthdict[int(i.split()[0])]=float('inf')
        return res,minlengthdict

filename=sys.argv[1]

path,minLength=readpath2dict(filename)
#
# # copy path dict to newpath
# newpath=dict(path)
#
# for i in path:
#     for j in path[i]:
#         if j in newpath:
#             newpath[j][i]=path[i][j]
#         else:
#             newpath[j]={}
#             newpath[j][i] = path[i][j]
#
#
#
# nodes = dict(minLength)
#
# minFrom = {1:1}
# # when there is something in nodes
# while nodes:
#     # find the min
#     m = min(nodes,key=nodes.get)
#     # remove the min
#     nodes.pop(m,None)
#
#     for i in newpath[m]:
#         newLength = minLength[m]+newpath[m][i]
#
#         # core of D's
#         if newLength<minLength[i]:
#             minLength[i]=newLength
#             nodes[i]=newLength
#             minFrom[i]=m
#             if m==1:
#                 minFrom[i]=i
#
#
# # out put to file
# output=''
# for i in minLength:
#     output+="go to "+str(i)+", pass through "+str(minFrom[i])+", length is "+str(minLength[i])+'\n'
#
# with open('dijkstra.txt','w+') as file:
#     file.write(output)

#second
newpath=dict(path)
for i in path:
    for j in path[i]:
        if j in newpath:
            newpath[j][i]=path[i][j]
        else:
            newpath[j]={}
            newpath[j][i] = path[i][j]

popen=[]



for i in newpath:
    # create subprocess and add to list, wait for done
    popen.append(subprocess.Popen(('python','nns.py',str(i),filename)))

for i in popen:

    i.wait()

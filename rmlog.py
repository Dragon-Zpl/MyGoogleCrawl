import os
import time


path = r"D:\Users\Administrator\PycharmProjects\MyGoogleCrawl"



def removelog(path):
    nowtime = time.time()
    for filename in os.listdir(path):
        if os.path.isfile(filename):
            statinfo = os.stat(os.path.join(path,filename))
            create_time = statinfo.st_ctime
            if nowtime - create_time >= 259200:
                os.remove(os.path.join(path,filename))

if __name__ == '__main__':
    removelog(path)
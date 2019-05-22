import weibo_app.config as config
import os
from django.http import HttpResponse
import gzip
import zlib
import arrow
def getGzip(name,time):
    gzipDir = config.gzipDir
    if name=="gra_typhoon":
        path = gzipDir + name + "/" + time + "/"
    else:
        path = gzipDir + name + "/" + time[0:4] + "/" + time[4:6] + "/" + time[6:8] + "/"
    try:
        mkdir(path)
    except Exception as e:
        print("Execption:" + e)

    if os.path.exists(path + time + ".gz"):
        binfile = open(path + time + ".gz", 'rb')
        response = HttpResponse(binfile)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(time + ".json")
        response.__setitem__('Content-Encoding', "gzip")
        return response
    else:
        return None
def jsonToGzip(temp,name):
    gzipDir = config.gzipDir
    path = gzipDir + name+ "/"
    try:
        mkdir(path)
    except Exception as e:
        print("Execption:" + e)

    tmpstr = str(temp)
    by = str.encode(tmpstr)
    tempGlobal = gzip.compress(by)
    with open(path + name + ".gz", "wb") as file:
        file.write(tempGlobal)
        file.close()
    response = HttpResponse(tempGlobal)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(name + ".json")
    response.__setitem__('Content-Encoding', "gzip")
    return response
def mkdir(path):
    path = path.strip()
    path = path.rstrip("\\")
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        return True
    else:
        return False


def jsonToGzip_oil(temp):
    tmpstr = str(temp)
    by = str.encode(tmpstr)
    tempGlobal = gzip.compress(by)
    response = HttpResponse(tempGlobal)
    response['Content-Type'] = 'application/json'
    response.__setitem__('Content-Encoding', "gzip")

    return response
import platform

os = platform.system()
if os == "Windows":
    gzipDir = "D:/weibo_keys_data/json_data/"
    imgDir = "D:/weibo_keys_data/img_data/"
else:
    gzipDir = "/weibo_img_keys_data/json_data/"
    imgDir = "/weibo_keys_data/img_data/"
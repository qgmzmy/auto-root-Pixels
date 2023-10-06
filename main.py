import os
import re


# 获取最新的下载链接合集
print("正在获取Factory Image链接...")
os.system("curl -o link https://developers.google.cn/android/images?hl=en >nul 2>nul")

# 获取机型
productName = os.popen("adb shell getprop ro.product.name")
productName = productName.read().replace('''
''', "")

# 获取版本
buildId = os.popen("adb shell getprop ro.build.id")
buildId = buildId.read().replace('''
''', "").lower()

# 提取下载链接
downloadLink = "https://googledownloads.cn/dl/android/aosp/" + productName + "-" + buildId + "-factory-.+?\.zip"
with open("link", "r", encoding="utf-8") as link:
    linkList = link.read()
pattern = r"https://googledownloads.cn/dl/android/aosp/" + productName + "-" + buildId + "-factory-.+?\.zip"
matches = re.findall(pattern, linkList)

# 下载Factory Image
if matches:
    print("正在下载Factory Image...")
    # os.system("curl -o factoryImage.zip " + matches[0])
    sha256 = matches[0].split("-")[-1][:-4]

    sha256checksum = re.search(r'' + sha256 + "(.*?)<", linkList)
    print("正在校验Factory Image...")
    if sha256checksum:
        cert = os.popen("certutil -hashfile factoryImage.zip sha256")
        cert = cert.read()
        
        sha256checksum = sha256checksum.group(1)
        if sha256 + sha256checksum in cert:
            print("校验成功")
            print("正在解压Factory Image...")
            os.system("tar -xzvf factoryImage.zip >nul 2>nul")
            originDir = os.getcwd()
            os.chdir(productName + "-" + buildId)
            os.system("tar -xzvf image-" + productName + "-" + buildId + ".zip >nul 2>nul")

            # 判断是否为init_boot机型
            if os.path.exists("init_boot.img"):
                partition = "init_boot"
            elif os.path.exists("boot.img"):
                partition = "boot"
            else:
                print("文件丢失")

            # 获取root文件
            print("正在下载Root包...")
            os.system("curl -o magisk.zip https://qgmzmy.github.io/Files/patchboot/magisk.zip")
            os.system("tar -xzvf magisk.zip >nul 2>nul")

            # 推送root文件
            print("正在修补" + partition + "镜像...")
            os.system("adb push magisk /data/local/tmp/")
            os.system("adb push " + partition + ".img /data/local/tmp/magisk/")

            # 修补镜像
            os.system("adb shell chmod +x /data/local/tmp/magisk/*")
            os.system("adb shell /data/local/tmp/magisk/boot_patch.sh " + partition + ".img")

            # 获取修补后的镜像
            os.system("adb pull /data/local/tmp/magisk/new-boot.img")

            # 刷入镜像
            os.system("adb reboot bootloader")
            os.system("ping 127.0.0.1 >nul 2>nul")
            os.system("fastboot flash " + partition + " new-boot.img reboot")
        else:
            print("校验失败")
    else:
        print("校验失败")
else:
    print("未找到资源链接")
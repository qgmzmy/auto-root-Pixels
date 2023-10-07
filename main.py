import os
import re

os.system('title Auto Root Pixels 禁止用于商业用途')
print("######################################")
print("           Auto Root Pixels")
print("######################################")
print("                              qgmzmy")
print(" 禁止用于商业用途")
print(" 作者不对使用本软件造成的任何后果负责")
print()
print("按任意键开始...")
os.system("pause >nul 2>nul")


# 下载adb
print("正在更新adb...")
if os.path.exists("adb.exe"):
    os.remove("adb.exe")
elif os.path.exists("AdbWinApi.dll"):
    os.remove("AdbWinApi.dll")
elif os.path.exists("AdbWinUsbApi.dll"):
    os.remove("AdbWinUsbApi.dll")
elif os.path.exists("fastboot.exe"):
    os.remove("fastboot.exe")

os.system("curl -o adb.zip https://dl.google.com/android/repository/platform-tools_r34.0.4-windows.zip >nul 2>nul")
os.system("tar -xzvf adb.zip >nul 2>nul")
os.system("move .\platform-tools\\adb.exe .\\ >nul 2>nul")
os.system("move .\platform-tools\\fastboot.exe .\\ >nul 2>nul")
os.system("move .\platform-tools\\AdbWinUsbApi.dll .\\ >nul 2>nul")
os.system("move .\platform-tools\\AdbWinApi.dll .\\ >nul 2>nul")
os.remove("adb.zip")
os.system("rmdir platform-tools /s /q")


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


def checkImage():
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
            os.system("ping 127.0.0.1 >nul 2>nul")
            rm = input("刷入完毕，是否删除已下载的镜像[Y/n]: ")
            if rm == "y" or rm == "Y":
                os.remove(originDir + "\\factoryImage.zip")
            os.remove(originDir + "\link")
            os.system("rmdir " + originDir + "\\" + productName + "-" + buildId + "/s /q")
            os.system("pause")
        else:
            rm = input("校验失败，是否删除已下载的镜像[Y/n]: ")
            if rm == "y" or rm == "Y":
                os.remove("factoryImage.zip")
            os.remove("link")
            os.system("pause")
    else:
        print("校验失败")


# 判断factoryImage.zip是否存在
if os.path.exists("factoryImage.zip"):
    checkImage()
else:
    # 下载Factory Image
    if matches:
        print("正在下载Factory Image...")
        os.system("curl -o factoryImage.zip " + matches[0])
        checkImage
    else:
        print("未找到资源链接")
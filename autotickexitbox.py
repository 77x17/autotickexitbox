import cv2
import time
import subprocess
from PIL import Image
  
run     = True
N_EXIT  = 7
N_ARROW = 2


def run_command(command):
    subprocess.run(command, shell=True, text=True)


def take_screenshot(width = 1080, height = 1920):
    # windows
    # run_command("adb shell screencap /sdcard/Pictures/screenshot.raw && adb pull /sdcard/Pictures/screenshot.raw")
    
    # termux
    run_command("adb shell screencap /sdcard/Pictures/screenshot.raw && adb pull /sdcard/Pictures/screenshot.raw > /dev/null 2>&1")
    
    bytespp = 4

    with open('screenshot.raw', 'rb') as file:
        raw_data = file.read(width * height * bytespp)

    img_bytes = bytearray(raw_data)

    img = Image.frombytes('RGBA', (width, height), bytes(img_bytes), 'raw')

    img.save('screenshot.png', 'PNG')


def findLocation(input_png, click = True):
    img_rgb  = cv2.imread('screenshot.png')
    template = cv2.imread(input_png)

    img_rgb  = cv2.resize(img_rgb, (0, 0), fx=0.5, fy=0.5)
    template = cv2.resize(template, (0, 0), fx=0.5, fy=0.5)

    res       = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
    threshold = .75
    
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
 
    if max_val >= threshold:
        x, y = max_loc

        if click:            
            run_command(f"adb shell input tap {2 * x + template.shape[0]} {2 * y + template.shape[1]}")
            #print(2 * x + template.shape[0], 2 * y + template.shape[1])
            
        return True

    return False


def efast_efree(start_time):
    take_screenshot()

    #print("go")
    if findLocation("go.png"):
        take_screenshot()

        start_time[0] = time.time()

    #print("ok")
    if findLocation("ok.png", False):
        if findLocation("limit.png"):
            global run
            run = False

        findLocation("ok.png")

        start_time[0] = time.time()
        
        return

    #print("equation")
    while findLocation("equation.png", False):
        ans = 0

        find = False
        for i in range(0, 5):
            if findLocation(f"numleft_{i}.png", False):
                ans += i
                find = True
                break

        if not find:
            ans = 9
        else:
            for i in range(0, 5):
                if findLocation(f"numright_{i}.png", False):
                    ans += i
                    find = True
                    break

            if not find:
                ans = 9

        findLocation("ansbox.png")

        run_command(f"adb shell input text {ans}")

        run_command("adb shell input keyevent 4")

        findLocation("equation.png")

        take_screenshot()

        start_time[0] = time.time()

    #print("------------------------------------\nads")
    
    if findLocation("googleplay.png", False):
        run_command("adb shell input keyevent 4")
        
        take_screenshot()

    if findLocation("googleplay_1.png", False):
        run_command("adb shell input keyevent 4")
        run_command("adb shell input keyevent 4")

        take_screenshot()
        
    click = False

    for i in range(1, N_ARROW + 1):
        if findLocation(f"arrow_{i}.png"):
            take_screenshot()
            click = True

    for i in range(1, N_EXIT + 1):
        if findLocation(f"exit_{i}.png"):
            take_screenshot()
            click = True

    if click:
        return

    take_screenshot(1920, 1080)

    for i in range(1, N_ARROW + 1):
        if findLocation(f"arrow_{i}.png"):
            take_screenshot()

    for i in range(1, N_EXIT + 1):
        if findLocation(f"exit_{i}.png"):
            take_screenshot(1920, 1080)

    if (time.time() - start_time[0]) > 240:
        start_time[0] = time.time()
        run_command("adb shell am force-stop com.efast.efree")
        run_command("adb shell monkey -p com.efast.efree -c android.intent.category.LAUNCHER 1")


if __name__ == '__main__':
    take_screenshot()

    cnt = 0
    while True:
        print("Begin at: {}".format(time.strftime("%H:%M:%S", time.localtime())))
        
        run = True
        run_command("adb shell monkey -p com.efast.efree -c android.intent.category.LAUNCHER 1")

        start_time = [time.time()]
        while run:
            efast_efree(start_time)

        run_command("adb shell am force-stop com.efast.efree")
        
        run_command("adb shell am start -n com.termux/.app.TermuxActivity")
        
        cnt = cnt + 1
        print("------------------------")
        print("Running count =", cnt)
        print("At this moment: {}".format(time.strftime("%H:%M:%S", time.localtime())))
        print("Sleep time.........")
        print("------------------------")
        time.sleep(600)
        run_command("adb shell input tap 0 0")
        time.sleep(600)
        run_command("adb shell input tap 0 0")
        time.sleep(600)
        run_command("adb shell input tap 0 0")  
        time.sleep(600)
        run_command("adb shell input tap 0 0")
        time.sleep(600) 
        run_command("adb shell input tap 0 0")
        time.sleep(600)
        run_command("adb shell input tap 0 0")
        

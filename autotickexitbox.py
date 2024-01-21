import cv2
import time
import subprocess
import xml.etree.ElementTree as ET
from PIL import Image
  
N_EXIT = 7

run    = True


def run_command(command):
    subprocess.run(command, shell=True, text=True)
    # try:
    #     result = subprocess.check_output(command, shell=True, text=True)
    #     print(result)
    # except subprocess.CalledProcessError as e:
    #     print(f"Error executing command: {e}")


def check_resource_id_in_xml(resource_id_to_check, app, clickable = "true"):
    xml_file = 'window_dump.xml'

    tree = ET.parse(xml_file)
    root = tree.getroot()

    def check_resource_id_exists(element, resource_id):
        return resource_id in element.attrib.get('resource-id', '') and element.attrib['package'] == app and element.attrib['clickable'] == clickable 

    resource_id_found = any(check_resource_id_exists(element, resource_id_to_check) for element in root.iter())

    if resource_id_found:
        #print(f"Resource ID '{resource_id_to_check}' found in the XML.")
        return True
    else:
        #print(f"Resource ID '{resource_id_to_check}' not found in the XML.")
        return False


def check_text_in_xml(text_to_check, app, clickable = "true"):
    xml_file = 'window_dump.xml'

    tree = ET.parse(xml_file)
    root = tree.getroot()

    def check_resource_id_exists(element, text):
        return text in element.attrib.get('text', '') and element.attrib['package'] == app and element.attrib['clickable'] == clickable

    text_found = any(check_resource_id_exists(element, text_to_check) for element in root.iter())

    if text_found:
        #print(f"Text '{text_to_check}' found in the XML.")
        return True
    else:
        #print(f"Text '{text_to_check}' not found in the XML.")
        return False


def get_bounds_for_resource_id(resource_id):
    xml_file = 'window_dump.xml'

    tree = ET.parse(xml_file)
    root = tree.getroot()

    def get_bounds(element):
        values = [int(value) if value.isdigit() else 0 for value in element.attrib.get('bounds', '').replace('][', ',').strip('[]').split(',')]
        return (values[0] + values[2]) / 2, (values[1] + values[3]) / 2

    for element in root.iter():
        if 'resource-id' in element.attrib and element.attrib['resource-id'] == resource_id:
            return get_bounds(element)

    return None


def get_bounds_for_text(text):
    xml_file = 'window_dump.xml'

    tree = ET.parse(xml_file)
    root = tree.getroot()

    def get_bounds(element):
        values = [int(value) if value.isdigit() else 0 for value in element.attrib.get('bounds', '').replace('][', ',').strip('[]').split(',')]
        return (values[0] + values[2]) / 2, (values[1] + values[3]) / 2

    for element in root.iter():
        if 'text' in element.attrib and element.attrib['text'] == text:
            return get_bounds(element)

    return None


def get_answer_plus():
    xml_file = 'window_dump.xml'

    tree = ET.parse(xml_file)
    root = tree.getroot()

    def get_text(element):
        values = [int(value) if value.isdigit() else 0 for value in element.attrib.get('text', '').replace(' ', '').split('+')]
        return values[0] + values[1]

    for element in root.iter():
        if 'resource-id' in element.attrib and element.attrib['resource-id'] == "com.efast.efree:id/tvMath":
            return get_text(element)

    return None


def take_screenshot(width = 1080, height = 1920):
    run_command("adb shell screencap /sdcard/Pictures/screenshot.raw && adb pull /sdcard/Pictures/screenshot.raw")
    
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
    threshold = .8
    
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
 
    if max_val >= threshold:
        x, y = max_loc

        if click:            
            run_command(f"adb shell input tap {2 * x + template.shape[0]} {2 * y + template.shape[1]}")
            #print(2 * x + template.shape[0], 2 * y + template.shape[1])
            
        return True

    return False


def efast_efree():
    time.sleep(1)
    take_screenshot()

    #print("go")
    if findLocation("go.png"):
        take_screenshot()

    #print("ok")
    if findLocation("ok.png", False):
        run_command("adb shell uiautomator dump && adb pull /sdcard/window_dump.xml")

        if check_text_in_xml("Oops, you've exceeded the limit", "com.efast.efree", "false"):
            global run 
            run = False
            
        findLocation("ok.png")
        
        take_screenshot()

        return

    #print("equation")
    if findLocation("equation.png", False):
        run_command("adb shell input keyevent 3")
        run_command("adb shell monkey -p com.efast.efree -c android.intent.category.LAUNCHER 1")
        
        run_command("adb shell uiautomator dump && adb pull /sdcard/window_dump.xml")
        
        if check_resource_id_in_xml("com.efast.efree:id/ivCheckUser", "com.efast.efree"):
            x, y = get_bounds_for_resource_id("com.efast.efree:id/etResultUser")
            run_command(f"adb shell input tap {x} {y}")

            run_command(f"adb shell input text {get_answer_plus()}")
            
            run_command("adb shell input keyevent 4")
            run_command("adb shell input keyevent 4")

            x, y = get_bounds_for_resource_id("com.efast.efree:id/ivCheckUser")
            run_command(f"adb shell input tap {x} {y}")
        
        take_screenshot()

    #print("------------------------------------\nads")
    #print(0)
    if findLocation("arrow.png"):
        time.sleep(1)
        take_screenshot()

    for i in range(1, N_EXIT + 1):
        #print(i)
        if findLocation(f"exit_{i}.png"):
            time.sleep(1)
            take_screenshot()

    take_screenshot(1920, 1080)

    #print("rotate")
    #print(0)
    if findLocation("arrow.png"):
        time.sleep(1)
        take_screenshot()

    for i in range(1, N_EXIT + 1):
        #print(i)
        if findLocation(f"exit_{i}.png"):
            time.sleep(1)
            take_screenshot(1920, 1080)


if __name__ == '__main__':
    # take_screenshot()
    cnt = 0
    while True:
        run = True
        run_command("adb shell monkey -p com.efast.efree -c android.intent.category.LAUNCHER 1")

        while run:
            efast_efree()

        run_command("adb shell am force-stop com.efast.efree")
        
        run_command("adb shell am start -n com.termux/.app.TermuxActivity")
        
        cnt = cnt + 1
        print("------------------------")
        print("Running count =", cnt)
        print("Sleep time.........")
        print("------------------------")
        time.sleep(3600)
import subprocess
import time
import xml.etree.ElementTree as ET


BFAST_DELAY_TIME = 35
EFAST_DELAY_TIME = 50
ADS_DELAY        = 2    


run = True


def run_command(command):
    try:
        result = subprocess.check_output(command, shell=True, text=True)
        print(result)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")


def check_resource_id_in_xml(resource_id_to_check, app, clickable = "true"):
    # Specify the XML file
    xml_file = 'window_dump.xml'

    # Parse the XML file 
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Define a function to check if the resource-id exists
    def check_resource_id_exists(element, resource_id):
        return resource_id in element.attrib.get('resource-id', '') and element.attrib['package'] == app and element.attrib['clickable'] == clickable 

    # Check if the resource-id exists in any element of the XML
    resource_id_found = any(check_resource_id_exists(element, resource_id_to_check) for element in root.iter())

    # Output the result
    if resource_id_found:
        print(f"Resource ID '{resource_id_to_check}' found in the XML.")
        return True
    else:
        print(f"Resource ID '{resource_id_to_check}' not found in the XML.")
        return False


def check_text_in_xml(text_to_check, app, clickable = "true"):
    # Specify the XML file
    xml_file = 'window_dump.xml'

    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Define a function to check if the resource-id exists
    def check_resource_id_exists(element, text):
        return text in element.attrib.get('text', '') and element.attrib['package'] == app and element.attrib['clickable'] == clickable

    # Check if the resource-id exists in any element of the XML
    text_found = any(check_resource_id_exists(element, text_to_check) for element in root.iter())

    # Output the result
    if text_found:
        print(f"Text '{text_to_check}' found in the XML.")
        return True
    else:
        print(f"Text '{text_to_check}' not found in the XML.")
        return False


def get_bounds_for_resource_id(resource_id):
    xml_file = 'window_dump.xml'

    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Define a function to get bounds for a resource-id
    def get_bounds(element):
        values = [int(value) if value.isdigit() else 0 for value in element.attrib.get('bounds', '').replace('][', ',').strip('[]').split(',')]
        return (values[0] + values[2]) / 2, (values[1] + values[3]) / 2

    # Iterate through elements to find the specified resource-id
    for element in root.iter():
        if 'resource-id' in element.attrib and element.attrib['resource-id'] == resource_id:
            return get_bounds(element)

    # Return None if the resource-id is not found
    return None


def get_bounds_for_text(text):
    xml_file = 'window_dump.xml'

    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Define a function to get bounds for a text
    def get_bounds(element):
        values = [int(value) if value.isdigit() else 0 for value in element.attrib.get('bounds', '').replace('][', ',').strip('[]').split(',')]
        print((values[0] + values[2]) / 2, (values[1] + values[3]) / 2)
        return (values[0] + values[2]) / 2, (values[1] + values[3]) / 2

    # Iterate through elements to find the specified text
    for element in root.iter():
        if 'text' in element.attrib and element.attrib['text'] == text:
            return get_bounds(element)

    # Return None if the text is not found
    return None


def find_exit_bounds(app):
    xml_file = 'window_dump.xml'

    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Define a function to get bounds for a resource-id
    def get_bounds(element):
        values = [int(value) if value.isdigit() else 0 for value in element.attrib.get('bounds', '').replace('][', ',').strip('[]').split(',')]
        return (values[0] + values[2]) / 2, (values[1] + values[3]) / 2

    ans_x = 0
    ans_y = 0

    # Iterate through elements to find the specified resource-id
    for element in root.iter():
        if 'resource-id' in element.attrib and element.attrib['package'] == app and element.attrib['clickable'] == "true":
            x, y = get_bounds(element)
            if abs(x - 939) + abs(y - 126) < abs(ans_x - 939) + abs(ans_y - 126):
                ans_x = x
                ans_y = y

    if abs(ans_x - 939) + abs(ans_y - 126) > 293:
        return 0, 0
    
    return ans_x, ans_y


def get_answer_plus():
    xml_file = 'window_dump.xml'

    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Define a function to get bounds for a resource-id
    def get_text(element):
        values = [int(value) if value.isdigit() else 0 for value in element.attrib.get('text', '').replace(' ', '').split('+')]
        return values[0] + values[1]

    # Iterate through elements to find the specified resource-id
    for element in root.iter():
        if 'resource-id' in element.attrib and element.attrib['resource-id'] == "com.efast.efree:id/tvMath":
            return get_text(element)

    # Return None if the resource-id is not found
    print("Not found math question!!!")
    return None


def bfast_bfree(cnt, x_GO = 540, y_GO = 1192):
    run_command("adb shell uiautomator dump && adb pull /sdcard/window_dump.xml")
    
    if check_text_in_xml("Oops, you've exceeded the limit", "com.bfast.bfree", "false"):
        global run 
        run = False
    
    if check_text_in_xml("OK", "com.bfast.bfree"):
        x_OK, y_OK = get_bounds_for_text("OK")
        run_command(f"adb shell input tap {x_OK} {y_OK}")
        run_command(f"adb shell input tap {x_GO} {y_GO}")

    if check_text_in_xml("GO", "com.bfast.bfree") and get_bounds_for_text("GO") != None:
        x_GO, y_GO = get_bounds_for_text("GO")
        run_command(f"adb shell input tap {x_GO} {y_GO}")

        run_command("adb shell uiautomator dump && adb pull /sdcard/window_dump.xml")
        while check_text_in_xml("OK", "com.bfast.bfree"):
            x_OK, y_OK = get_bounds_for_text("OK")
            run_command(f"adb shell input tap {x_OK} {y_OK}")
            run_command(f"adb shell input tap {x_GO} {y_GO}")
            run_command("adb shell uiautomator dump && adb pull /sdcard/window_dump.xml")

        cnt = cnt + 1

        time.sleep(BFAST_DELAY_TIME)
    else:
        ads_resourses = [
            "cb-close-button",
            "al_skipButton",
            "al_closeButton",
            "com.bfast.bfree:id/ia_fl_close_button",
        ]
        
        for ads_resource in ads_resourses:
            if check_resource_id_in_xml(ads_resource, "com.bfast.bfree"):
                x, y = get_bounds_for_resource_id(ads_resource)
                run_command(f"adb shell input tap {x} {y}")

                time.sleep(ADS_DELAY)
                
                cnt = 0 

                return

        x, y = find_exit_bounds("com.bfast.bfree")
        print(f"ads tab at: {x}, {y}")
        if x != 0 and y != 0:
            run_command(f"adb shell input tap {x} {y}")
            
            cnt = 0

            time.sleep(ADS_DELAY)

    if cnt == 10:
        run = False


def efast_efree(cnt, x_GO = 540, y_GO = 1192):
    run_command("adb shell uiautomator dump && adb pull /sdcard/window_dump.xml")

    if check_text_in_xml("Oops, you've exceeded the limit", "com.efast.efree", "false"):
        global run 
        run = False
    
    if check_text_in_xml("OK", "com.efast.efree"):
        x_OK, y_OK = get_bounds_for_text("OK")
        run_command(f"adb shell input tap {x_OK} {y_OK}")
        run_command(f"adb shell input tap {x_GO} {y_GO}")

    if check_text_in_xml("GO", "com.efast.efree") and get_bounds_for_text("GO") != None:
        x_GO, y_GO = get_bounds_for_text("GO")
        run_command(f"adb shell input tap {x_GO} {y_GO}")

        run_command("adb shell uiautomator dump && adb pull /sdcard/window_dump.xml")
        if check_resource_id_in_xml("com.efast.efree:id/ivCheckUser", "com.efast.efree"):
            x, y = get_bounds_for_resource_id("com.efast.efree:id/etResultUser")
            run_command(f"adb shell input tap {x} {y}")

            run_command(f"adb shell input text {get_answer_plus()}")
            
            run_command("adb shell input keyevent 4")

            x, y = get_bounds_for_resource_id("com.efast.efree:id/ivCheckUser")
            run_command(f"adb shell input tap {x} {y}")
        
        while check_text_in_xml("OK", "com.efast.efree"):
            x_OK, y_OK = get_bounds_for_text("OK")
            run_command(f"adb shell input tap {x_OK} {y_OK}")
            run_command(f"adb shell input tap {x_GO} {y_GO}")
            run_command("adb shell uiautomator dump && adb pull /sdcard/window_dump.xml")

        cnt = cnt + 1

        time.sleep(EFAST_DELAY_TIME)
    else:
        ads_resourses = [
            "cb-close-button",
            "al_skipButton",
            "al_closeButton",
            "skipButton",
            "ecCloseBtn",
        ]

        for ads_resource in ads_resourses:
            if check_resource_id_in_xml(ads_resource, "com.efast.efree"):
                x, y = get_bounds_for_resource_id(ads_resource)
                print(x, y)
                run_command(f"adb shell input tap {x} {y}")

                cnt = 0

                time.sleep(ADS_DELAY)

                return
        
        x, y = find_exit_bounds("com.efast.efree")
        print(f"ads tab at: {x}, {y}")
        if x != 0 and y != 0:
            run_command(f"adb shell input tap {x} {y}")

            cnt = 0

            time.sleep(ADS_DELAY)
        
    if cnt == 10:
        run = False

if __name__ == '__main__':
    while True:
        cnt = 0
        run = True
        run_command("adb shell am force-stop com.efast.efree")
        run_command("adb shell monkey -p com.efast.efree -c android.intent.category.LAUNCHER 1")
        print(run)
        while run:
            efast_efree(cnt)
        
        time.sleep(5)

        cnt = 0
        run = True
        run_command("adb shell am force-stop com.bfast.bfree")
        run_command("adb shell monkey -p com.bfast.bfree -c android.intent.category.LAUNCHER 1")
        while run:
            bfast_bfree(cnt)
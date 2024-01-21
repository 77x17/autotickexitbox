import subprocess
import time
import xml.etree.ElementTree as ET
import cv2
import numpy as np

def run_command(command):
    try:
        subprocess.check_output(command, shell=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

# data:      "input"
# app:       "name"
# type:      "xml type"
# clickable: "true/false"
def check_type_in_xml(data, app, type, clickable = "true"):
    # Specify the XML file
    xml_file = 'window_dump.xml'

    # Parse the XML file 
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Define a function to check if the exists
    def check_exists(element, _data):
        return _data in element.attrib.get(type, '') and element.attrib['package'] == app and element.attrib['clickable'] == clickable 

    # Check if the resource-id exists in any element of the XML
    found = any(check_exists(element, data) for element in root.iter())

    # Output the result
    if found:
        print(f"{type} '{data}' found in the XML.")
        return True
    else:
        print(f"{type} '{data}' not found in the XML.")
        return False


def get_bounds(data, type):
    xml_file = 'window_dump.xml'

    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Define a function to get bounds for a text
    def get_bound(element):
        values = [int(value) if value.isdigit() else 0 for value in element.attrib.get('bounds', '').replace('][', ',').strip('[]').split(',')]
        print((values[0] + values[2]) / 2, (values[1] + values[3]) / 2)
        return (values[0] + values[2]) / 2, (values[1] + values[3]) / 2

    # Iterate through elements to find the specified text
    for element in root.iter():
        if type in element.attrib and element.attrib[type] == data:
            return get_bound(element)

    # Return None if the text is not found
    return None


def findLocation(gem_png):
    img_rgb  = cv2.imread('test.png')
    template = cv2.imread(gem_png)
    
    img_rgb  = cv2.resize(img_rgb, (0, 0), fx=0.5, fy=0.5)
    template = cv2.resize(template, (0, 0), fx=0.5, fy=0.5)


    res       = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
    threshold = .6
    loc       = np.where(res >= threshold)
    n         = len(loc[0])
    temp      = tuple(zip(*loc[::-1]))

    if n == 0:
        return

    x = (temp[0], temp[int(n/4) - 1], temp[int(2 * n/4) - 1], temp[int(3 * n/4) - 1])

    def calculate_distance(point1, point2):
        return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])

    distance_threshold = 50
    filtered_tuples = [x[i] for i in range(len(x) - 1) if calculate_distance(x[i], x[i + 1]) > distance_threshold]
    filtered_tuples.append(x[-1])

    for pt in filtered_tuples:
        run_command(f"adb shell input tap {pt[0] * 2} {pt[1] * 2}")
        print(pt[0] * 2, pt[1] * 2)

def convert_raw_to_png():
    width   = 1080
    height  = 1920
    bytespp = 4
    # Load the raw image
    with open('test.raw', 'rb') as file:
        # Read image data
        raw_data = file.read(width * height * bytespp)

    # Convert raw data to NumPy array
    img_np = np.frombuffer(raw_data, dtype=np.uint8).reshape((height, width, bytespp))

    # Adjust channel order if needed
    if bytespp == 4:
        # Assuming RGBA format, change to BGRA for OpenCV
        img_bgr = img_np[:, :, [2, 1, 0, 3]]
    else:
        # Assuming RGB format
        img_bgr = img_np[:, :, [2, 1, 0]]

    # Save the image as PNG
    cv2.imwrite('test.png', img_bgr)


if __name__ == '__main__':
    # run_command("adb shell input tap 0 0")
    # run_command("adb shell input tap 0 0")
    # run_command("adb shell input tap 0 0")

    while True:
    # while False:
        print("begin\n")

        run_command("adb shell screencap /sdcard/Pictures/test.raw && adb pull /sdcard/Pictures/test.raw")
        convert_raw_to_png()
        # run_command("adb shell input tap 168 834")
        # run_command("adb shell input tap 146 1282")
        # run_command("adb shell input tap 600 1282")
        # run_command("adb shell input tap 600 834")
        
        print("blue")
        findLocation("_blue.png")

        print("gold")
        findLocation("_gold.png")

        print("green")
        findLocation("_green.png")

        print("pink")
        findLocation("_pink.png")

        print("red")
        findLocation("_red.png")

        print("\nend")
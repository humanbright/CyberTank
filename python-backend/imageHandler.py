import cv2
import base64

# given a basic image in jpg or png, conver it to a numpy array (DO THIS FIRST)
def convertImageNp(image_path):
    # Load the image from the same directory
    image = cv2.imread(image_path)
    return image

# image parameter: numpy.ndarray
def convertImage64(image_numpy):
    retval, buffer = cv2.imencode('.jpg', image_numpy)
    image64_String = base64.b64encode(buffer).decode("utf-8")
    return image64_String


# DEBUG

original_path = "fork.png"
convertNumpy = convertImageNp(original_path)
image64 = convertImage64(convertNumpy)

print("Base64 String:", image64)

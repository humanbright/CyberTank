import cv2
import base64

def convertImageNp(image_path):
    image = cv2.imread(image_path)
    return image

def convertImage64(image_numpy):
    retval, buffer = cv2.imencode('.jpg', image_numpy)
    image64_String = base64.b64encode(buffer).decode("utf-8")
    return image64_String

def debug():
    original_path = "fork.png"
    convertNumpy = convertImageNp(original_path)
    image64 = convertImage64(convertNumpy)
    print("Base64 String:", image64)
    
    # Open camera
    cam = cv2.VideoCapture(0)  # Change to 0 if your camera is the first camera device
    
    if not cam.isOpened():
        print("Cannot open camera")
        exit()
    
    while True:
        # Capture frame-by-frame
        ret, frame = cam.read()
        
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        
        # Display the resulting frame
        cv2.imshow('frame', frame)
        
        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) == ord('q'):
            break

    # When everything done, release the capture
    cam.release()
    cv2.destroyAllWindows()

# debug()
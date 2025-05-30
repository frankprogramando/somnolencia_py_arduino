import cv2
import numpy as np
import mss

with mss.mss() as sct:
    # Define una región específica donde se muestre el video
    monitor = {"top": 100, "left": 100, "width": 640, "height": 480}
    while True:
        img = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        cv2.imshow("Camara", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cv2.destroyAllWindows()

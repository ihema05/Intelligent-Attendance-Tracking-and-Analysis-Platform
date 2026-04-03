# test_camera.py 
# — quick OpenCV camera test
import cv2, time

def test(index=0, frames=100):
    print(f"[TEST] Opening camera index {index} ...")
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # use DirectShow on Windows
    if not cap.isOpened():
        print(f"[ERROR] Camera index {index} could not be opened.")
        return False
    print("[TEST] Camera opened. Capturing frames...")
    i = 0
    while i < frames:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] frame read failed at frame", i)
            break
        cv2.imshow("Camera Test - press q to quit", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        i += 1
    cap.release()
    cv2.destroyAllWindows()
    print("[TEST] Done. Camera appears to work.")
    return True

if __name__ == "__main__":
    # try indexes 0..2 automatically if 0 fails
    import sys
    ok = test(0)
    if not ok:
        for idx in (1,2):
            print(f"[TEST] Trying camera index {idx} ...")
            if test(idx):
                break
    sys.exit(0)

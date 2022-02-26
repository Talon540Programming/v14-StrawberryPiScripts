#ifconfig: get ipv4 address
#run using flask run -h (ipv4 address) -p 5802

from flask import Flask, render_template, Response
import numpy as np
import cv2

from netifaces import interfaces, ifaddresses, AF_INET
for ifaceName in interfaces():
    addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
    if(' '.join(addresses) != 'No IP addr' ):
        if not(' '.join(addresses).startswith("127.")):
            local_ip = ' '.join(addresses)

app = Flask(__name__)
camera = cv2.VideoCapture(0)  # use 0 for web camera #'cams' for all connects cams

def raw_gen():  # Raw Video Feed
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def blue_gen():  # Blue Video Feed
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:

            b, g, r = cv2.split(frame)
            zeros_ch = np.zeros(frame.shape[0:2], dtype="uint8")
            frame = cv2.merge([b, zeros_ch, zeros_ch])

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def red_gen():  # Red Video Feed
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:

            b, g, r = cv2.split(frame)
            zeros_ch = np.zeros(frame.shape[0:2], dtype="uint8")
            frame = cv2.merge([zeros_ch, zeros_ch, r])


            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/test_feed')
def test_screen():
    return("hello world")


@app.route('/raw_feed')
def raw_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(raw_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/masks/blue')
def blue_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(blue_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/masks/red')
def red_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(red_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/') #Base root
def index():
    """Video streaming home page."""
    return render_template('root.html')


if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host=local_ip, debug=True,port="5800",use_reloader=False)
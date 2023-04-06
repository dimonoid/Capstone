# import necessary libs
import uvicorn, cv2
from vidgear.gears.asyncio import WebGear_RTC

# create your own custom streaming class
class Custom_Stream_Class:
    """
    Custom Streaming using OpenCV
    """

    def __init__(self, source=0):

        # !!! define your own video source here !!!
        self.source = cv2.VideoCapture(source)

        # define running flag
        self.running = True

    def read(self):

        # don't forget this function!!!

        # check if source was initialized or not
        if self.source is None:
            return None
        # check if we're still running
        if self.running:
            # read frame from provided source
            (grabbed, frame) = self.source.read()
            # check if frame is available
            if grabbed:

                # do something with your OpenCV frame here

                # lets convert frame to gray for this example
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # return our gray frame
                return gray
            else:
                # signal we're not running now
                self.running = False
        # return None-type
        return None

    def stop(self):

        # don't forget this function!!!

        # flag that we're not running
        self.running = False
        # close stream
        if not self.source is None:
            self.source.release()

# assign your Custom Streaming Class with adequate source (for e.g. foo.mp4)
# to `custom_stream` attribute in options parameter
options = {"custom_stream": Custom_Stream_Class(source="foo.mp4")}

# initialize WebGear_RTC app without any source
web = WebGear_RTC(logging=True, **options)

# run this app on Uvicorn server at address http://localhost:8000/
uvicorn.run(web(), host="localhost", port=8000)

# close app safely
web.shutdown()
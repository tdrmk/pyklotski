import cv2
import pygame

# Refer to https://github.com/tdrmk/pygame_recorder for more details
class ScreenRecorder:
    def __init__(self, width, height, fps, out_file = 'output.avi'):
        # define the codec and create a video writer object
        four_cc = cv2.VideoWriter_fourcc(*'XVID')
        self.video = cv2.VideoWriter(out_file, four_cc, float(fps), (width, height))

    def capture_frame(self, surf):
        pixels = cv2.rotate(pygame.surfarray.pixels3d(surf), cv2.ROTATE_90_CLOCKWISE)
        pixels = cv2.flip(pixels, 1)
        pixels = cv2.cvtColor(pixels, cv2.COLOR_RGB2BGR)
        self.video.write(pixels)

    def stop(self):
        self.video.release()
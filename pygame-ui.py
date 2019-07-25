#
# deepstream-UI
# Max_Dauber@Dell.com

import os
import sys
import time
import glob
import pygame
import random
import subprocess

#Buttons = ['vid0', 'vid1', 'vid2', 'mem', 'paint']
Buttons = ['vid0', 'vid1', 'vid2', 'paint']
Button_size = 75
WindowName = 'genz-demo-ctrl'

Proc = None
Vlist = []


#p = os.popen('hostname')
#Hostname = p.readlines()[0].strip()

os.environ['SDL_VIDEO_WINDOW_POS'] = "200,0"
os.environ['SDL_AUDIODRIVER'] = "dummy"

pygame.init()
#clock = pygame.time.Clock()
fps = 60
Wborder_size = 0.4      # %40

Wbrdr = int(Button_size * Wborder_size)
Size = [Button_size * len(Buttons) + Wbrdr * 2,  Button_size + Wbrdr * 2]

pygame.display.set_caption(WindowName)
screen = pygame.display.set_mode(Size, pygame.NOFRAME)
# /usr/share/fonts/truetype/...
#button_font = pygame.font.Font('gzfont.ttf', 18)

#wminfo = pygame.display.get_wm_info()['window']
#print(wminfo)
#print(pygame.display.list_modes())


Devnull = open(os.devnull, 'w')

def switch_running_process(cmd):
    global Proc
    print('new cmd:', cmd)
    if Proc != None:
        Proc.kill()
    Proc = subprocess.Popen(cmd.split(),
                            #stdout=subprocess.PIPE,
                            stdout=Devnull,
                            shell=False,
                            preexec_fn=os.setsid)

class Button:
    hover = False
    active = False

    def __init__(self, text, pos):
        self.text = text
        self.x = pos[0]
        self.y = pos[1]
        self.set_txtrect()
        self.draw()

    def draw(self):
        self.set_rend()
        screen.blit(self.rend, self.txtrect)

    def set_rend(self):
        self.rend = button_font.render(self.text, True, self.get_color())

    def get_color(self):
        if self.hover or self.active:
            return (255, 255, 255)
        return (128, 128, 128)

    def _redraw(self):
        # border
        b1 = 0.06 * Button_size
        b2 = b1 + 2
        self.btnrect = pygame.draw.rect(screen, (200, 200, 200),
                                [Wbrdr + self.x + b1, Wbrdr + self.y + b1,
                                        Button_size - b1*2, Button_size - b1*2])
        pygame.draw.rect(screen, (  0,   0,   0),
                                [Wbrdr + self.x + b2, Wbrdr + self.y + b2,
                                        Button_size - b2*2, Button_size - b2*2])
        self.draw()

    def set_txtrect(self):
        self.set_rend()
        self.txtrect = self.rend.get_rect()
        self.txtrect.center = (Button_size/2 + Wbrdr + self.x, Button_size/2 + Wbrdr + self.y)
        self._redraw()

    def activate(self):
        global Vlist
        self.active = False

        if self.text.startswith('vid'):
            idx = self.text[-1:]
            if len(Vlist) == 0:
                Vlist = glob.glob('/mnt/gz' + idx + '/videos/*')
                random.shuffle(Vlist)
                # why not use a script?  because shells don't kill easily.
                # we get far better control over running processes when fewer
                # processes are in between us and the program.
            cmd = 'mplayer -fs -quiet -nosound ' + Vlist[0]
            Vlist.pop(0)
            self.active = True

        elif self.text == 'mem':
            #cwd : BASE_PATH + '/memory-game',
            #path: 'node_modules/electron/dist/electron',
            #args : [ '.', '--pid=0', '--numproc=2', '--fullscreen', '--initialize', '--file=/dev/gzc0_0_1' ]
            cmd = 'echo ' + self.text
            self.active = True

        elif self.text == 'paint':
            dev = glob.glob('/dev/gzc*_1_*')[0]
            cmd = './whiteboard -w 128 -f -a 4 -b 8 ' + dev
            self.active = True

        else:
            print('unknown program [%s]' % self.text)
            cmd = 'echo ' + self.text

        switch_running_process(cmd)

    def deactivate(self):
        self.active = False
        # have to blank the button cause the font renderer is sloppy
        self._redraw()


x = 0
all_buttons = []
for bx in Buttons:
    all_buttons.append(Button(bx, (x, 0)))
    x += Button_size

#screen.fill([0, 0, 0])

def main():
    global Proc
    # keep our window on top of all others
    os.system('wmctrl -r ' + WindowName + ' -b add,above')

    current_bx = None
    while True:
        time.sleep(0.1)

        # if the current process finished, reactivate the last button
        if Proc != None:
            if Proc.poll() != None:
                Proc = None
                if current_bx != None:
                    current_bx.activate()

        for event in pygame.event.get():

            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                for bx in all_buttons:
                    if bx.btnrect.collidepoint(mouse_pos):
                        bx.hover = True
                    else:
                        bx.hover = False
                    bx.draw()
                continue

            #if event.type == pygame.QUIT:
            #    return

            # check for 'q' press
            if event.type == pygame.KEYDOWN  and  event.scancode == 24:
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for bx in all_buttons:
                    if bx.btnrect.collidepoint(mouse_pos):
                        print('b%d was pressed' % all_buttons.index(bx))
                        if current_bx != None:
                            current_bx.deactivate()
                            current_bx.draw()
                        bx.activate()
                        current_bx = bx
                        continue

                continue

            #print(event)

        pygame.display.update()
        #clock.tick(fps)

main()
pygame.quit()


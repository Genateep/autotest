import argparse
import csv
import glob
import os
import pyautogui as pag
import subprocess as s


from datetime import datetime
from pathlib import Path
from time import sleep

parser = argparse.ArgumentParser(description='kkrieger autotest')
parser.add_argument(
    'file',
    nargs='?',
    default='pno0001.exe',
    help='Path to file, default = current dir'
)
parser.add_argument(
    '-o',
    default=Path.cwd() / f'results_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}',
    help='Path to output, default = current dir'
)
args = parser.parse_args()

fraps_log_dir = 'C:/Fraps/Benchmarks'


def press_key(key: str, interval=0.0, times=0):
    for _ in range(times + 1):
        pag.keyDown(key)
        sleep(interval)
        pag.keyUp(key)
        sleep(0.1)


def click(interval=0, times=0):
    for _ in range(times + 1):
        pag.mouseDown(button='left')
        sleep(interval)
        pag.mouseUp(button='left')
        sleep(0.5)


def main():
    # checking output dir
    if not Path(args.o).exists():
        os.mkdir(args.o)
        print(f'{args.o} folder created')

    # launching process
    start_time = datetime.now()
    p = s.Popen([args.file, '-f'])
    print('Loading game')
    sleep(3)

    # waiting for game to load by checking background color
    while pag.pixelMatchesColor(300, 300, (0, 0, 0)):
        sleep(0.5)
    print(f'Game loaded in {datetime.now() - start_time}')

    # skipping intro and starting game
    press_key('enter', times=2)

    # making start_screenshot
    scr = pag.screenshot()
    scr.save(Path(args.o) / 'scr_start.png')

    # start collecting statistics
    press_key('f11')

    # shoot-n-move
    pag.moveRel(-3, 5, 1)
    click(times=3)
    press_key('w', interval=8)
    pag.moveRel(-1, 3, 1)
    click(times=1)
    press_key('s', interval=1)
    press_key('d', interval=2)
    press_key('w', interval=8)

    # stop collecting statistics
    press_key('f11')

    # making end_screenshot
    scr = pag.screenshot()
    scr.save(Path(args.o) / 'scr_end.png')

    # terminate process
    p.kill()
    print(f'Scenario finished in {datetime.now() - start_time}')

    # getting last benchmark file and creating new with average fps number
    list_of_files = glob.glob(fraps_log_dir + '/*.csv')
    latest_file = max(list_of_files, key=os.path.getctime).replace('\\', '/')
    fps_list = []

    with open(latest_file, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            fps_list.append(row[0])

    fps_list.pop(0)
    fps_average = round(sum([int(x) for x in fps_list]) / len(fps_list))

    with open(Path(args.o) / 'average_fps.txt', 'w') as file:
        file.write(str(fps_average))

    print('average_fps.txt created')


if __name__ == '__main__':
    main()

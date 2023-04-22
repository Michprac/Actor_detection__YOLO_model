import sensor, image, lcd, time
import KPU as kpu
import gc, sys

input_size = (224, 224)
labels = ['Tom_Cruise']
anchors = [6.7, 6.91, 5.22, 6.31, 2.64, 3.11, 6.03, 6.91, 4.22, 5.22]
clock = time.clock()

def lcd_show_except(e):
    import uio
    err_str = uio.StringIO()
    sys.print_exception(e, err_str)
    err_str = err_str.getvalue()
    img = image.Image(size=input_size)
    img.draw_string(0, 10, err_str, scale=1, color=(0xff,0x00,0x00))
    lcd.display(img)

def main(anchors, labels = None, model_addr="/sd/m.kmodel", sensor_window=input_size, lcd_rotation=0, sensor_hmirror=False, sensor_vflip=False):
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.set_windowing(sensor_window)
    sensor.set_hmirror(sensor_hmirror)
    sensor.set_vflip(sensor_vflip)
    sensor.run(1)

    i = 0;
    last_photos = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    lcd.init(type=1)
    lcd.rotation(lcd_rotation)
    lcd.clear(lcd.WHITE)

    if not labels:
        with open('labels.txt','r') as f:
            exec(f.read())
    if not labels:
        print("no labels.txt")
        img = image.Image(size=(320, 240))
        img.draw_string(90, 110, "no labels.txt", color=(255, 0, 0), scale=2)
        lcd.display(img)
        return 1

    try:
        img = image.Image("startup.jpg")
        lcd.display(img)
    except Exception:
        img = image.Image(size=(320, 240))
        img.draw_string(90, 110, "loading model...", color=(255, 255, 255), scale=2)
        lcd.display(img)

    try:
        task = None
        task = kpu.load(model_addr)
        kpu.init_yolo2(task, 0.5, 0.3, 5, anchors) # threshold:[0,1], nms_value: [0, 1]
        k = 0
        now = 0
        while(True):
            img = sensor.snapshot()
            clock.tick()
            objects = kpu.run_yolo2(task, img)
            t = clock.fps()

            if objects:
                k = k + 1
                if k > 400:
                    k = 0
                for obj in objects:
                    i = i % 20
                    last_photos[i] = obj.value()
                    avg_prob = sum(last_photos) / 20
                    pos = obj.rect()
                    img.draw_rectangle(pos)
                    if k % 20 == 0:
                        now = avg_prob
                    img.draw_string(pos[0], pos[1], "%s : %.2f" %(labels[obj.classid()], now), scale=2, color=(255, 0, 0))
                i = i + 1
            img.draw_string(0, 200, "FPS:%d" %(t), scale=2, color=(255, 0, 0))
            lcd.display(img)
    except Exception as e:
        raise e
    finally:
        if not task is None:
            kpu.deinit(task)


if __name__ == "__main__":
    try:
        # main(anchors = anchors, labels=labels, model_addr=0x300000, lcd_rotation=0)
        main(anchors = anchors, labels=labels, model_addr="/sd/model-20565.kmodel")
    except Exception as e:
        sys.print_exception(e)
        lcd_show_except(e)
    finally:
        gc.collect()

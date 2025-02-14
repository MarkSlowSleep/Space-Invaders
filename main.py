from machine import Pin, SoftI2C, Timer, PWM, ADC
import ssd1306, framebuf, SpaceShip, Alien, Attack
import time 

i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
width = 128 
height = 64  

buzzer = PWM(Pin(15))  
buzzer.freq(512)
buzzer.duty(0)

adc = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)
adc_value = adc.read()

display = ssd1306.SSD1306_I2C(width, height, i2c) 

score = 0  

btn1 = Pin(14, Pin.IN, Pin.PULL_UP)  
btn2 = Pin(12, Pin.IN, Pin.PULL_UP)  
btn3 = Pin(27, Pin.IN, Pin.PULL_UP)  


W = 55  
H = 45  

interface = 0  
state = 0  
ChangeInterface = Timer(0) 
Callbullet = Timer(1)
Bullet_active = 1  


pos_bullet_x = 0  
pos_bullet_y = 0  


bufer_Ship = SpaceShip.Ship  
bufer_Alien = Alien.Action1 
bufer_Bullet = Attack.Bullet 


Space = framebuf.FrameBuffer(bufer_Ship, 20, 23, framebuf.MONO_HLSB) 
AlienSprite = framebuf.FrameBuffer(bufer_Alien, 10, 6, framebuf.MONO_HLSB) 
AttackSprite = framebuf.FrameBuffer(bufer_Bullet, 10, 6, framebuf.MONO_HLSB) 

alien_rows = 2  
alien_columns = 2  
alien_start_x = 10
alien_start_y = 10
alien_spacing_x = 20  
alien_spacing_y = 15 

aliens = [[True for _ in range(alien_columns)] for _ in range(alien_rows)] 
alien_positions = [[(alien_start_x + c * alien_spacing_x, alien_start_y + r * alien_spacing_y)
                    for c in range(alien_columns)] for r in range(alien_rows)] 

alien_direction = 1  

bullet_timer = Timer(2)  


notes = {
    'c': 261,
    'd': 294,
    'e': 329,
    'f': 349,
    'g': 391,
    'gS': 415,
    'a': 440,
    'aS': 455,
    'b': 466,
    'cH': 523,
    'cSH': 554,
    'dH': 587,
    'dSH': 622,
    'eH': 659,
    'fH': 698,
    'fSH': 740,
    'gH': 784,
    'gSH': 830,
    'aH': 880
}

song_playing = False
i = 0  

def beep(note, duration):
    buzzer.freq(note)  
    buzzer.duty_u16(32768)  
    time.sleep(duration / 1000)  
    buzzer.duty_u16(0)  
    time.sleep(0.05)  

def first_section():
    beep(notes['a'], 500)
    beep(notes['a'], 500)
    beep(notes['a'], 500)
    beep(notes['f'], 350)
    beep(notes['cH'], 150)
    beep(notes['a'], 500)
    beep(notes['f'], 350)
    beep(notes['cH'], 150)
    beep(notes['a'], 650)

    time.sleep(0.5)

    beep(notes['eH'], 500)
    beep(notes['eH'], 500)
    beep(notes['eH'], 500)
    beep(notes['fH'], 350)
    beep(notes['cH'], 150)
    beep(notes['gS'], 500)
    beep(notes['f'], 350)
    beep(notes['cH'], 150)
    beep(notes['a'], 650)

    time.sleep(0.5)

def second_section():
    beep(notes['aH'], 500)
    beep(notes['a'], 300)
    beep(notes['a'], 150)
    beep(notes['aH'], 500)
    beep(notes['gSH'], 325)
    beep(notes['gH'], 175)
    beep(notes['fSH'], 125)
    beep(notes['fH'], 125)
    beep(notes['fSH'], 250)

    time.sleep(0.325)

    beep(notes['aS'], 250)
    beep(notes['dSH'], 500)
    beep(notes['dH'], 325)
    beep(notes['cSH'], 175)
    beep(notes['cH'], 125)
    beep(notes['b'], 125)
    beep(notes['cH'], 250)
    time.sleep(0.35)

def play_melody():
    global song_playing  
    if interface == 0:
        song_playing = True
        first_section()
        if interface != 0:  
            return

        second_section()
        if interface != 0:
            return

        beep(notes['f'], 250)
        beep(notes['gS'], 500)
        if interface != 0:
            return
        beep(notes['f'], 350)
        beep(notes['a'], 125)
        beep(notes['cH'], 500)
        beep(notes['a'], 375)
        beep(notes['cH'], 125)
        beep(notes['eH'], 650)

        if interface != 0:
            return

        second_section()

        beep(notes['f'], 250)
        beep(notes['gS'], 500)
        if interface != 0:
            return
        beep(notes['f'], 375)
        beep(notes['cH'], 125)
        beep(notes['a'], 500)
        beep(notes['f'], 375)
        beep(notes['cH'], 125)
        beep(notes['a'], 650)
    elif interface == 1:
        stop_melody()

        

def stop_melody():
    song_playing = False
    buzzer.duty_u16(0)  
def reset_aliens():
    global aliens, alien_positions

    aliens = [[True for _ in range(alien_columns)] for _ in range(alien_rows)] 
    alien_positions = [[(alien_start_x + c * alien_spacing_x, alien_start_y + r * alien_spacing_y)
                        for c in range(alien_columns)] for r in range(alien_rows)] 

def move_aliens():
    global alien_positions, alien_direction 
    move_down = False 

    pot_value = adc.read()  


    speed = max(1, min(20, pot_value // 200))  

    for r in range(alien_rows):
        for c in range(alien_columns):
            if aliens[r][c]: 
                x, y = alien_positions[r][c]  
                alien_positions[r][c] = (x + alien_direction * 2, y)


    leftmost = width  
    rightmost = 0     

    for r in range(alien_rows):
        for c in range(alien_columns):
            if aliens[r][c]:
                x, y = alien_positions[r][c]
                if x < leftmost:
                    leftmost = x  
                if x > rightmost:
                    rightmost = x  

    if leftmost <= 0 or rightmost >= width - 10:
        alien_direction *= -1  
        move_down = True  

    if move_down: 
        for r in range(alien_rows):
            for c in range(alien_columns):
                if aliens[r][c]:  
                    alien_x, alien_y = alien_positions[r][c]  
                    alien_positions[r][c] = (alien_x, alien_y + 5)  

    time.sleep(speed / 1000.0)  



def check_aliens_collision():
    global H
    for r in range(alien_rows):
        for c in range(alien_columns):
            if aliens[r][c]:  
                alien_x, alien_y = alien_positions[r][c]  
                if alien_y + 6 >= H:  
                    return True 
    return False  

def buzz(frequency, duration):
    global buzzer  
    buzzer.freq(frequency)  
    buzzer.duty(512)  
    time.sleep(duration)  
    buzzer.duty(0)  

def fire_sound():
    buzz(128, 0.1)  
    time.sleep(0.1)  
    


def aliendeath_sound():
    buzz(500, 0.2)  
    time.sleep(0.1)  

def bullet():
    global W, H, interface, pos_bullet_y, pos_bullet_x, Bullet_active, state  
    if btn3.value() == 0 and state == 1: 
        if interface == 1 and Bullet_active == 1:  
            pos_bullet_y = H + 10  
            pos_bullet_x = W + 6  
            Bullet_active = 0 
            bulletMove()  
            fire_sound() 



def bulletMove():
    global pos_bullet_y, pos_bullet_x, Bullet_active, interface, aliens, alien_positions, score

    if interface == 1 and Bullet_active == 0: 
        display.fill_rect(pos_bullet_x, pos_bullet_y, 10, 6, 0)  
        pos_bullet_y -= 5 

        hit_alien = False  

        for r in range(alien_rows):
            for c in range(alien_columns):
                if aliens[r][c]:  
                    alien_x, alien_y = alien_positions[r][c]  
                    if alien_x <= pos_bullet_x <= alien_x + 10 and alien_y <= pos_bullet_y <= alien_y + 6: 
                        aliens[r][c] = False  
                        Bullet_active = 1  
                        score += 1 
                        display.fill_rect(alien_x, alien_y, 10, 6, 0)  
                        aliendeath_sound()  
                        reset_bullet() 
                        hit_alien = True  

        if not hit_alien:
            display.text("*", pos_bullet_x, pos_bullet_y)  
            display.blit(Space, W, H)  
            display.show()  
        
        if pos_bullet_y < 0:  
            reset_bullet() 



def reset_bullet():
    global Bullet_active, pos_bullet_y, pos_bullet_x  
    Bullet_active = 1  
    pos_bullet_x = 0 
    pos_bullet_y = 0 

def check_aliens_status():
    return all(not status for row in aliens for status in row) 

def MoveLeft():
    global W, H, interface  
    if interface == 1: 
        if btn1.value() == 0:  
            display.fill(0) 
            if W > 0:  
                W -= 5  
            display.blit(Space, W, H)
            display.show()  

def MoveRight():
    global W, H, interface
    if interface == 1:  
        if btn2.value() == 0:  
            display.fill(0)  
            if W < (width - 20):  
                W += 5  
            display.blit(Space, W, H)  
            display.show()  

def Change_interface(timer):
    global interface, state, W, H, Bullet_active  
    if btn3.value() == 0:  
        if state == 1:  
            if interface == 0:  
                W = 55  
                H = 45  
                interface = 1  
                stop_melody()  
                reset_aliens()
                state = 0 
            elif interface == 1:  
                Bullet_active = 1  
                W = 55 
                H = 45  
                interface = 0  
                reset_aliens()
                state = 0 



def showPush(pin):  
    global W, state, interface  
    if btn1.value() == 0: 
        MoveLeft()  
    elif btn2.value() == 0:  
        MoveRight()  
    elif btn3.value() == 0:  
        if state == 0:  
            state += 1  
            ChangeInterface.init(period=1500, mode=Timer.ONE_SHOT, callback=Change_interface)  
    elif btn3.value() == 1:  
        state = 0  



btn1.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=showPush)
btn2.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=showPush)
btn3.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=showPush)



while True:
    if interface == 0:  
        display.fill(0)  
        display.text("START GAME", 20, 30) 
        display.show() 
        play_melody()  
            
    elif interface == 1:  
        display.fill(0) 
        MoveRight() 
        MoveLeft() 
        bullet()
        bulletMove() 
        move_aliens() 
        
        for r in range(alien_rows):
            for c in range(alien_columns):
                if aliens[r][c]:  
                    alien_x, alien_y = alien_positions[r][c]  
                    display.blit(AlienSprite, alien_x, alien_y)  

        display.blit(Space, W, H)  
        display.show() 

        if check_aliens_status():  
            display.fill(0)  
            display.text("YOU WIN!", 20, 20)  
            display.text("Score: " + str(score), 20, 40) 
            display.show()  
            time.sleep(2)  
            interface = 0  
            score = 0

        if check_aliens_collision(): 
            display.fill(0) 
            display.text("GAME OVER", 20, 20)  
            display.text("Score: " + str(score), 20, 40)  
            display.show()  
            time.sleep(2) 
            interface = 0  
            score = 0 
    adc_value = adc.read()
    print(str(interface))
    #print(str(btn3.value()))  





#!/usr/bin/env pybricks-micropython
#importerer biblioteker 
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
import time

#Globale variabler sættes 
driver_speed=180        #Hastighed på motor
angle_speed_turn=18     #Beskriver hvor skarpt den drejer altså forskel i hastighed på de to hjul

#Vi har målt reflektionsværdier for henholdsvis hvid, grå og sort
white_reflection=34     #En reflektionsværdi der ligger ca. i midten af intervallet mellem grå og hvid
black_reflection=4      #En reflektionsværdi der ligger lidt en smule over sort 

black_lines=1           #Denne variabel bruges til at tælle antallet af sorte linjer den har forbipasseret

#Antal grader der bruges i dreje funktionen "robot.turn" der hentes fra et bibliotek
turn_35_degrees=35      
turn_45_degrees=45

drive_step=20           #Længde den kører, som bruges i funktionen "blind_driving"         
black_width=25          #Længden af en sort streg, som bruges i funktionen "drive"
bottle_size=200         #Tykkelsen af flasken, som bruges i funktionen "first_grib"
t_cross=9000            #Tiden [ms] det tager at køre fra starten af vippen til den er nået gennem porten       
counter=0               #Bruges som tidstæller
finish=8000
#Initialisere robotten
ev3 = EV3Brick()

#Initialisere motorene
Venstre_motor = Motor(Port.A, positive_direction=Direction.CLOCKWISE)
Højre_motor = Motor(Port.B, positive_direction=Direction.CLOCKWISE)
Griber_moter = Motor(Port.C, positive_direction=Direction.COUNTERCLOCKWISE)

#Initialisere sensorene
linesensor = ColorSensor(Port.S1)

#Initialisere robottens "drivebase"
    #Her sættes hjulets diameter og afstand mellem hjulene så funktioner som robot.turn, som hentes fra biblioteket, matcher hvad den reelt gør.
robot = DriveBase(Venstre_motor, Højre_motor, wheel_diameter=70, axle_track=110)

#Funktion der lægger en til variablen "black_lines", som bruges i funktionen "drive"
def add_black_lines():
    global black_lines      #Sikre at den kan ændre i den globale værdi "black_lines" 
    black_lines+=1          #Den ligger 1 til variablen med oberatoren "+="

#Funktionen lægger en til variablen "counter"
def counter_is_ticking():
    global counter
    counter+=1

#Funktion der checker for sorte linjer og kalder funktionen "follow_line"
#Parametre: 
    #drive_until: beskriver hvilken sort linje på banen den skal køre til
    #tight_corner: bruges hvis angle_speed_turn ikke er nok til at holde robotten på stregen i et skarpt sving
def drive(drive_until,tight_corner):
    while black_lines <= drive_until:                   #Løkke der chekker om den er nået den sorte linje, som er beskrevet i parametren "drive_until"
        if linesensor.reflection() > black_reflection:  #If-statement, der chekker om robotten er over noget, der ikke er sort
                                                        #funktionen fra robt-biblioteket "linesensor.reflection()" returnere en reflektionværdi fra lyssensoren
            follow_line(tight_corner)                   #Hvis ja, kaldes(refererer) funktionen "follow_line" og vedlægger parametren tight_corner
        else:
            robot.stop()                                #Hvis nej, stopper robotten 
            add_black_lines()                           #og kalder funktionen "add_black_lines"
            robot.straight(black_width)                 #Den køre fremad svarende til bredden af en sort linje som er angivet i variablen "black_width"
            time.sleep(0.1)                             #Holder en kort pause på 0,1 sek

#Funktion der føljer en grå linje
def follow_line(tight_corner):
    if linesensor.reflection() < white_reflection :                     #If-statement, der chekker om robottens lyssensor returnerer en reflektionsværdi, som er under variablen "white_reflektion"
        robot.drive(driver_speed, -1*(angle_speed_turn + tight_corner)) #Hvis ja, kalder den "robot.drive()" som får robotten til at køre i en cirkelbue specifiseret at parametrene:
                                                                        #1. parameter: Speed
                                                                        #2. parameter: Turn radius                       
    else:
        robot.drive(driver_speed, angle_speed_turn + tight_corner)      #Hvis nej, sker det samme blot med negativ "angle_speed_turn"

#Funktion der griber den første flaske på banen, løfter den og settær den ned et nyt sted


#Funktion der kører fremad i steps indtil den møder en streg hvorefter den kører over stregen
def blind_driving(white_first): #Parameteren bestemmer om den først skal kører over en hvid overflade og derefter over en grå overflade eller omvendt
    if white_first == True:     
        #først hvid så grå
        while linesensor.reflection() > white_reflection :
            robot.straight(drive_step)
        while linesensor.reflection() < white_reflection :
            robot.straight(drive_step)
    else:                       
        #Først grå så hvid
        while linesensor.reflection() < white_reflection :
            robot.straight(drive_step)
        while linesensor.reflection() > white_reflection :
            robot.straight(drive_step)

#Funktion der kører fremad i steps indtil den møder en streg hvorefter den kører over stregen
def brudt_streg():
    drive(1,0)                      #Robotten kører til sort linje nr.1

    robot.turn(-turn_35_degrees)    #Robotten drejer til højre
    robot.straight(3*drive_step)    #Robotten kører lidt fremad
    blind_driving(True)             #Kører i steps til den dedekterer en grå streg og kører derefter i steps til den er kørt over den grå streg
    robot.straight(3*drive_step)    #Robotten kører lidt fremad
    robot.stop()                    #Robotten stopper
    robot.turn(turn_35_degrees)     #Drejer til venstre (retter op)

    drive(2,0)                      #Robotten kører til sort linje nr.2
    
    #Her sker det samme som blot spejlvendt
    robot.turn(turn_35_degrees)
    robot.straight(2*drive_step)
    blind_driving(True)
    robot.stop()
    robot.turn(-turn_35_degrees)

    drive(3,15)                     #Her kører den til linje 3 og sætter rotationshastigheden op da den skal rundt i et sving

#Funktion der placere sig korrekt, griber den første flaske på banen, løfter den og settær den ned et nyt sted
def flyt_flaske():
    robot.straight(3*drive_step)
    robot.stop()
    robot.turn(-turn_45_degrees)
    blind_driving(False)
    robot.turn(-turn_45_degrees-5)      #Den retter robotten  op så den har den rette kurs
    robot.stop()
    robot.settings(80)                  #Hastigheden nedsættes
    robot.straight(350)                 #Kører fremad
    #Her lukker gribearmen sig
    Griber_moter.run_time(-350,1400-bottle_size, then=Stop.HOLD, wait=True)
    robot.straight(200)
    #Her åbner gribearmen sig
    Griber_moter.run_time(350,1400-bottle_size, then=Stop.HOLD, wait=True)
    robot.straight(-350)                #Den bakker
    robot.turn(135)                     #og drejer
    robot.stop()
    robot.settings(180)                 #og hastigheden sættes tilbage til default
    blind_driving(True)                 #Den kører til den rammer en strej og kører derefter over stregen inden den standser
    robot.turn(-turn_45_degrees)        #Den retter op så den står parallelt med linjen

    drive(4,0)                          #Kører videre til næste (4.) sorte streg

#Funktion der kører over vippen og gennem næste port inden den drejer og finder stregen igen efter t-krydset
def vippe():
    robot.straight(170)  
    robot.turn(110)
    blind_driving(False)

    drive(5,0)
    #Her gentages funktionen "follow_line" indtil den er forbi t-krydset
    while counter < t_cross:            #Chekker om tælleren er mindre end variablen t-cross
        follow_line(0)              
        counter_is_ticking()            #Kalder funktionen "counter_is_ticking" der lægger 1 til variablen "counter"
    robot.turn(135)                     #Den drejer efter t-krydset
    blind_driving(True)                 #Kalder blind_driving 
    robot.straight(drive_step)          #Kører lidt ekstra
    robot.turn(-turn_45_degrees)        #og retter op

    drive(6,0)

#Funktion der kører over de parallelle streger og retter op ved den korrekte streg og kører rundt i svinget til den næste sorte streg
def parallelle_streger():
    robot.straight(100)
    robot.turn(turn_35_degrees)
    robot.straight(340)
    robot.turn(-turn_35_degrees)
    drive(8,10)

#Funktion der placerer en flaske i midten af målskiven
def placer_flaske():
    pass

#Funktion der kører i et V uden om en flaske der skal undviges
def undvig_flaske():
    robot.turn(-turn_35_degrees)
    robot.straight(450)
    robot.turn(2*turn_35_degrees)
    robot.straight(200)
    blind_driving(True)
    robot.straight(40)
    robot.turn(-45)
    robot.stop()
    robot.settings(80)
    drive(9,15)                     #Rotationshastigheden nedsættes i svinget
    robot.stop()
    robot.settings(180)

#Funktion der kører gennem væg-forhindringen
def undvig_væg():
    robot.turn(-20)
    robot.straight(400)
    robot.turn(68)
    robot.straight(260)
    robot.turn(-45)
    robot.straight(120)
    robot.turn(-45)
    robot.straight(600)
    robot.turn(90)
    blind_driving(True)
    robot.turn(-45)
    drive(10,0)

#Funktion der undviger flaske 2. gang
def undvig_flaske_2():
    robot.turn(turn_35_degrees)
    robot.straight(600)
    robot.turn(-90)
    robot.straight(200)
    blind_driving(True)
    robot.straight(40)
    robot.turn(70)
    drive(11,15)

#Funktion der kører langs målfeltet til den er halvvejs, og drejer en kvart omgang og kører lidt frem så spidsen af robotten er i midten af målfeltet
def mål():
    robot.turn(30)
    robot.straight(100)
    robot.turn(-30)
    global counter              
    counter = 0                 #Tæller sættes til 0 igen (resættes efter tidligere brug)
    while counter < finish:     #Chekker om counter er mindre end variablen "finish"
        follow_line(15)         #Kalder follow_line med øget rotationshastighed
        counter_is_ticking()    #Kalder funktionen "counter_is_ticking" der lægger 1 til variablen "counter"
    robot.turn(-90)             #Drejer en kvart omgang
    robot.straight(100)         #og kører lidt frem så spidsen af robotten er i midten af målfeltet

#Funktionen "main" kalder alle 9 funktioner der tilsammen fører robotten gennem banens deludfordringer
def main():
    brudt_streg()
    flyt_flaske()
    vippe()
    parallelle_streger()
    placer_flaske()
    undvig_flaske()
    undvig_væg()
    undvig_flaske_2()
    mål()

####  PROGRAM RUNNING
main()          



EESchema Schematic File Version 2
LIBS:power
LIBS:device
LIBS:transistors
LIBS:conn
LIBS:linear
LIBS:regul
LIBS:74xx
LIBS:cmos4000
LIBS:adc-dac
LIBS:memory
LIBS:xilinx
LIBS:microcontrollers
LIBS:dsp
LIBS:microchip
LIBS:analog_switches
LIBS:motorola
LIBS:texas
LIBS:intel
LIBS:audio
LIBS:interface
LIBS:digital-audio
LIBS:philips
LIBS:display
LIBS:cypress
LIBS:siliconi
LIBS:opto
LIBS:atmel
LIBS:contrib
LIBS:valves
LIBS:UV-LED-cache
EELAYER 25 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L LED D1
U 1 1 596FA117
P 2400 1800
F 0 "D1" H 2400 1900 50  0000 C CNN
F 1 "LED" H 2400 1700 50  0000 C CNN
F 2 "LEDUV:VLMU3500" H 2400 1800 50  0001 C CNN
F 3 "" H 2400 1800 50  0001 C CNN
	1    2400 1800
	0    -1   -1   0   
$EndComp
$Comp
L CONN_01X02 J1
U 1 1 596FA21F
P 1100 1650
F 0 "J1" H 1100 1800 50  0000 C CNN
F 1 "CONN_01X02" V 1200 1650 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Angled_1x02_Pitch2.54mm" H 1100 1650 50  0001 C CNN
F 3 "" H 1100 1650 50  0001 C CNN
	1    1100 1650
	0    1    1    0   
$EndComp
Wire Wire Line
	1050 1450 850  1450
Wire Wire Line
	850  1450 850  2450
$Comp
L D_Zener D2
U 1 1 598B4E49
P 2050 1550
F 0 "D2" H 2050 1650 50  0000 C CNN
F 1 "D_Zener" H 2050 1450 50  0000 C CNN
F 2 "Diodes_THT:D_A-405_P2.54mm_Vertical_KathodeUp" H 2050 1550 50  0001 C CNN
F 3 "" H 2050 1550 50  0001 C CNN
	1    2050 1550
	0    1    1    0   
$EndComp
$Comp
L D_Zener D3
U 1 1 598B4ED9
P 2050 2000
F 0 "D3" H 2050 2100 50  0000 C CNN
F 1 "D_Zener" H 2050 1900 50  0000 C CNN
F 2 "Diodes_THT:D_A-405_P2.54mm_Vertical_KathodeUp" H 2050 2000 50  0001 C CNN
F 3 "" H 2050 2000 50  0001 C CNN
	1    2050 2000
	0    -1   -1   0   
$EndComp
Wire Wire Line
	2050 1700 2050 1850
Wire Wire Line
	2050 1400 2400 1400
Wire Wire Line
	2400 1400 2400 1650
Wire Wire Line
	2400 1950 2400 2250
Wire Wire Line
	2400 2250 2050 2250
Wire Wire Line
	2050 2250 2050 2150
Wire Wire Line
	1150 1450 1700 1450
Wire Wire Line
	1700 1450 1700 1300
Wire Wire Line
	1700 1300 2250 1300
Wire Wire Line
	2250 1300 2250 1400
Connection ~ 2250 1400
Wire Wire Line
	850  2450 2250 2450
Wire Wire Line
	2250 2450 2250 2250
Connection ~ 2250 2250
$EndSCHEMATC

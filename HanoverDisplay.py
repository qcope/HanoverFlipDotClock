import numpy
import time
from datetime import datetime
import serial
import collections
from BitmapFont import BitmapFont

DISPLAY_COLS = 96
DISPLAY_ROWS = 16
BAUDRATE=4800
ROW_OFFSET_SMALL_FONT = 6
MAX_DISPLAY_ITERATIONS = 100

class HanoverDisplay:
    def __init__(self,port):
        self.display_binary=numpy.zeros((DISPLAY_ROWS,DISPLAY_COLS), dtype=bool) #Start with a blank display
        self.display_binary_old = None #Variable will hold the last displayed bitmap, when one has been set
        self.port=port
        self.font = BitmapFont()
        self.cursor_col = 0
        self.cursor_row = 0
        self.screen_updates_left = 0
        self.ser = None
        
    def __str__(self):
        display_string=""
        for row in range(DISPLAY_ROWS):
            for column in range(DISPLAY_COLS):  
                if self.display_binary[row,column]:
                    display_string = display_string + '*'
                else:
                    display_string = display_string + ' '
            display_string = display_string + '\n'
        return display_string

    def clear(self):
        if self.screen_updates_left <=0:
            self.invert()
            self.update_hanover()
            self.screen_updates_left = MAX_DISPLAY_ITERATIONS
        self.display_binary=numpy.zeros((DISPLAY_ROWS,DISPLAY_COLS), dtype=bool)
        self.cursor_col = 0
        self.cursor_row = 0


    def invert(self):
        for row in range(DISPLAY_ROWS):
            for col in range(DISPLAY_COLS):
                if self.display_binary[row][col]:
                    self.display_binary[row][col]=False
                else:
                    self.display_binary[row][col]=True

    def set_cursor(self,col,row):
        self.cursor_col = col
        self.cursor_row = row

    def set_dot(self,col,row):
        if col < 0 or row < 0 or col >= DISPLAY_COLS or row >= DISPLAY_ROWS:
            return
        self.display_binary[row][col]=True

    def unset_dot(self,col,row):
        if col < 0 or row < 0 or col >= DISPLAY_COLS or row >= DISPLAY_ROWS:
            return
        self.display_binary[row][col]=False

    def write_character(self, character):
        # iterate over font... at the right column
        display_column=self.cursor_col
        for dot_column in range(self.font.get_character_width()):
            column_data = self.font.get_columnn_for_character(character,dot_column)
            for dot_row in range(self.font.get_character_height()):
                if column_data & 0x1:
                    self.set_dot(display_column+dot_column, dot_row + self.cursor_row)
                else:
                    self.unset_dot(display_column+dot_column, dot_row + self.cursor_row)
                column_data = column_data >> 1
        self.cursor_col = self.cursor_col + self.font.get_character_width()

    def set_digit(self, digit, character):
        display_column=digit * self.font.get_character_width()
        self.write_character(character)
        return

    def set_message(self, message):
        for digit in range(len(message)):
            self.set_digit(digit,message[digit])

    def set_two_lines(self, line_one, line_two):
        self.clear()
        self.set_small_font()

        for digit in range(len(line_one)):
            self.set_digit(digit,line_one[digit])

        self.set_cursor(0,self.font.get_character_height()) # move onto the second line of the display
 
        for digit in range(len(line_two)):
            self.set_digit(digit,line_two[digit])

    def set_small_font(self):
        if self.cursor_col > 0: # we have already written text in big font
            self.cursor_row = ROW_OFFSET_SMALL_FONT # make the text line up nicely in this special case
        self.font.set_small_font()

    def set_big_font(self):
        self.cursor_row = 0
        self.font.set_big_font()

    def get_hanover_integers(self):
        hanover_ints=[]
        for column in range(DISPLAY_COLS): #Lets work through one column at a time. Each column has 2 bytes / integers
            top_int = 0
            bottom_int = 0
            unit = 1 # start with bit 0
            for bit in range(8):
                if self.display_binary[bit][column]:
                    top_int=top_int+unit 
                if self.display_binary[bit + 8][column]:
                    bottom_int=bottom_int+unit 
                unit = unit << 1
            hanover_ints.append(top_int)
            hanover_ints.append(bottom_int)
        return hanover_ints

    def get_hanover_ascii(self):
        hanover_ascii=[]
        hanover_integers=self.get_hanover_integers()
        for i in range(len(hanover_integers)):
            strnum = str('{:02X}'.format(hanover_integers[i]))
            if len(strnum)%2:
                strnum = '0'+strnum
            for digit in strnum:
                hanover_ascii.append(ord(digit))
            
        return hanover_ascii

    def update_hanover(self):
        #check if we are being asked to set the display to what it already is set to.
        if self.display_binary_old is not None and numpy.array_equal(self.display_binary,self.display_binary_old):
            return
        if self.ser is None:
            self.ser = serial.Serial(port=self.port,baudrate=BAUDRATE)
        length_data = DISPLAY_COLS * 2
        header = [0x02, 0x31, 0x30] #Binary output, display number zero
        strnum = str('{:02X}'.format(length_data))
        if len(strnum)%2:
            strnum = '0'+strnum
        for digit in strnum:
            header.append(ord(digit)) #header has the number of bytes of data to send now
        data=header.copy() #new list now contains the correct header
        body=self.get_hanover_ascii()
        data.extend(body)
        #now data has all we need... lets calc a checksum, add a footer, with the checksum
        checksum = 0
        for byte in data :
 	        checksum += byte
        checksum = checksum & 0xFF
        checksum = checksum ^ 255
        data.append(0x03)
        strnum = str('{:02X}'.format(checksum))
        if len(strnum)%2:
            strnum = '0'+strnum
        for digit in strnum:
            data.append(ord(digit))
        #now send data to display
        for byte in data:
            self.ser.write(chr(byte).encode())
        #Let's leave it to the destructor to close now
        #ser.close() #seemed to cause grief on linux, openning and closing all the time
        self.display_binary_old=numpy.copy(self.display_binary)
        self.screen_updates_left = self.screen_updates_left - 1

       

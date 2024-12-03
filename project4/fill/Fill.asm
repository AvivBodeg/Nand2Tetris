// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.
// the screen pixels are in the range 16384-24576

// addr = current address on screen, set to screen
@SCREEN
D=A
@addr
M=D

// Choose color white = 0, black = -1
(LOOP)
    @KBD
    D=M
    // if key is pressed (RAM[KBD] != 0): jump to BLA
    @BLACK 
    D;JNE
    (WHITE)
        @color
        M=0
        @DRAW
        0;JMP
    (BLACK)
        @color
        M=-1
(DRAW)
    @color
    D=M
    @addr
    A=M
    // RAM[addr] = color
    M=D
    @addr
    M=M+1
    D=M
    // if 24576 - addr >= 0: jump to @LOOP 
    @24576
    D=A-D
    @LOOP
    D;JGE
    // else: reset @addr
    @SCREEN 
    D=A
    @addr
    M=D
    @LOOP
    0;JMP
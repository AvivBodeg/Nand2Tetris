// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

// Reset R2 and i
@i
M=0
@R2
M=0
// Loop until i = R1
(LOOP)
    @i
    D=M
    @R1
    D=D-M
    @END
    D;JEQ
    // increase R2
    @R0
    D=M
    @R2
    M=D+M
    // check if to end loop
    @i
    M=M+1
    @LOOP
    0;JMP
// infinte loop
(End)
    @END
    0;JMP
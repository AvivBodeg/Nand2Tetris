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
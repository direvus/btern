# Multiply the value in RAM address 0 by the value in address 1.
# Store the result in address 3.
# We will use address 2 as a loop counter.
# RAM[0] = -77
MOV 0 A
MOV -77 D
CPY D M

# RAM[1] = 3
MOV 1 A
MOV 3 D
CPY D M

# RAM[3] = 0
MOV 3 A
CLR M

# RAM[2] = RAM[1]
MOV 1 A
CPY M D
MOV 2 A
CPY D M

# while (RAM[2] > 0):
#     RAM[3] += RAM[0]
#     RAM[2] -= 1
LOOP:
MOV 0 A
CPY M D
MOV 3 A
ADD D M M
MOV 2 A
DEC M D
CPY D M
MOV LOOP A
CHK D JGT
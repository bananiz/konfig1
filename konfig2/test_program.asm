; Test program to perform element-wise min operation on two vectors
; Vector 1 starts at address 0
; Vector 2 starts at address 8
; Result will be stored in Vector 2

; Load and compare first element
14 42    ; Load constant 42 into accumulator
15 0     ; Store in first vector at address 0
14 17    ; Load constant 17 into accumulator
15 8     ; Store in second vector at address 8
25 0     ; Read from first vector
20 8     ; Min operation with second vector
15 8     ; Store result back in second vector

; Load and compare second element
14 55    ; Load constant 55
15 1     ; Store in first vector
14 89    ; Load constant 89
15 9     ; Store in second vector
25 1     ; Read from first vector
20 9     ; Min operation
15 9     ; Store result

; Load and compare third element
14 23    ; Load constant 23
15 2     ; Store in first vector
14 12    ; Load constant 12
15 10    ; Store in second vector
25 2     ; Read from first vector
20 10    ; Min operation
15 10    ; Store result

; Load and compare fourth element
14 76    ; Load constant 76
15 3     ; Store in first vector
14 45    ; Load constant 45
15 11    ; Store in second vector
25 3     ; Read from first vector
20 11    ; Min operation
15 11    ; Store result

; Load and compare fifth element
14 34    ; Load constant 34
15 4     ; Store in first vector
14 67    ; Load constant 67
15 12    ; Store in second vector
25 4     ; Read from first vector
20 12    ; Min operation
15 12    ; Store result

; Load and compare sixth element
14 91    ; Load constant 91
15 5     ; Store in first vector
14 31    ; Load constant 31
15 13    ; Store in second vector
25 5     ; Read from first vector
20 13    ; Min operation
15 13    ; Store result

; Load and compare seventh element
14 28    ; Load constant 28
15 6     ; Store in first vector
14 83    ; Load constant 83
15 14    ; Store in second vector
25 6     ; Read from first vector
20 14    ; Min operation
15 14    ; Store result

; Load and compare eighth element
14 63    ; Load constant 63
15 7     ; Store in first vector
14 19    ; Load constant 19
15 15    ; Store in second vector
25 7     ; Read from first vector
20 15    ; Min operation
15 15    ; Store result

"""hello

line3

hello1"""

print("hello!")

with open("odd_numbers.txt", "w") as file:
    number = 1

    while number <= 1000:
        if number % 2 != 0:
            # Write the odd number to the file
            file.write(str(number) + "\n")
        number += 1
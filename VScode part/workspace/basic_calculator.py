# This is a basic calculator program

import sys

def add(x, y):
	return x + y

def subtract(x, y):
	return x - y

def multiply(x, y):
	return x * y

def divide(x, y):
	return x / y if y != 0 else 'Error: Division by zero is not allowed'

if __name__ == '__main__':
	print(add(int(sys.argv[1]), int(sys.argv[2])))
	print(subtract(int(sys.argv[1]), int(sys.argv[2])))
	print(multiply(int(sys.argv[1]), int(sys.argv[2])))
	print(divide(int(sys.argv[1]), int(sys.argv[2])))

from exceptions import CustomError
import logger
import logging

print("Hello")
logging.info("The log should be created")

def divide(a, b):
    if b == 0:
        raise CustomError("Division by zero is not allowed", 400)
    return a / b

try:
    result = divide(10, 0)
except CustomError as e:
    print(f"Caught an error:\n{e}")
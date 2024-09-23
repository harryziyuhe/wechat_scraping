import pyautogui
import time
import os
from utils import refresh

# Path to the screenshot image file (template to match on the screen)
account = input("Please input account name: ")
screenshot_path = f'fig/{account}.png'  # Replace with your screenshot file path

#refresh()

try:
    # Locate the screenshot element on the screen
    location = pyautogui.locateOnScreen(screenshot_path)
    print(location)
    if location is not None:
        # Get the center coordinates of the located element
        center_x, center_y = pyautogui.center(location)
        
        # Move the mouse to the center of the located element
        pyautogui.moveTo(center_x, center_y, duration=0.5)  # duration adds a smooth movement effect
        print(f"Mouse moved to {center_x}, {center_y}")
    else:
        print("Element not found on the screen. Make sure the element is visible.")
except Exception as e:
    print(f"An error occurred: {e}")


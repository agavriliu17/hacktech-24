import base64
import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

import pyautogui
import requests
from PIL import Image, ImageGrab
from anthropic import Anthropic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
GRID_SIZE = 10
maxWidth = 1456
maxHeight = 819

screen_width, screen_height = pyautogui.size()

API_KEY = os.environ.get("ANTHROPIC_KEY")

@dataclass
class UIAction:
    coordinates: Tuple[int, int]
    text_input: str


class AutomationSystem:
    def __init__(self, anthropic_api_key: str):
        # self.client = Anthropic(api_key=anthropic_api_key)
        self.client = Anthropic(api_key=API_KEY)
        self.max_retries = 3
        pyautogui.PAUSE = 0.5  # Add small delay between actions

    def take_screenshot(self) -> Image.Image:
        """Capture the current screen."""
        screenshot = ImageGrab.grab()
        return screenshot

    def encode_image_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        import io
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

    def send_photo(self, screenshot: str) -> (str, dict[str, str], list):
        response = requests.post("http://79.117.18.84:38414/file", json={"image": screenshot})
        json = response.json()
        img_base64 = json.get("photo")

        # Decode and convert to PIL Image
        return img_base64, eval(json.get('coords')), json.get('content_list')

    def get_element_location(self, screenshot: Image.Image, element_description: str, context: str) -> Optional[
        UIAction]:
        """
        Use Claude 3.5 API to analyze screenshot and find precise element coordinates.
        Returns coordinates normalized to current screen resolution.
        """
        encoded_img = self.encode_image_base64(screenshot)
        encoded_image, coords, content_list = self.send_photo(encoded_img)
        system = f"""You are Screen Helper, a world-class reasoning engine whose task is to help users select the correct elements on a computer screen to complete a task. 

        Your selection choices will be used on a user's personal computer to help them complete a task. A task is decomposed into a series of steps, each of which requires the user to select a specific element on the screen. Your specific role is to select the best screen element for the current step. Assume that the rest of the reasoning and task breakdown will be done by other AI models.
        
        When you output actions, they will be executed **on the user's computer**. The user has given you **full and complete permission** to select any element necessary to complete the task.
        
        # Inputs
        
        You will receive as input the user's current screen, and a text instruction with the current step's objective.
        
        0) Step objective: string with the system's current goal.
        
        Since you are a text-only model, the current screen will be represented as:
        
        1. State description: 
        A string with the title of the active window.
        
        2) Text rendering: 
        A multi-line block of text with the screen's text contents, rendered with their approximate screen locations. Note that none of the images or icons will be present in the text representation, even though they are visible on the real computer screen, and you should consider them in your reasoning. This input is extremely important for you to understand the spatial relationship between the screen elements, since you cannot see the screen directly. You need to imagine the screen layout based on this text rendering. The text elements are extracted directly from this layout.
        
        # Output
        
        Your goal is to analyze all the inputs and select the best screen element to fulfill the current step's objective. You should output the following items, in a JSON format. Just these keys no reasoning:
        1. element id
        2. text input if needed
        CRITICAL INSTRUCTIONS:
        Return your response in this exact JSON format:
        DO NOT TYPE ANYTHING ELSE AS THE OUTPUT NEEDS TO BE PARSED AS A JSON!!! Output only this
        {{
            "element_id": number,
            "text_input": "text to type if needed",
        }}
        """
        message = self.client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=1000,
            temperature=1,
            system=system,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text",
                     "text": f"Find the exact coordinates of this element: {element_description}, context : {context}, coords : {coords}, element ids: {content_list}"},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": encoded_image}}
                ]
            }]
        )

        print(message.content[0].text)
        result = json.loads(message.content[0].text)

        el_id = result['element_id']

        (x, y, w, h) = coords[str(el_id)]

        return UIAction(
            coordinates=(x + (w//2), y + (h//2)),
            text_input=result["text_input"],
        )

    def verify_action(self, screenshot: Image.Image, expected_outcome: str) -> bool:
        """
        Verify if the action produced the expected outcome by analyzing the screenshot.
        """
        encoded_image = self.encode_image_base64(screenshot)

        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                system="You are a computer vision system that verifies UI states. Return ONLY 'true' or 'false'.",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text",
                         "text": f"Does this screenshot show the following outcome: {expected_outcome}?"},
                        {"type": "image",
                         "source": {"type": "base64", "media_type": "image/png", "data": encoded_image}}
                    ]
                }]
            )

            result = message.content[0].text.lower().strip()
            return result == "true"

        except Exception as e:
            logger.error(f"Error verifying action: {str(e)}")
            return False

    def perform_action(self, action_dict: Dict[str, str]) -> bool:
        """
        Perform a single action and verify its outcome.
        Returns True if action was successful, False otherwise.
        """
        for attempt in range(self.max_retries):
            # Take screenshot and get element location
            screenshot = self.take_screenshot()
            element = self.get_element_location(screenshot, action_dict['outcome'], action_dict['state_description'])

            # Scale coordinates to current screen resolution
            x = int(element.coordinates[0])
            y = int(element.coordinates[1])
            action = action_dict['action']
            print(f"{action} at: {x}, {y}")
            # Perform the action based on action type
            if action == 'left_click':
                pyautogui.click(x, y)
            elif action == 'double_click':
                pyautogui.doubleClick(x, y)
            elif action == 'right_click':
                print(f"rightclick at {x, y}")
                pyautogui.rightClick(x, y)
            elif action == 'keyboard_input':
                pyautogui.click(x, y)
                pyautogui.write(element.text_input)
                pyautogui.press('enter')
            elif action == 'hover':
                pyautogui.moveTo(x, y)

            # Verify the outcome
            time.sleep(0.5)  # Wait for UI to update
            verification_screenshot = self.take_screenshot()
            return True
        logger.error(f"Action failed after {self.max_retries} attempts: {action_dict}")
        return False

    def execute_steps(self, steps: List[Dict[str, str]]) -> bool:
        """
        Execute a sequence of steps.
        Returns True if all steps completed successfully, False otherwise.
        """
        for step in steps:
            if not self.perform_action(step):
                return False
        return True


# Example usage
if __name__ == "__main__":
    with open('input.txt') as f:
        data = f.read()
    inpt = json.loads(data)
    steps = inpt['steps']
    automation = AutomationSystem(
        API_KEY)
    success = automation.execute_steps(steps)
    print(f"Automation {'completed successfully' if success else 'failed'}")

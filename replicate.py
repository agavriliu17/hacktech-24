import os

import pyautogui
from anthropic import Anthropic
import base64
from PIL import Image, ImageGrab
import time
from typing import Dict, List, Tuple, Optional
import json
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
GRID_SIZE = 10
maxWidth = 1456
maxHeight = 819

screen_width, screen_height = pyautogui.size()

API_KEY = "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"


@dataclass
class UIAction:
    coordinates: Tuple[int, int]
    confidence: float
    element_description: str
    hover_feedback_expected: str
    text_input: str


class AutomationSystem:
    def __init__(self, anthropic_api_key: str):
        self.client = Anthropic(api_key=anthropic_api_key)
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

    def get_element_location(self, screenshot: Image.Image, element_description: str, context: str) -> Optional[
        UIAction]:
        """
        Use Claude 3.5 API to analyze screenshot and find precise element coordinates.
        Returns coordinates normalized to current screen resolution.
        """
        encoded_image = self.encode_image_base64(screenshot)
        system = f"""You are a computer vision system specialized in GUI automation.
        You need to find the EXACT location of an element to interact with.

        CRITICAL INSTRUCTIONS:
        1. Look at the screenshot very carefully
        2. Find the EXACT element that matches the action description
        3. For text elements, look for the exact text match
        4. For folders/files, ensure the name matches exactly
        5. For buttons/menus, ensure it's the exact UI element needed
        6. Provide coordinates at the CENTER of the element. PROVIDE THE EXACT COORDINATE.
        Use the entire screen for coordinates do not provide them relative to the open window
        7. For hover actions, ensure the coordinates are precise!
        8. If you're not 100% certain, set confidence below 0.7
        Opening a folder is a double click
        Return your response in this exact JSON format:
        DO NOT TYPE ANYTHING ELSE AS THE OUTPUT NEEDS TO BE PARSED AS A JSON
        {{
            "coordinates": [x, y],
            "text_input": "text to type if needed",
            "confidence": 0.0 to 1.0,
            "element_description": "Detailed description of what you found and why you're confident it's correct",
            "hover_feedback_expected": "Description of expected visual feedback during hover (tooltip, highlight, etc.)"
        }}"""
        message = self.client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=1000,
            temperature=1,
            system=system,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text",
                     "text": f"Find the exact coordinates of this element: {element_description}, context : {context}"},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": encoded_image}}
                ]
            }]
        )
        print(message.content[0].text)
        result = json.loads(message.content[0].text)
        print(result)

        return UIAction(
            coordinates=(result["coordinates"][0], result["coordinates"][1]),
            confidence=result["confidence"],
            element_description=result["element_description"],
            hover_feedback_expected=result["hover_feedback_expected"],
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
            element = self.get_element_location(screenshot, action_dict['purpose'], action_dict['context'])

            if not element or element.confidence < 0.8:
                logger.warning(f"Low confidence or no element found. Attempt {attempt + 1}/{self.max_retries}")
                continue

            # Scale coordinates to current screen resolution
            x = int(element.coordinates[0]) * (screen_width / maxWidth)
            y = int(element.coordinates[1]) * (screen_height / maxHeight)
            action = action_dict['action']
            expected = element.hover_feedback_expected
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
            # TODO: verify
            # if self.verify_action(verification_screenshot, expected):
            #     logger.info(f"Action successful: {expected}")
            #     return True

            # logger.warning(f"Action verification failed. Attempt {attempt + 1}/{self.max_retries}")

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
    inpt = {
        "os": "macos",
        "steps": [
            {
                "step_number": 1,
                "app": "Finder",
                "action": "double_click",
                "purpose": "To open the 'job_descriptions' folder.",
                "context": "The user is in the Finder application on macOS and clicks on the 'job_descriptions' folder inside the 'DataSet' directory."
            },
            {
                "step_number": 2,
                "app": "Finder",
                "action": "right_click",
                "purpose": "To open the context menu within the folder. Click on a empty part of the explorer",
                "context": "The settings menu is used to perform various actions like creating a new folder."
            },
            {
                "step_number": 3,
                "app": "Finder",
                "action": "left_click",
                "purpose": "To create a new folder.",
                "context": "The user selects 'New Folder' from the settings menu."
            },
            {
                "step_number": 4,
                "app": "Finder",
                "action": "keyboard_input",
                "purpose": "To name the newly created folder.",
                "context": "The folder is named 'untitled folder' by default, and the user is editing its name to 'test'."
            }
        ]
    }
    steps = inpt['steps']
    automation = AutomationSystem(
        API_KEY)
    success = automation.execute_steps(steps)
    print(f"Automation {'completed successfully' if success else 'failed'}")

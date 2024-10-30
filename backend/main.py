from openai import OpenAI
from dotenv import load_dotenv
import cv2
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import json
import os
from prompts import analyze_video_promp

load_dotenv()
API_KEY = os.environ.get("OPENAI_API_KEY")

# Helper function to calculate Mean Squared Error (MSE) between two images


def mse(img1, img2):
    h, w, _ = img1.shape
    diff = cv2.subtract(img1, img2)
    err = np.sum(diff**2)
    mse = err/(float(h*w))
    return mse


def process_video(video_path):
    # Initialize video capture object
    cap = cv2.VideoCapture(video_path)

    # Check if video opened successfully
    if not cap.isOpened():
        print("Error: Could not open video.")
        exit()

    # Read the first frame from the video
    ret, prev_frame = cap.read()
    if not ret:
        print("Error: Could not read the first frame.")
        cap.release()
        exit()

    # Convert the first frame to grayscale
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    # Parameters
    THRESHOLD = 70  # Difference threshold to detect state change
    MIN_DIFF_AREA = 500  # Minimum area of change to be considered relevant
    FRAME_SKIP = 15  # Skip a certain number of frames to make the process faster

    frame_count = 0  # Initialize frame counter for skipping frames
    previous_frame = None
    previous_mse = 0  # Track previous MSE
    base64_images = []  # Array to store base64-encoded images

    while True:
        # Read the next frame from the video
        ret, frame = cap.read()
        if not ret:
            print("End of video reached.")
            break

        frame_count += 1

        # Process every 'FRAME_SKIP' frame (to speed up the process)
        if frame_count % FRAME_SKIP != 0:
            continue

        # Convert the current frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Compute the absolute difference between the current and previous frame
        diff = cv2.absdiff(prev_gray, gray)

        # Apply a binary threshold to the difference image
        _, thresh = cv2.threshold(diff, THRESHOLD, 255, cv2.THRESH_BINARY)

        # Find contours of the difference regions
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Check if any significant change is detected based on contour area
        change_detected = False

        for contour in contours:
            if cv2.contourArea(contour) > MIN_DIFF_AREA:
                # Significant change detected
                change_detected = True
                print(f"Relevant change detected at frame {frame_count}")

                # Initialize current_mse to 0 if previous_frame is None
                current_mse = 0 if previous_frame is None else mse(
                    previous_frame, frame)

                # Calculate MSE difference if a previous MSE value exists
                mse_difference = abs(
                    current_mse - previous_mse) if previous_frame is not None else None

                # Save image locally and to Base64 list if relevant change
                if (previous_frame is None) or (mse_difference and mse_difference > 0.05):
                    # Save frame as an image locally
                    filename = f'relevant_change_{frame_count}.png'
                    cv2.imwrite(filename, frame)

                    # Convert frame to Base64 and store it
                    pil_img = Image.fromarray(
                        cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    buffer = BytesIO()
                    pil_img.save(buffer, format="PNG")
                    base64_images.append(base64.b64encode(
                        buffer.getvalue()).decode('utf-8'))

                    # Update previous_frame and previous_mse
                    previous_frame = frame
                    previous_mse = current_mse
                break  # Exit the loop once a relevant change is detected

        # Update the previous frame to the current frame
        prev_gray = gray

        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release video capture object
    cap.release()
    cv2.destroyAllWindows()

    # Now, base64_images contains the Base64-encoded strings of each relevant frame
    return base64_images


def analyze_video(parsed_images):
    client = OpenAI(api_key=API_KEY)

    # Use map to apply the transformation to each item
    parsed_images = list(map(lambda img: {
        "type": "image_url",
        "image_url": {
            "url": f'data:image/png;base64,{img}'
        }
    }, parsed_images))

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "analyze these screen captures carefully and explain in step by step the actions that the user is taking"
                    }
                ]
            },
            {
                "role": "user",
                "content": parsed_images
            },
        ],
        temperature=1,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "video_explanation",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "steps": {
                            "type": "array",
                            "description": "A sequence of steps explaining actions taken in the video.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "state_description": {
                                        "type": "string",
                                        "description": "A description of the state of the application or software at the time of the action."
                                    },
                                    "action": {
                                        "type": "string",
                                        "description": "The specific action performed, such as right click, left click, typing, etc.",
                                        "enum": [
                                            "right_click",
                                            "left_click",
                                            "double_click",
                                            "hover",
                                            "keyboard_input"
                                        ]
                                    },
                                    "outcome": {
                                        "type": "string",
                                        "description": "The result or consequence of the action taken."
                                    }
                                },
                                "required": [
                                    "state_description",
                                    "action",
                                    "outcome"
                                ],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": [
                        "steps"
                    ],
                    "additionalProperties": False
                }
            }
        }
    )

    return response


# parsed_images = process_video("recording2.mov")
# response = analyze_video(parsed_images)

# print(response.choices[0].message.content)

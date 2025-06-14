import requests

def perform_ocr(image_path, api_key, language='chs', ocr_engine=2):
    """
    Performs OCR on an image using the OCR.space API.
    """
    api_url = 'https://api.ocr.space/parse/image'

    try:
        with open(image_path, 'rb') as image_file:
            payload = {
                'apikey': api_key,
                'language': language,
                'OCREngine': str(ocr_engine), # API expects OCREngine as string
                'isOverlayRequired': 'False', # Boolean False can also be used, API is flexible
            }
            files = {
                'file': (image_path.split('/')[-1], image_file) # Send filename for clarity
            }

            print(f"Sending OCR request for {image_path} with API key {api_key[:5]}... (Engine: {ocr_engine}, Lang: {language})")

            response = requests.post(api_url, data=payload, files=files, timeout=30) # Added timeout

            # Check if the request was successful before trying to parse JSON
            if response.status_code != 200:
                # Attempt to get error message from response body if possible
                try:
                    error_data = response.json()
                    error_message_detail = error_data.get('ErrorMessage', [f"HTTP Status {response.status_code}"])[0]
                    if isinstance(error_message_detail, list): # Sometimes ErrorMessage is a list of strings
                        error_message_detail = ", ".join(error_message_detail)
                except ValueError: # If response is not JSON
                    error_message_detail = response.text or f"HTTP Status {response.status_code}"
                return f"OCR Error: Request failed. ({error_message_detail})"

            result = response.json()

            if result.get('IsErroredOnProcessing'):
                error_messages = result.get('ErrorMessage', ['Unknown processing error.'])
                # ErrorMessage can be a list or a string
                if isinstance(error_messages, list):
                    return f"OCR Error: {', '.join(error_messages)}"
                else:
                    return f"OCR Error: {error_messages}"

            if result.get('OCRExitCode') == 1 and result.get('ParsedResults'):
                parsed_text = result['ParsedResults'][0].get('ParsedText', '')
                if parsed_text:
                    return parsed_text.strip()
                else:
                    return "OCR Error: No text found in results."
            elif result.get('OCRExitCode') in [2,3,4,5,6,7]: # Specific error codes from OCR.space
                 error_messages = result.get('ErrorMessage', ['Specific OCR error code received.'])
                 if isinstance(error_messages, list):
                    return f"OCR Error ({result.get('OCRExitCode')}): {', '.join(error_messages)}"
                 else:
                    return f"OCR Error ({result.get('OCRExitCode')}): {error_messages}"
            else:
                # Fallback for other unexpected OCR.space responses
                error_message = result.get('ErrorMessage', ['Unknown OCR error from API. Check OCRExitCode.'])[0] if isinstance(result.get('ErrorMessage'), list) else result.get('ErrorMessage', 'Unknown OCR error from API. Check OCRExitCode.')
                return f"OCR Error: {error_message} (OCRExitCode: {result.get('OCRExitCode')})"

    except requests.exceptions.Timeout:
        return f"Network Error: The request to OCR.space timed out."
    except requests.exceptions.RequestException as e:
        # Handles network errors, connection errors etc.
        return f"Network Error: {e}"
    except FileNotFoundError:
        return f"Error: Image file not found at {image_path}"
    except Exception as e:
        # Catch-all for other unexpected errors (e.g., issues not related to requests)
        return f"Error processing OCR request: {e}"

if __name__ == '__main__':
    # This is a placeholder for direct testing.
    # To test this properly, you would need:
    # 1. A valid API key for OCR.space.
    # 2. An image file (e.g., 'test_image.png').
    #
    # Example (replace with your actual key and a test image path):
    # test_api_key = "YOUR_ACTUAL_OCR_SPACE_API_KEY"
    # test_image = "path/to/your/test_image.png"
    #
    # if test_api_key == "YOUR_ACTUAL_OCR_SPACE_API_KEY" or not os.path.exists(test_image):
    #     print("Please set a valid API key and image path to test ocr_service.py directly.")
    # else:
    #     print(f"Testing OCR service with image: {test_image}")
    #     ocr_text_result = perform_ocr(test_image, test_api_key)
    #     print("\n--- OCR Result ---")
    #     print(ocr_text_result)
    #     print("--- End of OCR Result ---")
    print("ocr_service.py: To test, provide a valid API key and image path in the __main__ block.")

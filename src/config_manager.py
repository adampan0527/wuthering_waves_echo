import json
import os

CONFIG_FILE_PATH = "config.json"  # At the root of the project

def save_api_key(api_key: str):
    """Saves the API key to the config file."""
    try:
        with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump({"api_key": api_key}, f, ensure_ascii=False, indent=4)
        print(f"API Key saved to {CONFIG_FILE_PATH}")
        return True
    except Exception as e:
        print(f"Error saving API Key to {CONFIG_FILE_PATH}: {e}")
        return False

def load_api_key() -> str | None:
    """Loads the API key from the config file."""
    if not os.path.exists(CONFIG_FILE_PATH):
        print(f"Config file {CONFIG_FILE_PATH} not found.")
        return None

    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            api_key = config_data.get("api_key")
            if api_key:
                print(f"API Key loaded from {CONFIG_FILE_PATH}")
                return api_key
            else:
                print(f"API Key not found in {CONFIG_FILE_PATH}.")
                return None
    except FileNotFoundError: # Should be caught by os.path.exists, but as a safeguard
        print(f"Config file {CONFIG_FILE_PATH} not found during load attempt.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {CONFIG_FILE_PATH}. File might be corrupted.")
        return None
    except Exception as e:
        print(f"Error loading API Key from {CONFIG_FILE_PATH}: {e}")
        return None

if __name__ == '__main__':
    # Test saving
    print("Testing config_manager.py...")
    test_key_to_save = "test_12345_abcdef"
    if save_api_key(test_key_to_save):
        print(f"Saved '{test_key_to_save}' successfully.")
    else:
        print(f"Failed to save '{test_key_to_save}'.")

    # Test loading
    loaded_key = load_api_key()
    if loaded_key:
        print(f"Loaded API Key: '{loaded_key}'")
        if loaded_key == test_key_to_save:
            print("Load test successful: Loaded key matches saved key.")
        else:
            print("Load test failed: Loaded key does not match saved key.")
    else:
        print("Failed to load API Key after saving.")

    # Test loading non-existent key (by temporarily renaming config file if it was created)
    original_path = CONFIG_FILE_PATH
    test_path_for_not_found = "temp_config_not_found.json"

    if os.path.exists(original_path):
        try:
            os.rename(original_path, test_path_for_not_found)
            print(f"\nTesting load_api_key when file '{original_path}' is missing...")
            should_be_none = load_api_key()
            if should_be_none is None:
                print("Correctly returned None for missing file.")
            else:
                print(f"Incorrectly returned '{should_be_none}' for missing file.")
        finally: # Ensure rename back
            if os.path.exists(test_path_for_not_found):
                 os.rename(test_path_for_not_found, original_path)
    else:
        print(f"\nSkipping missing file load test as '{original_path}' was not created by save test.")

    # Clean up test file
    # if os.path.exists(CONFIG_FILE_PATH):
    #     os.remove(CONFIG_FILE_PATH)
    #     print(f"\nCleaned up {CONFIG_FILE_PATH}")

import os
import openai
import py_chronolog_client

# Update LD_LIBRARY_PATH
current_ld_library_path = os.environ.get("LD_LIBRARY_PATH", "")
os.environ["LD_LIBRARY_PATH"] = "/home/ssonar/chronolog/Debug/lib:" + current_ld_library_path
print("Updated LD_LIBRARY_PATH:", os.environ["LD_LIBRARY_PATH"])

# Update PYTHONPATH environment variable
current_pythonpath = os.environ.get("PYTHONPATH", "")
os.environ["PYTHONPATH"] = "/home/ssonar/chronolog/Debug/lib:" + current_pythonpath

print("Updated PYTHONPATH:", os.environ["PYTHONPATH"])

print("Updated LD_LIBRARY_PATH:", os.environ["LD_LIBRARY_PATH"])

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def chat_with_gpt(prompt, model="gpt-3.5-turbo", temperature=0.7):
    """
    Sends a prompt to the ChatGPT API and returns the response.

    Args:
        prompt (str): The user's prompt to send to ChatGPT.
        model (str): The model name to use (default: "gpt-3.5-turbo").
        temperature (float): Controls randomness (default: 0.7).

    Returns:
        str: The response text from ChatGPT.
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    # --- ChatGPT Interaction ---
    user_prompt = "Give 100 questions on the topic of Artificial Intelligence."
    print("Sending prompt to ChatGPT...")
    chatgpt_response = chat_with_gpt(user_prompt)
    
    if chatgpt_response:
        print("ChatGPT response received:")
        print(chatgpt_response)
    else:
        print("Failed to get a response from ChatGPT.")
        return  # Exit if no response was obtained

    # --- ChronoLog Logging ---
    print("\nConnecting to ChronoLog...")
    # Initialize ChronoLog client configuration.
    clientConf = py_chronolog_client.ClientPortalServiceConf("ofi+sockets", "127.0.0.1", 5555, 55)
    client = py_chronolog_client.Client(clientConf)
    
    # Connect to the ChronoVisor service.
    return_code = client.Connect()
    print("client.Connect() call returns:", return_code)
    
    # Create a chronicle (if it does not already exist).
    attrs = dict()
    return_code = client.CreateChronicle("chronicle_chatgpt", attrs, 1)
    print("client.CreateChronicle() returned:", return_code)
    
    # Acquire a story within the chronicle to log events.
    return_tuple = client.AcquireStory("chronicle_chatgpt", "chatgpt_story", attrs, 1)
    print("client.AcquireStory() returned:", return_tuple)
    
    if return_tuple[0] == 0:
        print("Acquired Story = chatgpt_story within chronicle = chronicle_chatgpt")
        # Log the ChatGPT response as an event.
        print("Logging ChatGPT response as an event in ChronoLog...")
        return_tuple[1].log_event(chatgpt_response)
    else:
        print("Failed to acquire story for logging.")
    
    # Release the acquired story.
    return_code = client.ReleaseStory("chronicle_chatgpt", "chatgpt_story")
    print("client.ReleaseStory() returned:", return_code)
    
    # Disconnect the client from the ChronoLog system.
    return_code = client.Disconnect()
    print("client.Disconnect() returned:", return_code)

if __name__ == "__main__":
    main()

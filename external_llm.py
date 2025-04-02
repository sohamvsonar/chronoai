import os
import time
import openai
import py_chronolog_client

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def chat_with_gpt(prompt, model="gpt-3.5-turbo", temperature=0.7):
    """
    Sends a prompt to the ChatGPT API and returns the response.
    
    Args:
        prompt (str): The user's prompt.
        model (str): The model name (default: "gpt-3.5-turbo").
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
        print(f"Error in chat_with_gpt: {e}")
        return None

def main():
    # --- ChronoLog Client Setup ---
    print("Connecting to ChronoLog...")
    clientConf = py_chronolog_client.ClientPortalServiceConf("ofi+sockets", "127.0.0.1", 5555, 55)
    client = py_chronolog_client.Client(clientConf)
    
    return_code = client.Connect()
    print("client.Connect() returns:", return_code)
    
    attrs = dict()
    return_code = client.CreateChronicle("py_chronicle", attrs, 1)
    print("client.CreateChronicle() returns:", return_code)
    
    return_tuple = client.AcquireStory("py_chronicle", "chatgpt_test_story", attrs, 1)
    print("client.AcquireStory() returns:", return_tuple)
    
    if return_tuple[0] != 0:
        print("Failed to acquire story. Exiting.")
        return
    story = return_tuple[1]

    # --- Loop to Send 100 Prompts and Log Responses ---
    for i in range(1, 101):
        prompt = f"Test prompt {i}: Tell me something interesting about the number {i}."
        print(f"\nSending prompt {i}: {prompt}")
        response = chat_with_gpt(prompt)
        
        if response:
            print("Received response:")
            print(response)
        else:
            response = "No response received due to an error."
        
        # Combine prompt and response into one log message
        log_message = f"Prompt: {prompt}\nResponse: {response}"
        print("Logging event to ChronoLog...")
        story.log_event(log_message)
        
        # Optional: Pause briefly to avoid hitting API rate limits.
        time.sleep(1)

    # --- Clean Up ChronoLog Client ---
    return_code = client.ReleaseStory("py_chronicle", "chatgpt_test_story")
    print("\nclient.ReleaseStory() returns:", return_code)
    
    return_code = client.Disconnect()
    print("client.Disconnect() returns:", return_code)

if __name__ == "__main__":
    main()

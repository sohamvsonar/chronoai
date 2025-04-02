import os
import time
import requests
import py_chronolog_client

def prompt_ollama(model, prompt, server_url='http://localhost:11434'):
    url = f'{server_url}/api/generate'
    data = {
        'model': model,
        'prompt': prompt,
        'stream': False
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        return result.get('response', '').strip()
    else:
        print(f"Request failed: {response.status_code}: {response.text}")
        return None

def main():
    # --- ChronoLog Client Setup ---
    print("Connecting to ChronoLog...")
    clientConf = py_chronolog_client.ClientPortalServiceConf("ofi+sockets", "127.0.0.1", 5555, 55)
    client = py_chronolog_client.Client(clientConf)
    
    return_code = client.Connect()
    print("client.Connect() returns:", return_code)
    
    attrs = dict()
    return_code = client.CreateChronicle("chronicle_llama", attrs, 1)
    print("client.CreateChronicle() returns:", return_code)
    
    return_tuple = client.AcquireStory("chronicle_llama", "story_llama", attrs, 1)
    print("client.AcquireStory() returns:", return_tuple)
    
    if return_tuple[0] != 0:
        print("Failed to acquire story. Exiting.")
        return
    story = return_tuple[1]

    # --- Loop to Send 100 Prompts and Log Responses ---
    for i in range(1, 101):
        prompt = f"Test prompt {i}: Tell me something interesting about the number {i} in short."
        print(f"\nSending prompt {i}: {prompt}")
        response = prompt_ollama("llama3.2", prompt)
        
        if response:
            print("Received response:")
            print(response)
        else:
            response = "No response received due to an error."
        
        # Combine prompt and response into one log message
        log_message = f"Prompt: {prompt}\nResponse: {response}"
        print("Logging event to ChronoLog...")
        story.log_event(log_message)
        
        # Optional pause to avoid overwhelming the server.
        time.sleep(1)

    # --- Clean Up ChronoLog Client ---
    return_code = client.ReleaseStory("chronicle_llama", "story_llama")
    print("\nclient.ReleaseStory() returns:", return_code)
    
    return_code = client.Disconnect()
    print("client.Disconnect() returns:", return_code)

if __name__ == "__main__":
    main()

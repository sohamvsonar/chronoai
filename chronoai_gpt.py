import os
import openai
import py_chronolog_client

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def gpt_interaction(prompt_text):
    # 1. Set up ChronoLog client
    client_conf = py_chronolog_client.ClientPortalServiceConf("ofi+sockets", "127.0.0.1", 5555,55)
    client = py_chronolog_client.Client(client_conf)
    
    # 2. Connect and prepare a chronicle + story
    client.Connect()
    code = client.CreateChronicle("chatgpt", {}, 1)
    #print(code)
    ret, story = client.AcquireStory("chatgpt", "database", {}, 1)
    print(ret, story)
    if ret != 0:
        raise RuntimeError("Failed to acquire story for logging.")
    
    # 3. Send prompt to ChatGPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0.7
    ).choices[0].message["content"].strip()
    
    # 4. Log prompt and response
    log_entry = f"Response: {response}"
    story.log_event(log_entry)
    
    # 5. Tear down
    client.ReleaseStory("chatgpt", "database")
    print("Released")
    client.Disconnect()
    
    return response


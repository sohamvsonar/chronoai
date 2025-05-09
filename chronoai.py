import os
import py_chronolog_client

def ai_interaction(output):
    # 1. Set up ChronoLog client
    client_conf = py_chronolog_client.ClientPortalServiceConf("ofi+sockets", "127.0.0.1", 5555,55)
    client = py_chronolog_client.Client(client_conf)
    
    # 2. Connect and prepare a chronicle + story
    client.Connect()
    code = client.CreateChronicle("chatgpt", {}, 1)
    #print(code)
    ret, story = client.AcquireStory("chatgpt", "conversation", {}, 1)
    #print(ret, story)
    if ret != 0:
        raise RuntimeError("Failed to acquire story for logging.")
        
    # 4. Log prompt and response
    log_entry = output
    story.log_event(log_entry)
    
    # 5. Tear down
    client.ReleaseStory("chatgpt", "conversation")
    print("Released")
    client.Disconnect()    

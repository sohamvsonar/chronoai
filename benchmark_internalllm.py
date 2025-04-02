import os
import time
import requests
import py_chronolog_client

# --- Helper function to send prompt to Ollama server ---
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

# --- Benchmark without ChronoLog logging ---
def benchmark_without_chronolog(n=100):
    print("\n--- Benchmark: WITHOUT ChronoLog Logging ---")
    start_time = time.time()
    for i in range(1, n + 1):
        prompt = f"Test prompt {i}: Tell me something interesting about the number {i} in short."
        response = prompt_ollama("llama3.2", prompt)
        if response is None:
            response = "No response received due to an error."
        print(f"Request {i} completed.")

        # No logging is performed here
        # Optionally, add a delay if necessary:
        time.sleep(0.1)
    end_time = time.time()
    duration = end_time - start_time
    print(f"Benchmark without ChronoLog logging completed in {duration:.2f} seconds")
    return duration

# --- Setup ChronoLog Client ---
def setup_chronolog():
    print("\nSetting up ChronoLog...")
    clientConf = py_chronolog_client.ClientPortalServiceConf("ofi+sockets", "127.0.0.1", 5555, 55)
    client = py_chronolog_client.Client(clientConf)
    
    ret = client.Connect()
    print("client.Connect() returns:", ret)
    
    attrs = {}
    ret = client.CreateChronicle("bench_chronicle_llama", attrs, 1)
    print("client.CreateChronicle() returns:", ret)
    
    ret_tuple = client.AcquireStory("bench_chronicle_llama", "bench_story_llama", attrs, 1)
    print("client.AcquireStory() returns:", ret_tuple)
    
    if ret_tuple[0] != 0:
        print("Failed to acquire story. Exiting benchmark with logging.")
        return None, None
    story = ret_tuple[1]
    return client, story

# --- Benchmark with ChronoLog logging ---
def benchmark_with_chronolog(n=100, story=None):
    print("\n--- Benchmark: WITH ChronoLog Logging ---")
    start_time = time.time()
    for i in range(1, n + 1):
        prompt = f"Test prompt {i}: Tell me something interesting about the number {i} in short."
        response = prompt_ollama("llama3.2", prompt)
        if response is None:
            response = "No response received due to an error."
        # Combine prompt and response into one log message
        log_message = f"Prompt: {prompt}\nResponse: {response}"
        story.log_event(log_message)
        print(f"Request {i} and logging completed.")

        # Optionally, add a delay if necessary:
        time.sleep(0.1)
    end_time = time.time()
    duration = end_time - start_time
    print(f"Benchmark with ChronoLog logging completed in {duration:.2f} seconds")
    return duration

# --- Release ChronoLog Client ---
def release_chronolog(client):
    ret = client.ReleaseStory("bench_chronicle_llama", "bench_story_llama")
    print("client.ReleaseStory() returns:", ret)
    ret = client.Disconnect()
    print("client.Disconnect() returns:", ret)

# --- Main function to run benchmarks sequentially ---
def main():
    iterations = 100
    print("Starting benchmark tests...")
    
    # Run the benchmark without logging first
    duration_without = benchmark_without_chronolog(iterations)
    
    # Set up ChronoLog for the second benchmark
    client, story = setup_chronolog()
    if client is None or story is None:
        print("Skipping benchmark with ChronoLog due to setup failure.")
        return
    
    # Run the benchmark with ChronoLog logging
    duration_with = benchmark_with_chronolog(iterations, story)
    
    # Release the ChronoLog resources as the last process
    release_chronolog(client)
    
    # Output the benchmark results
    print("\n--- Benchmark Results ---")
    print(f"Without ChronoLog Logging: {duration_without:.2f} seconds")
    print(f"With ChronoLog Logging:    {duration_with:.2f} seconds")
    
    overhead = duration_with - duration_without
    print(f"Logging overhead: {overhead:.2f} seconds over {iterations} iterations")

if __name__ == "__main__":
    main()

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

def benchmark_without_logging(num_requests=100):
    """
    Benchmarks ChatGPT requests without ChronoLog logging.
    """
    print("Benchmarking without ChronoLog logging...")
    start_time = time.perf_counter()
    for i in range(1, num_requests + 1):
        prompt = f"Test prompt {i}: Tell me something interesting about the number {i}."
        response = chat_with_gpt(prompt)
        if response is None:
            response = "No response"
        print(f"Request {i} completed.")
    end_time = time.perf_counter()
    total_time = end_time - start_time
    avg_time = total_time / num_requests
    return total_time, avg_time

def benchmark_with_logging(num_requests=100):
    """
    Benchmarks ChatGPT requests with ChronoLog logging.
    """
    print("Benchmarking with ChronoLog logging...")
    
    # Setup ChronoLog client
    clientConf = py_chronolog_client.ClientPortalServiceConf("ofi+sockets", "127.0.0.1", 5555, 55)
    client = py_chronolog_client.Client(clientConf)
    
    connect_code = client.Connect()
    print("client.Connect() returns:", connect_code)
    
    attrs = dict()
    create_code = client.CreateChronicle("py_chronicle_101", attrs, 1)
    print("client.CreateChronicle() returns:", create_code)
    
    ret_tuple = client.AcquireStory("py_chronicle_101", "benchmark_story_101", attrs, 1)
    if ret_tuple[0] != 0:
        print("Failed to acquire story for logging.")
        return None, None
    story = ret_tuple[1]

    start_time = time.perf_counter()
    for i in range(1, num_requests + 1):
        prompt = f"Test prompt {i}: Tell me something interesting about the number {i}."
        response = chat_with_gpt(prompt)
        if response is None:
            response = "No response"
        log_message = f"Prompt: {prompt}\nResponse: {response}"
        story.log_event(log_message)
        print(f"Request {i} and logging completed.")
    end_time = time.perf_counter()
    total_time = end_time - start_time
    avg_time = total_time / num_requests

    release_code = client.ReleaseStory("py_chronicle_101", "benchmark_story_101")
    print("client.ReleaseStory() returns:", release_code)
    
    disconnect_code = client.Disconnect()
    print("client.Disconnect() returns:", disconnect_code)

    return total_time, avg_time

def main():
    num_requests = 100

    # Benchmark without ChronoLog logging
    total_no_log, avg_no_log = benchmark_without_logging(num_requests)
    print(f"\nBenchmark without logging: Total time = {total_no_log:.2f}s, "
          f"Average time per request = {avg_no_log:.2f}s\n")

    # Benchmark with ChronoLog logging
    total_with_log, avg_with_log = benchmark_with_logging(num_requests)
    if total_with_log is not None:
        print(f"\nBenchmark with logging: Total time = {total_with_log:.2f}s, "
              f"Average time per request = {avg_with_log:.2f}s")

if __name__ == "__main__":
    main()

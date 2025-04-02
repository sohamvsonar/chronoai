import os
import time
import openai
import py_chronolog_client

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def chat_with_gpt(prompt, model="gpt-3.5-turbo", temperature=0.7):
    """
    Sends a prompt to the ChatGPT API and returns the response along with the call duration.
    """
    start_time = time.perf_counter()
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    return response.choices[0].message['content'].strip(), elapsed_time

def benchmark_without_logging(prompt, iterations=5):
    """
    Benchmarks ChatGPT API call without ChronoLog logging.
    """
    total_chat_time = 0.0
    total_overall_time = 0.0

    print("Benchmarking ChatGPT response WITHOUT ChronoLog logging:")
    for i in range(iterations):
        overall_start = time.perf_counter()
        response, chat_time = chat_with_gpt(prompt)
        total_chat_time += chat_time
        overall_end = time.perf_counter()
        overall_time = overall_end - overall_start
        total_overall_time += overall_time
        print(f"Iteration {i+1}: ChatGPT call took {chat_time:.2f} s, overall time {overall_time:.2f} s")

    avg_chat_time = total_chat_time / iterations
    avg_overall_time = total_overall_time / iterations
    print("\nAverage ChatGPT call time: {:.2f} s".format(avg_chat_time))
    print("Average overall time (without logging): {:.2f} s".format(avg_overall_time))
    print("-" * 50, "\n")

def benchmark_with_logging(prompt, iterations=5):
    """
    Benchmarks ChatGPT API call with ChronoLog logging.
    Initializes the ChronoLog client once and reuses it for logging.
    """
    # Setup ChronoLog client configuration (do this once)
    clientConf = py_chronolog_client.ClientPortalServiceConf("ofi+sockets", "127.0.0.1", 5555, 55)
    client = py_chronolog_client.Client(clientConf)
    
    # Connect to ChronoLog system once
    connect_ret = client.Connect()
    print("ChronoLog client.Connect() returned:", connect_ret)
    
    attrs = dict()
    create_ret = client.CreateChronicle("py_chronicle_test", attrs, 1)
    print("ChronoLog client.CreateChronicle() returned:", create_ret)
    
    # Acquire story once (reuse it across iterations)
    ret_tuple = client.AcquireStory("py_chronicle_test", "chatgpt_story_test", attrs, 1)
    if ret_tuple[0] != 0:
        print("Failed to acquire story for logging. Error code:", ret_tuple[0])
        return
    story_handle = ret_tuple[1]

    total_chat_time = 0.0
    total_overall_time = 0.0

    print("Benchmarking ChatGPT response WITH ChronoLog logging:")
    for i in range(iterations):
        overall_start = time.perf_counter()

        # Get ChatGPT response and measure its call time.
        response, chat_time = chat_with_gpt(prompt)
        total_chat_time += chat_time

        # Log the response as an event in the acquired story.
        story_handle.log_event(response)

        overall_end = time.perf_counter()
        overall_time = overall_end - overall_start
        total_overall_time += overall_time

        print(f"Iteration {i+1}: ChatGPT call took {chat_time:.2f} s, overall time {overall_time:.2f} s")

    avg_chat_time = total_chat_time / iterations
    avg_overall_time = total_overall_time / iterations
    print("\nAverage ChatGPT call time: {:.2f} s".format(avg_chat_time))
    print("Average overall time (including logging): {:.2f} s".format(avg_overall_time))
    print("-" * 50, "\n")

    # Cleanup: Release story and disconnect once after all iterations
    release_ret = client.ReleaseStory("py_chronicle", "chatgpt_story")
    print("ChronoLog client.ReleaseStory() returned:", release_ret)
    disconnect_ret = client.Disconnect()
    print("ChronoLog client.Disconnect() returned:", disconnect_ret)

def main():
    prompt = "Give 100 questions on the topic of Artificial Intelligence."
    iterations = 5  # Adjust as needed

    benchmark_without_logging(prompt, iterations)
    benchmark_with_logging(prompt, iterations)

if __name__ == "__main__":
    main()

from chronoai_gpt import gpt_interaction


if __name__ == "__main__":
    #prompt = "Give a sample Database schema code snippet for the CRM Project"
    reply = gpt_interaction("Explain in detail what is an model context protocol server and how it works")
    print(reply)


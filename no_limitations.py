import os
import time
from openai import AzureOpenAI
from utils import load, dump
from dotenv import load_dotenv

load_dotenv()


def segment_with_openai(text: str, deployment_name: str) -> str:
    """
    Segments text into sentences using Azure OpenAI.
    """
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2023-07-01-preview"
    )

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that segments text into sentences. For each sentence, you will add a newline character at the end. The data is presented in naive chunks, it is possible that some sentences (mainly at the start and the end of file) are incomplete. Take that into account. Do not add any extra text or explanations."},
            {"role": "user", "content": f"Segment the following text into sentences:\n\n{text}"}
        ],
        temperature=0.1
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    # Make sure to set the following environment variables:
    # AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT_NAME

    deployment = os.getenv("MEDIA_LAB_AZURE_OPENAI_GPT41_DEPLOYMENT_NAME")
    if not all([os.getenv("AZURE_OPENAI_ENDPOINT"), os.getenv("AZURE_OPENAI_API_KEY"), deployment]):
        print("Error: Please set the required environment variables: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT_NAME")
    else:
        file_content = load('data/pa153_2025_test_all.txt')

        # Split content into chunks of 1000 characters to avoid rate limits
        chunk_size = 2000
        chunks = [file_content[i:i+chunk_size] for i in range(0, len(file_content), chunk_size)]

        segmented_text = ""
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}...")
            try:
                segmented_text += segment_with_openai(chunk, deployment)
                time.sleep(20)  # Add a delay between requests
            except Exception as e:
                if "RateLimitReached" in str(e):
                    print("Rate limit reached. Waiting for 60 seconds before retrying...")
                    time.sleep(60)
                    try:
                        segmented_text += segment_with_openai(chunk, deployment)
                    except Exception as retry_e:
                        print(f"An error occurred on retry: {retry_e}")
                        break
                elif "content_filter" in str(e):
                    print(f"Content filter triggered for chunk {i+1}. Splitting the chunk and retrying.")
                    sub_chunks = chunk.split('.')
                    for sub_chunk in sub_chunks:
                        if not sub_chunk.strip():
                            continue

                        sub_chunk_to_process = sub_chunk + '.' if not chunk.endswith(sub_chunk) else sub_chunk

                        try:
                            segmented_text += segment_with_openai(sub_chunk_to_process, deployment)
                            time.sleep(20)
                        except Exception as sub_e:
                            if "content_filter" in str(sub_e):
                                print("Content filter triggered for sub-chunk. Skipping this part.")
                                continue
                            elif "RateLimitReached" in str(sub_e):
                                print("Rate limit reached on sub-chunk. Waiting for 60 seconds before retrying...")
                                time.sleep(60)
                                try:
                                    segmented_text += segment_with_openai(sub_chunk_to_process, deployment)
                                except Exception as retry_sub_e:
                                    print(f"An error occurred on sub-chunk retry: {retry_sub_e}")
                            else:
                                print(f"An error occurred on sub-chunk: {sub_e}")
                    continue
                else:
                    print(f"An error occurred: {e}")
                    break

        dump('output/no_limitations_output.txt', segmented_text)
        print("Segmentation complete. Output written to output/no_limitations_output.txt")

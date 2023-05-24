import tiktoken

from services.openai import OPENAI_MODEL, OpenAiApiService
from services.pinecone import PineconeService

ENCODING = tiktoken.encoding_for_model(OPENAI_MODEL)

h_limit = 3800
s_limit = 3300


def count_tokens(message):
    return len(ENCODING.encode(message))


class PromptGenerator:
    def __init__(self):
        ...

    def retrieve(self, query):
        # Create embeddings for the query
        response = OpenAiApiService().get_embedded(query)
        # Retrieve from Pinecone
        xq = response['data'][0]['embedding']

        # Get relevant contexts
        contexts = PineconeService().search(xq)
        # Build the initial part of our prompt with the retrieved contexts included
        prompt_start = f"""Answer the question based on the context below, don’t justify your answers and if the answer cannot be found write "I don't know. Please contact HR for more information"\n\nContext:\n"""

        # Define the end of the prompt
        prompt_end = (
            f"\n\nQuestion: {query}\nAnswer:"
        )

        tmp_cnt_tokens, doc_lim_num = 0, 0
        tmp_cnt_prompt_start = count_tokens(prompt_start)
        tmp_cnt_prompt_end = count_tokens(prompt_end)

        for i, ctx in enumerate(contexts):
            tmp_cnt_tokens = tmp_cnt_tokens + count_tokens(ctx)
            if tmp_cnt_tokens + tmp_cnt_prompt_start + tmp_cnt_prompt_end > s_limit:
                doc_lim_num = i - 1
                break

        if doc_lim_num == 0:
            prompt = (prompt_start +
                      "\n\n---\n\n".join(contexts) +
                      prompt_end
                      )
        else:
            prompt = (prompt_start +
                      "\n\n---\n\n".join(contexts[:doc_lim_num + 1]) +
                      prompt_end
                      )

        # Return the final prompt
        return prompt

    def with_chatlogs(self, prompt, contexts, log_length=3):
        # If the length of the context exceeds the log_length, take only the last log_length elements
        if len(contexts) > log_length:
            chatlog = contexts[-log_length:]
        # If not, take the whole context
        else:
            chatlog = contexts

        tmp_msg = [{'role': 'system',
                    'content': 'You are an HR assistant that answer only the question that relate to the company. '
                               'You also allow to generate or convert any programing language as you know'}]
        tmp_prompt = [{"role": "user", "content": prompt}]

        tmp_msg_tokens = count_tokens(tmp_msg[0]["content"])
        tmp_prompt_tokens = count_tokens(tmp_prompt[0]["content"])

        # tok = []
        # for i in range(0, len(chatlog)):
        #     tok = tok + [len(encoding.encode(chatlog[i]["content"]))]

        tmp_chat_log_tokens = sum(map(lambda clog: count_tokens(clog['content']), chatlog))

        if tmp_msg_tokens + tmp_prompt_tokens + tmp_chat_log_tokens <= h_limit:
            messages = tmp_msg + chatlog + tmp_prompt
            feed_tokens = tmp_msg_tokens + tmp_prompt_tokens + tmp_chat_log_tokens
            print('Tokens Befor Feed :', tmp_msg_tokens + tmp_prompt_tokens + tmp_chat_log_tokens)
            # print('-'*70)
            # Make the API call to generate a response

        # Return the content of the model's response
        return messages

import ast
import timeit
from typing import NamedTuple
import pytesseract
import openai
from PIL import Image
import os
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# from hidden_constants import OPENAI_API_KEY


class Item(NamedTuple):
    start_text: str
    end_text: str


STORE_DICT = {
    "rema 1000": Item(start_text="serienr", end_text="sum "),
    "obs": Item(start_text="ref", end_text="totalt "),
    "extra": Item(start_text="salgskvittering", end_text="totalt "),
    "unknown": Item(start_text="unknown", end_text="unknown "),
}


def _export_image_text(image_path: str) -> str:
    image = Image.open(image_path)
    return pytesseract.image_to_string(image, lang="nor").lower()


def _make_gpt_prompt(image_path: str) -> str:
    lines = _export_image_text(image_path).split("\n")
    
    store = lines[0]
    if "extra" in store:
        store = "coop extra"
    elif "obs" in store:
        store = "coop obs"
    elif "rema" in store:
        store = "rema 1000"
    else:
        store = "unknown"

    store = STORE_DICT[store]

    start_index = 0
    end_index = len(lines)

    for i, line in enumerate(lines):
        if not start_index and line.startswith(store.start_text):
            start_index = i + 1
        elif not end_index and line.startswith(store.end_text):
            end_index = i
            break

    return ", ".join(
        line
        for line in lines[start_index:end_index]
        if not line.startswith("pant")
        )

def make_gpt_request(image_path: str) -> list[dict[str, str | int]]:
    prompt = _make_gpt_prompt(image_path)
    # print(prompt)
    message_prefix = (
           "Lag et JSON-datasett fra følgende matvarer. Svaret skal være på "
           "formatet {'matvare': {'antall': int, 'vekt': str, 'kategori': str}, "
                      "...}. Defaultverdi for antall skal være 1, vekt skal være 'N/A' og "
           "kategori skal være innenfor kjøleskap, tørrvare eller fryser. Rett "
           "opp i skrivefeil og generaliser navnet på matvaren."
           ) 
    openai.api_key = OPENAI_API_KEY
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"{message_prefix}:\n{prompt}"}],
        temperature=0.0,
    )
    result = completion.choices[0].message.content  # type: ignore
    # result = ast.literal_eval()
    result = result[result.find("{") : result.rfind("}") + 1]
    return result


def main(path) -> str:
    # test_receipts = {
    #     "rema": "src/receipts/receipt.jpg",
    #     "obs": "src/receipts/coop_obs.jpeg",
    # }
    return make_gpt_request(path)


if __name__ == "__main__":
    main()

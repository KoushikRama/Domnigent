from dotenv import load_dotenv
load_dotenv()

import os
import re
from typing import List
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate

import requests
from requests.exceptions import RequestException
import time

DOMAIN_RE = re.compile(r"^[a-z0-9]{1,63}\.[a-z]{2,}$")

def clean_candidates(text:str)-> List[str]:
    raw = re.findall(r"[a-zA-Z0-9]{1,63}\.[a-zA-Z]{2,}", text)

    cleaned=[]
    seen=set()

    for d in raw:
        d =d.lower().strip().strip(",.(){}[]\"'")
        if not DOMAIN_RE.match(d):
            continue
        if d not in seen:
            seen.add(d)
            cleaned.append(d)
    
    return cleaned

def generate_domains(user_prompt: str, max_n: int = 20, tlds: List[str] = None):
    if tlds is None:
        tlds = [".com",".ai",".io",".edu"]
    
    if not os.getenv("HF_TOKEN"):
        raise RuntimeError("Missing Hugging face API Token env variable")
    
    base_llm = HuggingFaceEndpoint(
        repo_id="mistralai/Mistral-7B-Instruct-v0.2",
        temperature=0.9,
        max_new_tokens=350,
        huggingfacehub_api_token=os.getenv("HF_TOKEN")
    )
    llm = ChatHuggingFace(llm=base_llm)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a branding assistant. Generate domain name ideas.\n"
         "Rules:\n"
         "- Output ONLY a numbered list of domains, no commentary.\n"
         "- Use lowercase.\n"
         "- Avoid trademarks.\n"
         "- Prefer 1-2 words, <= 12 characters before the TLD.\n"
         "- Avoid hyphens.\n"
         "- Use only these TLDs: {tlds}\n"
         "- Generate exactly {max_n} items.\n"
         ),
         ("user","{user_prompt}")
    ])

    response = llm.invoke(prompt.format(user_prompt=user_prompt, max_n=max_n, tlds=", ".join(tlds)))
    text = response.content
    domains = clean_candidates(text)

    return domains[:max_n]

def check_available_domains(domain:str ,timeout: float = 6.0, retries: int = 2) -> bool:
    if not DOMAIN_RE.match(domain):
        return False
    
    url = f"https://rdap.org/domain/{domain}"
    headers = {"Accept":"application/rdap+json", "User-Agent": "domain-agent-tutorial/1.0"}

    for attempt in range(retries+1):
        try:
            resp = requests.get(
                url,
                timeout=timeout,
                headers = {"Accept":"application/rdap+json", "User-Agent": "domain-agent-tutorial/1.0"},
                allow_redirects=False
            )
            if resp.status_code == 429:
                # rdap.org rate limit: back off and retry
                time.sleep(1.2 * (attempt + 1))
                continue

            if resp.status_code == 302:
                # Follow to authoritative RDAP server
                loc = resp.headers.get("Location")
                if not loc:
                    return False
                print(domain, "bootstrap", resp.status_code, "loc", resp.headers.get("Location"))
                rr = requests.get(loc, timeout=timeout, headers=headers)

                if rr.status_code == 404:
                    return True
                if rr.status_code == 200:
                    return False

                # Other registry responses => unknown
                return False

            if resp.status_code == 404:
                return False #Not found in RDAP, RDAP doesnt know which registry handles it
            if resp.status_code == 200:
                return False #Found in RDAP, already registered by
            
            return False
        
        except RequestException:
            #Network Errors, assume it as taken
            return False

def check_domains(domains:List[str])-> dict:
    available = []
    taken_or_unknown = []

    for d in domains:
        if check_available_domains(d):
            available.append(d)
        else:
            taken_or_unknown.append(d)
    
    return {
        "available": available,
        "taken_or_unknown": taken_or_unknown
    }
        
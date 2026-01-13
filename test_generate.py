from domain_agent import generate_domains, check_domains

prompt = "Short brandable domain names for potato chips that gives a salty and tangy vibe , prefer .com"
domains = generate_domains(prompt, max_n=20, tlds=[".com"])

results = check_domains(domains)

print("\nGENERATED:")
for d in domains:
    print(" -", d)

print("\nAVAILABLE:")
for d in results["available"]:
    print(" ✅", d)

print("\nTAKEN/UNKNOWN:")
for d in results["taken_or_unknown"]:
    print(" ❌", d)
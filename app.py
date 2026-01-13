import time
import streamlit as st
from dotenv import load_dotenv

from domain_agent import generate_domains, check_domains 

load_dotenv()

st.set_page_config(page_title="Domnigent", page_icon="🌐", layout="centered")

st.title("🌐 Domnigent")
st.caption("Generate domain ideas with Hugging Face and checks availability via RDAP.")

# --- Sidebar controls ---
st.sidebar.header("Settings")
tld_options = [".com", ".io", ".ai", ".org", ".net"]
selected_tlds = st.sidebar.multiselect("Allowed TLDs", tld_options, default=[".com"])
max_n = st.sidebar.slider("How many domains to generate?", min_value=5, max_value=40, value=20, step=5)
check_limit = st.sidebar.slider("How many to check for availability?", min_value=5, max_value=40, value=20, step=5)
st.sidebar.markdown("---")
st.sidebar.write("Tip: .com is crowded — try .io/.ai too.")

# --- Session state for chat-like experience ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- Input ---
user_prompt = st.text_area(
    "Describe what you want",
    placeholder="Example: short brandable domain for an AI robotics portfolio. modern, clean vibe. no hyphens.",
    height=120
)

col1, col2 = st.columns([1, 1])

with col1:
    generate_btn = st.button("✨Generate & Check", use_container_width=True)

with col2:
    clear_btn = st.button("🧹Clear", use_container_width=True)

if clear_btn:
    st.session_state.history = []
    st.rerun()

# --- Main action ---
if generate_btn:
    if not user_prompt.strip():
        st.warning("Please enter your requirements first.")
    elif not selected_tlds:
        st.warning("Select at least one TLD in the sidebar.")
    else:
        with st.spinner("Generating domain ideas..."):
            domains = generate_domains(user_prompt, max_n=max_n, tlds=selected_tlds)

        # Optional: only check first N (keeps it fast + avoids rate limits)
        domains_to_check = domains[:check_limit]

        with st.spinner("Checking availability (RDAP)..."):
            results = check_domains(domains_to_check)

        available = results["available"]
        taken_or_unknown = results["taken_or_unknown"]

        # Save to history
        st.session_state.history.insert(0, {
            "prompt": user_prompt,
            "tlds": selected_tlds,
            "generated": domains_to_check,
            "available": available,
            "taken_or_unknown": taken_or_unknown,
        })

# --- Display results ---
for idx, item in enumerate(st.session_state.history):
    st.markdown("---")
    st.subheader(f"Request #{len(st.session_state.history)-idx}")
    st.write(f"**Prompt:** {item['prompt']}")
    st.write(f"**TLDs:** {', '.join(item['tlds'])}")

    st.write("### ✅ Available")
    if item["available"]:
        for d in item["available"]:
            st.write(d)
    else:
        st.info("No available domains found in this batch. Try different keywords or add more TLDs.")

    with st.expander("Show taken/unknown + generated list"):
        st.write("**Generated (checked):**")
        st.write("\n".join([f"- {d}" for d in item["generated"]]))

        st.write("**Taken / Unknown:**")
        st.write("\n".join([f"- {d}" for d in item["taken_or_unknown"]]))

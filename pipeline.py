from agents import build_search_agent, writer_chain, critic_chain
from tools import extract_http_urls, scrape_url


def _agent_messages_to_text(result: dict) -> str:
    """Join all string message parts so tool outputs (with URLs) are not dropped."""
    parts: list[str] = []
    for m in result.get("messages", []):
        content = getattr(m, "content", None)
        if isinstance(content, str) and content.strip():
            parts.append(content.strip())
        elif isinstance(content, list):
            text_bits = [str(x) for x in content if x]
            if text_bits:
                parts.append("\n".join(text_bits))
    return "\n\n---\n\n".join(parts) if parts else ""


def run_research_pipeline(topic: str) -> str:

    state = {}
    
    #  step 1:Search agent working 
    print("\n"+" ="*50)
    print("step1: search agent is working...")
    print("="*50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages" : [("user", f"find recent, reliable and detailed information about: {topic}")]
    })

    state["search_results"] = _agent_messages_to_text(search_result)

    print("\n search result ", state["search_results"])

    # step 2: scrape top URLs deterministically (avoids Groq tool_use_failed on bad LLM URLs)
    print("\n"+" ="*50)
    print("step 2: Scraping top resources from search URLs...")
    print("="*50)

    urls = extract_http_urls(state["search_results"])
    scraped_chunks: list[str] = []
    for url in urls[:3]:
        chunk = scrape_url.invoke({"url": url})
        if isinstance(chunk, str) and chunk.strip() and not chunk.startswith("Could not scrape URL"):
            scraped_chunks.append(f"=== {url} ===\n{chunk}")
    state["scraped_content"] = (
        "\n\n".join(scraped_chunks)
        if scraped_chunks
        else "No pages could be scraped; using search snippets only."
    )

    print("\n scraped content:  \n", state["scraped_content"])

    # step 3: Writer agent
    print("\n"+" ="*50)
    print("step 3: Writer agent is drafting the report...")
    print("="*50)

    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic" : topic,
        "research" : research_combined
    })

    print("\n Final Report\n",state['report'])

    #critic report 

    print("\n"+" ="*50)
    print("step 4 - critic is reviewing the report ")
    print("="*50)

    state["feedback"] = critic_chain.invoke({
        "report":state['report']
    })

    print("\n critic report \n", state['feedback'])

    return state



if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    run_research_pipeline(topic)
"""
MedlinePlus Medical Information Tool
Fetches reliable health information from the US National Library of Medicine API.
No API key required.
"""

import requests
from langchain.tools import tool
import json


MEDLINEPLUS_URL = "https://wsearch.nlm.nih.gov/ws/query"


def search_medlineplus(query: str, max_results: int = 3) -> str:
    """
    Search MedlinePlus for health information and return formatted results.
    """
    try:
        params = {
            "db": "healthTopics",
            "term": query,
            "retmax": max_results,
            "rettype": "brief"
        }
        resp = requests.get(MEDLINEPLUS_URL, params=params, timeout=10)
        resp.raise_for_status()

        from xml.etree import ElementTree as ET
        root = ET.fromstring(resp.content)

        results = []
        for doc in root.findall(".//document"):
            title_el = doc.find(".//content[@name='title']")
            snippet_el = doc.find(".//content[@name='FullSummary']")
            url_attr = doc.get("url", "")

            title = title_el.text if title_el is not None else "Unknown"
            snippet = snippet_el.text if snippet_el is not None else ""

            # Clean HTML tags from snippet
            import re
            snippet = re.sub(r"<[^>]+>", "", snippet or "").strip()
            snippet = snippet[:400] + "..." if len(snippet) > 400 else snippet

            results.append(f"**{title}**\n{snippet}\nSource: {url_attr}")

        if results:
            header = (
                "\n⚠️ *This information is for educational purposes only. "
                "Always consult a qualified healthcare professional for medical advice.*\n\n"
            )
            return header + "\n\n---\n\n".join(results)
        else:
            return (
                f"No specific results found on MedlinePlus for '{query}'. "
                "Try a different search term or visit https://medlineplus.gov"
            )

    except requests.exceptions.RequestException as e:
        return f"Unable to reach MedlinePlus at this time. Error: {str(e)}"
    except Exception as e:
        return f"Error processing medical information: {str(e)}"


@tool
def medical_info_lookup(query: str) -> str:
    """
    Look up reliable medical and health information from MedlinePlus.
    Use this tool when the user asks about diseases, symptoms, medications,
    treatments, or general health topics.

    Args:
        query: The health topic, symptom, disease, or medication to search for.

    Returns:
        Reliable health information with source citations.
    """
    return search_medlineplus(query)

import google.generativeai as genai
import os

def generate_pitch(org_name, risk_score, locations, total_ips, open_ports_summary, cve_details, services_summary, ssl_issues, tone, focus_area, api_key):
    """
    Generates a personalized sales pitch using Google Gemini.
    """
    if not api_key:
        return "⚠️ Please provide a valid Gemini API key in the sidebar."
        
    try:
        genai.configure(api_key=api_key)
        # Using the flash model as recommended for fast, cost-effective text generation
        model = genai.GenerativeModel('gemini-3.1-flash-lite')
        
        system_prompt = """You are a senior cybersecurity sales consultant. 
Generate a compelling, personalized sales outreach email for a prospect 
based on their actual network security exposure data from Shodan scans.

Rules:
- Be professional but urgent — they have real vulnerabilities
- Reference SPECIFIC findings (CVEs, ports, products, locations)
- DO NOT fabricate vulnerabilities not in the data
- Include a clear call-to-action
- Keep under 200 words
- Suggest 2-3 specific services that could help
"""

        user_prompt = f"""
Generate a sales pitch for the following organization:

**Organization:** {org_name}
**Risk Score:** {risk_score}/100
**Location(s):** {locations}
**Total Exposed IPs:** {total_ips}
**Open Ports:** {open_ports_summary}
**Known Vulnerabilities:**
{cve_details}
**Exposed Services:**
{services_summary}
**SSL Issues:**
{ssl_issues}

Tone: {tone}
Focus Area: {focus_area}
"""
        
        response = model.generate_content([system_prompt, user_prompt])
        return response.text
        
    except Exception as e:
        return f"❌ Error generating pitch: {str(e)}\n\nFallback Template:\nHi IT Team at {org_name},\nWe noticed {total_ips} exposed IPs with a high risk score of {risk_score}. Let's chat."

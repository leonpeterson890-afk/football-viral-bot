import os
from groq import Groq

def generate_viral_script(article):
    # 1. Konfigirasyon kliyan an (Asire w ou mete vrè kle pa w la)
    client = Groq(api_key="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")
    
    # Nou rale tit ak deskripsyon, epi nou asire n yo pa gen karaktè ki ka fè Python fache
    tit = article.get("title", "Nouvèl foutbòl")
    content = article.get("description", "")
    
    # 2. Nou prepare prompt la (Mwen retire aksan yo nan pati kòd la sèlman pou evite konfli)
    # Men nan repons lan, AI a ap toujou ekri ak bèl aksan Kreyòl.
    prompt_text = (
        f"Ekri 3 script viral separe pou nouvel sa a: {tit}\n"
        f"Detay: {content}\n\n"
        "Foma repons lan dwe konsa:\n"
        "1. KREYOL AYISYEN (Ton: Cho/Popile)\n"
        "2. FRANCAIS (Ton: Journalistique)\n"
        "3. ENGLISH (Ton: Viral/Hype)\n"
        "Itilize anpil emoji foutbol!"
    )

    try:
        # 3. Rele AI a
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": "Ou se yon kreyatè kontni spòtif miltiling ki pale Kreyòl Ayisyen, Fransè, ak Anglè."
                },
                {
                    "role": "user", 
                    "content": prompt_text
                }
            ],
            temperature=0.8
        )
        
        # Nou asire n ke repons lan tounen yon string ki pwòp
        resilta = completion.choices[0].message.content
        return resilta

    except Exception as e:
        # Si gen yon erè, n ap voye yon mesaj ki senp
        return f"Erè AI: Gen yon ti pwoblèm nan kominikasyon ak sèvè a."
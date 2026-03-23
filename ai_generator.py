# Groq client (mete kle w nan .env epi li ak os.getenv si sa nesesè)
client = Groq(api_key=os.getenv("GROQ_API_KEY", "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"))

prompt_text = (
    f"Ekri 3 script viral separe pou nouvel sa a: {title}\n"
    f"Detay: {content}\n\n"
    "Foma repons lan dwe konsa:\n"
    "1. KREYOL AYISYEN (Ton: Cho/Popile)\n"
    "2. FRANCAIS (Ton: Journalistique)\n"
    "3. ENGLISH (Ton: Viral/Hype)\n"
    "Itilize anpil emoji foutbol!"
)

try:
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Ou se yon kreyatè kontni spòtif miltiling ki pale Kreyòl Ayisyen, Fransè, ak Anglè."},
            {"role": "user", "content": prompt_text}
        ],
        temperature=0.8
    )
    resilta = completion.choices[0].message.content
    return resilta
except Exception as e:
    return f"Erè AI: {e}"

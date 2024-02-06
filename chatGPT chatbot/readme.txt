pre spustenie bota si otvor command prompt a dojdi do adresára tohto priečinku. potom napíš príkaz:
python chatgpt.py "(sem napíš otázku ktorú sa bopython chatgpt.py ta chceš spýťať)"

Momentálne bot funguje len s priečinkom tutoriál ktorý je zadefinovaný v kóde avšak dá sa priložiť aj celý fajnwork ak sa vloží do tohto priečinka a taktiež sa uvedie lokácia v kóde.


template = """Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer. 
Use three sentences maximum and keep the answer as concise as possible. 
Always say "thanks for asking!" at the end of the answer. 
{context}
Question: {question}
Helpful Answer:"""
QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
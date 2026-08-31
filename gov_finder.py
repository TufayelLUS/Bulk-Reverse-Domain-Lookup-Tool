# Support script to help separate important sites from the collected list
print("Generating domains...")
domains = open('collected.txt', mode='r', encoding='utf-8').read().split('\n')
with open('input.txt', mode='w+', encoding='utf-8') as f:
    for link in domains:
        if any(x in link for x in ['.gov.', '.go.', '.gos.', '.gouv.', '.gob.', '.gop.', '.gog.', '.gkp.', '.gok.', '.bel.', '.edu.', '.cnr.', '.gub.', '.gv.', '.unb.', '.ufma.']) or any(link.endswith(x) for x in ['.gov', '.edu', '.mil', '.int']):
            f.write(f"{link}\n")
        
print("Done")

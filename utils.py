from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

def deduplicate_wishes(wishes, threshold=0.8):
    """
    O‘xshash tilaklarni guruhlash.
    Har bir guruh uchun eng qisqa tilak representative bo‘ladi.
    """
    if not wishes:
        return []

    embeddings = model.encode(wishes, convert_to_tensor=True)

    groups = []
    used = set()

    for i, wish in enumerate(wishes):
        if i in used:
            continue
        group = [wish]
        used.add(i)

        for j in range(i + 1, len(wishes)):
            if j in used:
                continue
            sim = util.cos_sim(embeddings[i], embeddings[j]).item()
            if sim > threshold:
                group.append(wishes[j])
                used.add(j)

        # eng qisqa tilakni representative sifatida olish
        representative = min(group, key=len)
        groups.append((representative, group))

    return groups

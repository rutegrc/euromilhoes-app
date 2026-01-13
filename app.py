import streamlit as st
import csv, random
from collections import Counter
from statistics import mean

st.set_page_config(page_title="Euromilhões Inteligente", layout="centered")

HIST = "historico.csv"

@st.cache_data
def carregar_dados():
    import pandas as pd

@st.cache_data(ttl=86400)  # atualiza 1x por dia

def carregar_dados():
    url = "https://raw.githubusercontent.com/datasets/euromillions/master/data/euromillions.csv"

    df = pd.read_csv(url)

    chaves, nums, stars = set(), [], []

    for _, r in df.iterrows():
        nums_chave = sorted([r[f"Ball {i}"] for i in range(1,6)])
        stars_chave = sorted([r["Lucky Star 1"], r["Lucky Star 2"]])

        chave = tuple(nums_chave + stars_chave)
        chaves.add(chave)
        nums.extend(nums_chave)
        stars.extend(stars_chave)

    return chaves, Counter(nums), Counter(stars)

def gerar_chave():
    return tuple(sorted(random.sample(range(1,51), 5)) +
                 sorted(random.sample(range(1,13), 2)))

def score(chave, fn, fs, modo):
    nums, stars = chave[:5], chave[5:]
    s = sum(fn[n] for n in nums) + sum(fs[e] for e in stars) * 2

    pares = sum(n % 2 == 0 for n in nums)
    altos = sum(n > 25 for n in nums)
    if pares in (2,3): s += 15
    if altos in (2,3): s += 15

    seq = sum(nums[i+1] == nums[i] + 1 for i in range(4))
    s -= seq * 6

    if abs(stars[0] - stars[1]) <= 1:
        s -= 6

    if modo == "conservador":
        s += sum(fn[n] > mean(fn.values()) for n in nums) * 5
    elif modo == "agressivo":
        s += sum(fn[n] < mean(fn.values()) for n in nums) * 6

    return s

# ---------------- UI ----------------
st.title("🎯 Euromilhões Inteligente")

modo = st.radio(
    "Escolhe o modo de jogo:",
    ["conservador", "equilibrado", "agressivo"],
    index=1
)

if st.button("Gerar Top 10 Chaves"):
    historico, fn, fs = carregar_dados()
    resultados = []

    with st.spinner("A calcular..."):
        for _ in range(40000):
            c = gerar_chave()
            if c in historico:
                continue
            resultados.append((score(c, fn, fs, modo), c))

    resultados.sort(reverse=True)
    top = resultados[:10]

    st.success("Chaves geradas com sucesso!")

    for i, (s, c) in enumerate(top, 1):
        st.write(
            f"**{i:02d}.** {c[:5]} ⭐ {c[5:]}  \nScore: `{s}`"
        )

import streamlit as st
import random
import pandas as pd
import csv
from collections import Counter
from statistics import mean

st.set_page_config(page_title="Jogos Santa Casa – Inteligente", layout="centered")

# =========================================================
# ---------------- EUROMILHÕES -----------------------------
# =========================================================
@st.cache_data(ttl=86400)
def carregar_euromilhoes():
    chaves, nums, stars = set(), [], []

    try:
        url = "https://raw.githubusercontent.com/datasets/euromillions/master/data/euromillions.csv"
        df = pd.read_csv(url)

        for _, r in df.iterrows():
            nums_chave = sorted([r[f"Ball {i}"] for i in range(1,6)])
            stars_chave = sorted([r["Lucky Star 1"], r["Lucky Star 2"]])

            chave = tuple(nums_chave + stars_chave)
            chaves.add(chave)
            nums.extend(nums_chave)
            stars.extend(stars_chave)

    except:
        with open("historico.csv", newline="") as f:
            r = csv.DictReader(f)
            for row in r:
                nums_chave = sorted(int(row[f"n{i}"]) for i in range(1,6))
                stars_chave = sorted([int(row["e1"]), int(row["e2"])])
                chave = tuple(nums_chave + stars_chave)
                chaves.add(chave)
                nums.extend(nums_chave)
                stars.extend(stars_chave)

    return chaves, Counter(nums), Counter(stars)

def gerar_euromilhoes():
    return tuple(sorted(random.sample(range(1,51), 5)) +
                 sorted(random.sample(range(1,13), 2)))

def score_euro(chave, fn, fs, modo):
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


# =========================================================
# ---------------- TOTOloto -------------------------------
# =========================================================
@st.cache_data(ttl=86400)
def carregar_totoloto():
    chaves, nums, stars = set(), [], []

    try:
        url = "https://www.lottery.co.uk/totoloto/results/download"
        df = pd.read_csv(url)

        for _, r in df.iterrows():
            nums_chave = sorted([int(r[f"Ball{i}"]) for i in range(1,6)])
            star = int(r["LuckyBall"])
            chave = tuple(nums_chave + [star])
            chaves.add(chave)
            nums.extend(nums_chave)
            stars.append(star)

    except:
        with open("historico_totoloto.csv", newline="") as f:
            r = csv.DictReader(f)
            for row in r:
                nums_chave = sorted(int(row[f"n{i}"]) for i in range(1,6))
                star = int(row["e1"])
                chave = tuple(nums_chave + [star])
                chaves.add(chave)
                nums.extend(nums_chave)
                stars.append(star)

    return chaves, Counter(nums), Counter(stars)

def gerar_totoloto():
    return tuple(sorted(random.sample(range(1,50), 5)) + [random.randint(1,13)])

def score_toto(chave, fn, fs, modo):
    nums, star = chave[:5], chave[5]
    s = sum(fn[n] for n in nums) + fs[star] * 2

    pares = sum(n % 2 == 0 for n in nums)
    altos = sum(n > 25 for n in nums)
    if pares in (2,3): s += 10
    if altos in (2,3): s += 10

    seq = sum(nums[i+1] == nums[i] + 1 for i in range(4))
    s -= seq * 6

    if modo == "conservador":
        s += sum(fn[n] > mean(fn.values()) for n in nums) * 4
    elif modo == "agressivo":
        s += sum(fn[n] < mean(fn.values()) for n in nums) * 5

    return s


# =========================================================
# ---------------- INTERFACE -------------------------------
# =========================================================
st.title("🎯 Jogos Santa Casa – Inteligente")

jogo = st.selectbox(
    "Escolhe o jogo:",
    ["Euromilhões", "Totoloto"]
)

modo = st.radio(
    "Modo de jogo:",
    ["conservador", "equilibrado", "agressivo"],
    index=1
)

if st.button("Gerar Top 3 Chaves"):
    resultados = []

    with st.spinner("A calcular..."):
        if jogo == "Euromilhões":
            hist, fn, fs = carregar_euromilhoes()
            for _ in range(40000):
                c = gerar_euromilhoes()
                if c not in hist:
                    resultados.append((score_euro(c, fn, fs, modo), c))

            resultados.sort(reverse=True)
            for i, (s, c) in enumerate(resultados[:3], 1):
                st.write(f"**{i:02d}.** {c[:5]} ⭐ {c[5:]}  \nScore: `{s}`")

        else:
            hist, fn, fs = carregar_totoloto()
            for _ in range(30000):
                c = gerar_totoloto()
                if c not in hist:
                    resultados.append((score_toto(c, fn, fs, modo), c))

            resultados.sort(reverse=True)
            for i, (s, c) in enumerate(resultados[:3], 1):
                st.write(f"**{i:02d}.** {c[:5]} ⭐ {c[5]}  \nScore: `{s}`")

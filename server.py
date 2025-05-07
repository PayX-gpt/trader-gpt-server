from flask import Flask, request, Response
import openai
import traceback
import json
import re

app = Flask(__name__)
import os
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ Leitura da memória comportamental do trader
with open("memoria_trader.txt", "r", encoding="utf-8") as f:
    MEMORIA_TRADER = f.read()
# 🔧 Prompt base com instrução para retorno numérico de setup
PROMPT = """
🧠 MEMÓRIA DO TRADER GPT — VERSÃO 3.5 OTIMIZADA

Você é o trader mais assertivo do planeta. Opera com lógica probabilística, price action institucional e comportamento humano de mercado. Sua missão é entregar diagnósticos com **precisão estatística real**, baseados apenas nos dados brutos fornecidos.

---

📊 ESTRUTURA DE ANÁLISE (HIERARQUIA):

• D1 → tendência principal (peso máximo)  
• H4 → confirma continuidade ou reversão  
• H1 → zonas de suporte, resistência, armadilhas  
• M15 → apenas para identificar **padrão técnico claro de entrada**

⚠️ **M15 nunca se sobrepõe aos tempos maiores**. Só valide entradas se D1, H4 e H1 estiverem alinhados.

---

📏 REGRA FUNDAMENTAL: DISTÂNCIA MÍNIMA ENTRE ENTRADA, STOP E GAIN (OBRIGATÓRIA)

Antes de validar qualquer entrada, aplique os cálculos abaixo com base no valor da entrada:

• STOP mínimo: **0,25% do valor da entrada**
  - Compra: stop = entrada − (entrada × 0.0025)
  - Venda: stop = entrada + (entrada × 0.0025)

• GAIN mínimo: **0,32% do valor da entrada**
  - Compra: gain = entrada + (entrada × 0.0032)
  - Venda: gain = entrada − (entrada × 0.0032)

⚠️ Se qualquer uma das distâncias for **menor que o mínimo**, a entrada deve ser automaticamente **recusada**.

---

🔎 CHECKLIST DE VALIDAÇÃO DA ENTRADA

Só valide a entrada se TUDO abaixo for verdadeiro:

✔ D1, H4 e H1 em confluência  
✔ Candle no M15 com padrão técnico válido  
✔ R/R ≥ 1.2  
✔ Probabilidade ≥ 56%  
✔ STOP ≥ 0.25% da entrada  
✔ GAIN ≥ 0.32% da entrada  
✔ Nenhuma zona de resistência (em compra) ou suporte (em venda) muito próxima  
✔ Volume e contexto favorecem a direção  
✔ Padrão técnico bem formado matematicamente

❌ Se qualquer item for falso → recuse a entrada.

---


📊 ESTRATÉGIAS DE PRICE ACTION PURO — 20 PADRÕES COM VALIDAÇÃO MATEMÁTICA

Utilize apenas os dados OHLC dos timeframes D1, H4, H1 e M15 para identificar os padrões abaixo.
Nunca use intuição visual. Use regras matemáticas com base em proporção e repetição.

Cada estratégia possui taxa de acerto média estimada com R/R ≥ 1.2.

⸻

1. Rejeição Tripla em Suporte com Pin Bar (≈65%)

• 3 toques no mesmo nível (±0.1%)
• Candle com sombra inferior ≥ 2× corpo e fechamento acima da metade

⸻

2. Rejeição Tripla em Resistência com Engolfo de Baixa (≈63%)

• 3 toques no topo (±0.1%)
• Candle engolfa o anterior com corpo claro de baixa

⸻

3. Falsa Quebra de Resistência com Reversão (≈62%)

• Rompe topo anterior, mas fecha abaixo do nível
• Sombra superior longa

⸻

4. Falsa Quebra de Suporte com Reversão (≈61%)

• Rompe fundo anterior, mas fecha acima
• Sombra inferior longa

⸻

5. Engolfo de Reversão Após 3 Candles Direcionais (≈58%)

• 3 candles de mesma direção
• Candle seguinte engolfa no sentido oposto

⸻

6. Inside Bar em Zona Chave (≈57%)

• Candle interno totalmente dentro do anterior
• Próximo candle rompe a barra-mãe

⸻

7. Falso Rompimento de Inside Bar (≈59%)

• Rompe a barra-mãe para um lado, mas fecha no lado oposto com força

⸻

8. Retração de 50% com Confirmação Técnica (≈60%)

• Candle de impulso
• Próximo candle retrai até 50% do corpo e forma Pin Bar ou Engolfo

⸻

9. Consolidação Estreita com Rompimento (≈63%)

• 3–6 candles pequenos com máximas e mínimas similares
• Rompimento com candle de corpo ≥ 60% do range

⸻

10. Topo Duplo com Rejeição (≈64%)

• 2 toques no mesmo topo com rejeição (sombra longa ou engolfo de baixa)

⸻

11. Fundo Duplo com Rejeição (≈64%)

• 2 toques no mesmo fundo com candle de rejeição (Pin Bar ou Engolfo de Alta)

⸻

12. Candle Direcional Após Compressão (≈62%)

• 3 candles com range pequeno
• Próximo candle tem range 2x maior e direção clara

⸻

13. Sequência de Mínimas Mais Altas (≈60%)

• 3 candles consecutivos com mínimas ascendentes
• Confirmação com candle de força (corpo ≥ 70%)

⸻

14. Sequência de Máximas Mais Baixas (≈60%)

• 3 candles com máximas descendentes
• Confirmação com candle de baixa forte

⸻

15. Falha de Continuação Após Rompimento (≈61%)

• Rompe resistência/suporte
• Falha em fechar fora da zona e forma candle técnico de reversão

⸻

16. Marubozu Após Candle de Indecisão (≈59%)

• Candle pequeno (Doji ou Spinning Top)
• Seguinte é Marubozu com corpo ≥ 90% do range

⸻

17. Rejeição com Sombra Superior Longa (≈57%)

• Sombra superior ≥ 2× corpo
• Fechamento abaixo da metade

⸻

18. Rejeição com Sombra Inferior Longa (≈57%)

• Sombra inferior ≥ 2× corpo
• Fechamento acima da metade

⸻

19. Reversão Após Terceiro Toque na Mesma Zona (≈66%)

• Zona tocada 3 vezes (±0.1%)
• Candle técnico no terceiro toque (Pin Bar ou Engolfo)

⸻

20. Rompimento com Pullback e Continuação (≈64%)

• Rompe suporte/resistência
• Retorna (pullback) à zona rompida
• Forma candle técnico de continuação

⸻

📌 Todas as estratégias devem ser validadas com:
	•	Cálculo de proporção exata entre corpo e sombras (OHLC)
	•	Validação da zona de suporte/resistência por repetição (≥ 2 ou 3 toques)
	•	Candle de entrada apenas no mais recente do M1
	•	Contexto maior favorável (D1, H4, H1)


👉 Use essas taxas como base inicial e **ajuste conforme o contexto real**.  
Exemplo: Engolfo com tendência forte e volume crescente = 60% → ajusta para 68%.

📌 NÃO invente padrões. Use apenas os listados, com base **matemática** (corpo/sombra/range).

---

📐 ANÁLISE VISUAL POR OHLC (OBRIGATÓRIA):

Simule candles usando:

• Corpo = |close − open|  
• Sombra superior = |high − max(open, close)|  
• Sombra inferior = |min(open, close) − low|

Valide padrões:

• Pin Bar = corpo < 30% do range + sombra ≥ 2× corpo  
• Engolfo = corpo engole totalmente o anterior  
• Marubozu = corpo ≥ 90% do range total

❗ NÃO use “intuição visual”. Use cálculo exato.

---

📦 EXECUÇÃO E FORMATO DE RESPOSTA (OBRIGATÓRIO)

• Sempre entrar **a mercado**, usando o candle mais recente de m1, o close do candle mis recente  
• NÃO usar ordens pendentes  
• NÃO fazer suposições sobre candles futuros  
• Use os valores reais dos candles e calcule entrada, stop e gain com precisão

Se houver entrada válida:
{
  "setup": 1 ou 2,
  "entrada": 1.23456,
  "stop": 1.22890,
  "gain": 1.24120,
  "probabilidade": 62
}

Se NÃO houver entrada válida:
{
  "setup": "SEM ENTRADA VÁLIDA",
  "entrada": 1.23456,
  "stop": 1.22890,
  "gain": 1.24120,
  "probabilidade": 62
}

⚠️ Campo "setup" deve ser:
• 1 = COMPRA  
• 2 = VENDA  
Nunca use texto no lugar de número, exceto quando **explicitamente não houver entrada válida**.

---

📛 PROIBIÇÕES ABSOLUTAS:

🚫 NÃO escreva nada fora do JSON  
🚫 NÃO explique  
🚫 NÃO use linguagem natural  
🚫 NÃO arredonde os valores  
🚫 NÃO valide entradas com SL ou TP abaixo dos percentuais mínimos

---

DADOS:
{dados}"""

@app.route("/analise", methods=["POST"])
def analise():
    try:
        raw_data = request.data.decode('utf-8', errors='ignore')
        print("RAW RECEIVED:", raw_data)

        try:
            raw_data = raw_data[:raw_data.rfind("}")+1]
            json_bruto = json.loads(raw_data)
            dados_mercado = json.dumps(json_bruto["dados"], ensure_ascii=False)
        except Exception as e:
            print("ERRO JSON:", str(e))
            return Response(json.dumps({"erro": f"Erro ao decodificar JSON: {str(e)}"}), status=400, mimetype="application/json")

        print("DADOS MERCADO:", dados_mercado)

        if len(dados_mercado.strip()) < 20:
            return Response(json.dumps({"erro": "Dados muito curtos para análise."}), status=400, mimetype="application/json")

        prompt_final = MEMORIA_TRADER + "\n\n" + PROMPT.replace("{dados}", dados_mercado)
        resposta = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um analista técnico de mercado."},
                {"role": "user", "content": prompt_final}
            ],
            temperature=0.4,
            max_tokens=500
        )

        conteudo = resposta.choices[0].message.content
        print("GPT RESPONSE:", conteudo)

        match = re.search(r"\{.*\}", conteudo, re.DOTALL)
        if match:
            json_limpo = match.group(0)

            try:
                json_obj = json.loads(json_limpo)

                # ✅ Corrige o setup para número real
                setup_raw = str(json_obj.get("setup", "")).strip().lower()
                if setup_raw in ["1", "compra"]:
                    json_obj["setup"] = 1
                elif setup_raw in ["2", "venda"]:
                    json_obj["setup"] = 2
                else:
                    return Response(json.dumps({"erro": f"Setup inválido recebido: {setup_raw}"}), status=400, mimetype="application/json")

                return Response(json.dumps(json_obj), status=200, mimetype="application/json")

            except Exception as err_json:
                print("Erro ao validar JSON:", err_json)
                return Response(json.dumps({"erro": "Formato inválido após GPT"}), status=500, mimetype="application/json")

        else:
            return Response(json.dumps({"erro": "GPT não retornou JSON válido"}), status=500, mimetype="application/json")

    except Exception as e:
        traceback.print_exc()
        return Response(json.dumps({"erro": str(e)}), status=500, mimetype="application/json")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

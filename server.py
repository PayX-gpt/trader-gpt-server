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


🎯 ESTRATÉGIAS TÉCNICAS (REGRAS MATEMÁTICAS + TAXA BASE)

Use apenas os candles fornecidos (OHLC) para detectar os padrões abaixo. A validação deve ser 100% matemática e seguir as definições exatas.

Cada padrão possui uma taxa de acerto base. Ajuste a probabilidade final conforme contexto de mercado (volume, tendência, confluência entre timeframes).

⸻

1. Pin Bar em Suporte/Resistência — 65%
• Corpo < 30% do range total
• Sombra (superior ou inferior) ≥ 2× corpo
• Ocorre após rejeição em zona de suporte ou resistência com múltiplos toques (mín. 3 candles anteriores)

⸻

2. Engolfo de Alta/Baixa após Pullback — 60%
• Corpo do candle atual engole completamente o corpo do anterior
• Direção contrária à do candle anterior
• Ideal após retração de 1 a 3 candles contra a tendência

⸻

3. Martelo ou Inverted Hammer em Tendência — 58%
• Corpo pequeno (< 30% do range total)
• Uma sombra longa (≥ 2× corpo), com a outra pequena ou ausente
• Contexto de tendência prévia (mín. 3 candles)

⸻

4. Doji com Volume em Nível-Chave — 55%
• Corpo ≈ 0 (|open − close| muito pequeno)
• Sombra superior e inferior presentes
• Volume crescente, ou doji aparece após compressão com breakout

⸻

5. Triângulo Ascendente/Descendente com Breakout — 62%
• Suporte ou resistência horizontal + outra linha convergente
• Mín. 3 toques em cada linha
• Candle de rompimento com corpo ≥ 60% do range total + volume elevado

⸻

6. Bandeira de Alta/Baixa com Continuação — 60%
• Movimento explosivo anterior (mín. 3 candles fortes)
• Seguido de canal estreito com leve inclinação oposta
• Rompimento com corpo ≥ 50% da bandeira

⸻

7. OCO ou OCO Invertido em Topos/Fundos — 65%
• Três picos ou vales: o do meio mais alto/baixo que os laterais
• Linha de pescoço bem definida (horizontal ou inclinada)
• Rompimento com candle de corpo forte (≥ 60% do range)

⸻

8. Divergência RSI com Reversão Confirmada — 57%
• Preço forma novo topo/fundo
• RSI não confirma (divergência)
• Confirmação com candle técnico (engolfo, martelo, etc.)

⸻

9. Breakout de Consolidação com Volume Acima da Média — 63%
• Range lateral estável (máx. 3% de oscilação)
• Candle de rompimento com:
	•	Corpo ≥ 50% do range
	•	Volume ≥ 2× média dos 3 candles anteriores

⸻

10. Retração de Fibonacci 61.8% com Confirmação — 59%
• Preço retrai até zona de 61.8% (calculada sobre movimento anterior)
• Confirmação com candle técnico na zona (pin bar, engolfo, etc.)

⸻

11. Cruzamento de Médias Móveis (MA50/MA200) com Volume — 60%
• MA50 cruza MA200 com inclinação positiva (compra) ou negativa (venda)
• Candle técnico se forma logo após o cruzamento
• Volume crescente reforça a direção

⸻

12. Bollinger Bands com Reversão + Volume — 58%
• Preço toca ou ultrapassa banda superior/inferior
• Candle de reversão com sombra longa e fechamento dentro das bandas
• Volume alto ou divergência de força

⸻

13. ADX acima de 25 com Confirmação de Tendência — 61%
• ADX > 25 indicando força direcional
• Entrada ocorre a favor da tendência, com candle forte de confirmação (marubozu ou engolfo)

⸻

14. MACD com Cruzamento e Histograma Crescente — 59%
• Linhas MACD se cruzam na direção da tendência
• Histograma mostra 2 ou mais candles de crescimento
• Candle de entrada técnico (engolfo, marubozu)

⸻

15. Estocástico com Divergência + Candle Técnico — 56%
• Estocástico marca sobrecompra/sobrevenda
• Divergência com o preço (ex: novo fundo no preço, mas não no oscilador)
• Confirmação com candle técnico (pin bar, doji, engolfo)

⸻

16. Parabolic SAR com Confirmação de Direção — 60%
• Pontos do SAR mudam de posição (abaixo → acima ou vice-versa)
• Candle de entrada confirma a nova direção
• Contexto favorável (volume, tendência maior)

⸻

17. Volume Clímax + Reversão Técnica — 62%
• Candle com volume extremamente alto em comparação com os 5 anteriores
• Candle seguinte mostra reversão clara (engolfo, pin bar, etc.)

⸻

18. Gap de Fuga com Continuação de Tendência — 64%
• Gap aparece na direção da tendência atual
• Candle seguinte não fecha o gap e continua a direção
• Volume crescente ou igual ao candle de gap

⸻

19. Estrela da Manhã / Estrela da Noite — 57%
• Três candles consecutivos:
	•	1º = forte (baixa ou alta)
	•	2º = candle pequeno (gap)
	•	3º = candle forte em direção contrária
• Gap claro entre o 1º e o 2º candle

⸻

20. Marubozu com Volume e Continuação — 56%
• Corpo ≥ 90% do range
• Sem sombras ou sombras muito pequenas
• Volume superior à média dos últimos 3 candles


⸻

📌 Regras para cada padrão:
	•	Use apenas cálculos baseados nos valores open, high, low, close
	•	Simule proporções com:
• corpo = |close − open|
• sombra sup. = |high − max(open, close)|
• sombra inf. = |min(open, close) − low|
	•	NÃO use interpretação visual
	•	Valide o padrão apenas se os valores batem com as proporções exigidas

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

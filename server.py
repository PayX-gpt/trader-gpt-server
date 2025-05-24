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
🧠 TRADER GPT — DECISÃO TÉCNICA FINAL

Você é um trader altamente técnico e objetivo. Sua função é **avaliar o contexto estrutural completo do mercado** com base em múltiplos timeframes (D1, H4, H1, M15) e indicar **apenas setups de alta confiança estatística**, com base no comportamento dos candles e price action institucional.

⚠️ As validações técnicas básicas já foram feitas. Sua única responsabilidade agora é avaliar a **estrutura do mercado** e tomar uma decisão assertiva, com base:

- Padrões de reversão ou continuação
- Zonas de suporte/resistência e rejeição
- Confluência entre os timeframes
- Estrutura de tendência ou consolidação

---

📊 O que você deve identificar:

• Se há um setup claro com base nas estruturas listadas
• Se o candle M1 atual é apropriado para entrada (marubozu, engolfo, pin bar)
• Se existe suporte/resistência técnica para posicionamento do stop e gain
• Se o trade possui R/R visualmente favorável (acima de 1.2)

---

📊 ESTRATÉGIAS DE PRICE ACTION PURO — 20 PADRÕES COM VALIDAÇÃO MATEMÁTICA

Utilize apenas os dados OHLC dos timeframes H1 e M15 para identificar os padrões abaixo.
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

---

📦 FORMATO DA RESPOSTA:

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
  "probabilidade": 62,
  "motivo": "",
  "checklist": {}
}


⚠️ Campo "setup" deve ser:
• 1 = COMPRA  
• 2 = VENDA  
Nunca use texto no lugar de número, exceto quando **explicitamente não houver entrada válida**.
Se e apenas se não setup = SEM ENTRADA VÁLIDA, explique o motivo e especifique qual regra descumprida ou quais regras descumprida.
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

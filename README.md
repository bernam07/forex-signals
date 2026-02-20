# MT5 XGBoost Martingale Trading Bot

Um bot de trading algorítmico avançado para MetaTrader 5 (MT5) que utiliza Machine Learning (XGBoost) focado em dados matemáticos estacionários (ATR, Retornos) para prever a direção a curto prazo do mercado. O bot é controlável via Telegram e emprega uma estratégia altamente agressiva de **Grid Trading com Martingale**, gerindo cestos de ordens dinâmicos e adaptando-se à volatilidade e custos da corretora em tempo real.

## Funcionalidades Principais

* **Machine Learning Estacionário:** Modelo XGBClassifier treinado com variáveis blindadas (Retornos Percentuais, Distância para a MA 50, ATR Pct e RSI), eliminando o colapso do modelo perante novos máximos/mínimos do preço absoluto.
* **Motor de Execução Martingale:** Calcula o lote inicial dinamicamente com base no saldo da conta e duplica o volume (fator 2.0x) a cada nova posição aberta contra a tendência, forçando o fecho do cesto ao mínimo ressalto do mercado.
* **Lógica de Sobrevivência (Target Breakeven):** O alvo de lucro cresce a cada nova ordem, mas se a grelha atingir uma profundidade crítica (4+ posições), o bot abandona o lucro e ajusta o alvo para *Breakeven* (0.50€) apenas para salvar a conta.
* **Filtros Institucionais de Proteção:**
  * **Meta Diária (Daily Goal):** Suspensão automática das operações assim que atinge 10% de lucro sobre o capital inicial no próprio dia.
  * **Filtro de Spread:** Bloqueia a abertura e expansão da grelha se o custo da corretora ultrapassar um limite seguro (proteção contra o *Rollover* noturno).
* **Alertas Visuais Dinâmicos:** O motor gera gráficos invisíveis na memória (`matplotlib.use('Agg')`) traçando as tuas posições exatas e o lucro flutuante, enviando o *screenshot* diretamente para o teu Telegram assim que o mercado aperta.

## Pré-requisitos

* Python 3.9 ou superior.
* Terminal MetaTrader 5 instalado e a correr no Windows.
* Conta MT5 configurada como **Hedging** (obrigatório para a grelha).
* **Alavancagem Máxima (Ex: 1:400 ou 1:500)** se operado com bancas reduzidas (< 1.000€).
* Permissões de "Algo Trading" ativadas com o botão verde no MT5.

## Instalação e Configuração

1. Clona este repositório:
```bash
git clone [https://github.com/bernam07/forex-signals.git](https://github.com/bernam07/forex-signals.git)
cd forex-signals
```

2. Instala as dependências necessárias:
```bash
pip install -r requirements.txt
```

3. Cria um ficheiro `.env` na raiz do projeto com as credenciais reais da tua conta corretora:
```env
MT5_LOGIN=LOGIN
MT5_PASSWORD=PASSWORD
MT5_SERVER=SERVIDOR
TELEGRAM_BOT_TOKEN=TOKEN_DO_BOTFATHER
TELEGRAM_CHAT_ID=CHAT_ID
```

## Como Usar?

Inicia o script principal:
```bash
python main.py
```

O bot ficará em modo de escuta. Abre o teu bot no Telegram e utiliza os seguintes comandos:

* `/start` - Abre o menu para selecionares o par de moedas e iniciares a máquina preditiva.
* `/stop` - Para a análise e a abertura de novas posições (posições já abertas continuam a ser geridas até ao fecho do cesto).
* `/status` - Mostra o estado de execução atual, par ativo e o lote a ser utilizado.

## Aviso de Risco Severo

Este bot utiliza uma estratégia de **Martingale**. Não possui *Stop Loss* fixo por ordem. Em vez disso, depende da alavancagem extrema e da margem livre para abrir lotes cada vez maiores e fazer o preço médio da operação. 

Foi otimizado para contas **Cent** ou para uma abordagem de alto risco em capital reduzido (ex: alavancagem 1:500 com 50€ a 100€). Executar este sistema durante eventos de alto impacto (notícias macroeconómicas) ou em mercados de forte tendência unilateral sem pausas resultará no esgotamento da margem livre e na liquidação total da conta (*Margin Call*). Utilizar exclusivamente com capital de risco ("dinheiro de casino") e adotar o hábito de levantar o capital inicial assim que a conta duplicar.
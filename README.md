# MT5 XGBoost Trading Bot

Um bot de trading algorítmico para MetaTrader 5 (MT5) que utiliza Machine Learning (XGBoost) para prever a direção do mercado com base em Smart Money Concepts (SMC) e RSI. O bot é totalmente controlável remotamente através do Telegram e utiliza uma estratégia de Grid Trading com "Basket Closure" para maximizar lucros rápidos em mercados laterais.

## Funcionalidades

* **Machine Learning:** Modelo XGBClassifier treinado dinamicamente com as últimas 50.000 velas de 5 minutos.
* **Feature Engineering:** Deteção automática de Fair Value Gaps (FVGs), Liquidity Sweeps, tendências macro (50 MA) e RSI.
* **Gestão Ativa (Grid & Basket Closure):** Abre múltiplas posições para fazer *cost averaging* e fecha o cesto inteiro simultaneamente quando um alvo de lucro predefinido é atingido.
* **Controlo Remoto por Telegram:** Inicia, para, verifica o estado e altera o par de moedas em tempo real através de mensagens no Telegram.
* **Proteção de Dados:** Credenciais geridas de forma segura através de variáveis de ambiente (`.env`).

## Pré-requisitos

* Python 3.9 ou superior.
* Terminal MetaTrader 5 instalado e a correr.
* Conta de Demonstração ativa no MT5 configurada como **Hedging** (não Netting).
* Permissões de "Algo Trading" ativadas nas opções do MT5.

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

3. Cria um ficheiro .env na raiz do projeto com as tuas credenciais reais


## Como Usar?

Inicia o script principal:
```bash
python main.py
```

O bot ficará à espera de comandos no teu telemóvel. Abre o teu bot no Telegram e utiliza os seguintes comandos:

/start - Abre o menu para selecionares o par de moedas e iniciares o treino do modelo.

/stop - Para a análise e a abertura de novas posições (posições abertas mantêm-se geridas pelo MT5).

/status - Mostra o estado atual, o par ativo e o tamanho do lote.

## Aviso de Risco

Este bot utiliza uma estratégia agressiva de Grid/Martingale sem Stop Loss fixo por ordem, dependendo do lucro líquido do "cesto". Isto exige uma margem livre considerável. Foi desenhado estritamente para contas de demonstração com capital elevado (ex: 100.000€). Executar este código numa conta real, especialmente com capital reduzido, resultará quase garantidamente na perda total dos fundos (Margin Call). Utiliza por tua conta e risco.
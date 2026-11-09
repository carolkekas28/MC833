
# Lab 3 — Previsão de Tráfego de Rede com LSTM

**MC833A — Programação em Redes de Computadores**  
**Universidade Estadual de Campinas (Unicamp)**  
**Instituto de Computação — 2º semestre de 2026**

**Aluna:** Ana Carolina de Almeida Cardoso — RA 246914  
**Professor:** Edmundo R. M. Madeira

## 1. Objetivo

Este projeto tem como objetivo analisar e prever o throughput de um link real de backbone utilizando redes neurais recorrentes do tipo **LSTM (Long Short-Term Memory)**.

São utilizados dados do projeto **MAWI (Measurement and Analysis on the WIDE Internet)**, referentes a duas capturas realizadas com 17 anos de diferença:

- **2007:** 10 de fevereiro de 2007, às 14h (JST).
- **2024:** 10 de fevereiro de 2024, às 14h (JST).

O trabalho é dividido em duas etapas:

1. **Análise Exploratória de Dados (EDA):** caracterização estatística e visual do tráfego TCP e UDP.
2. **Modelamento Preditivo (LSTM):** treinamento, avaliação e comparação de modelos de previsão do throughput.

Também é investigada a capacidade de generalização temporal dos modelos, verificando se uma LSTM treinada com dados de um ano consegue prever o tráfego do outro.

## 2. Estrutura do projeto

```text
lab3/
├── notebooks/
│   ├── 00_preprocessamento_MAWI.ipynb
│   ├── 01_EDA.ipynb
│   └── 02_LSTM.ipynb
│
├── dados/
│   ├── README_dados.md
│   ├── 200702101400/
│   │   ├── 200702101400_resumo.json
│   │   ├── 200702101400_serie_10ms.parquet
│   │   └── ...
│   └── 202402101400/
│       ├── 202402101400_resumo.json
│       ├── 202402101400_serie_10ms.parquet
│       └── ...
│
├── modelos/
│   ├── lstm_2007.keras
│   └── lstm_2024.keras
│
├── relatorio_projeto3.pdf
└── README.md
```

### Descrição dos arquivos

| Arquivo | Descrição |
|---|---|
| `00_preprocessamento_MAWI.ipynb` | Notebook de referência que demonstra o pré-processamento dos traces MAWI. |
| `01_EDA.ipynb` | Análise exploratória do throughput e das características dos pacotes. |
| `02_LSTM.ipynb` | Implementação, treinamento e avaliação dos modelos LSTM. |
| `dados/` | Arquivos JSON e Parquet dos traces de 2007 e 2024. |
| `modelos/` | Melhores modelos LSTM treinados, salvos no formato Keras. |
| `relatorio_projeto3.pdf` | Relatório com metodologia, resultados, gráficos e conclusões. |

Os arquivos PCAP originais não são necessários para executar os notebooks, pois os dados já foram pré-processados.

## 3. Tecnologias utilizadas

O projeto foi desenvolvido em **Python**, utilizando:

- **NumPy:** operações numéricas.
- **Pandas:** leitura e manipulação dos dados.
- **PyArrow:** leitura dos arquivos Parquet.
- **Matplotlib:** visualização dos resultados.
- **Scikit-learn:** normalização das séries temporais.
- **TensorFlow/Keras:** implementação e treinamento das redes LSTM.
- **Jupyter Notebook:** execução dos experimentos.

### Ambiente utilizado

| Componente | Versão |
|---|---|
| Python | 3.9.6 |
| TensorFlow | 2.19.0 |
| Keras | 3.10.0 |
| Pandas | 2.2.3 |
| PyArrow | 21.0.0 |
| Sistema operacional | macOS (Apple Silicon) |

## 4. Preparação do ambiente

Instale as dependências necessárias:

```bash
python3 -m pip install numpy pandas matplotlib scikit-learn pyarrow tensorflow==2.19.0 ipykernel
```

O projeto foi executado localmente no VS Code com Jupyter Notebook, embora os notebooks originais também tenham sido preparados para utilização no Google Colab.

### Configuração dos caminhos

Os notebooks utilizam a variável `PASTA_DADOS` para localizar os arquivos.

Para a estrutura local do repositório:

```python
from pathlib import Path

BASE = Path.cwd().resolve()

if BASE.name == 'notebooks':
    BASE = BASE.parent

PASTA_DADOS = str(BASE / 'dados')
```

Essa configuração permite executar os notebooks a partir das pastas `lab3/` ou `lab3/notebooks/`.

## 5. Base de dados

Os traces foram obtidos do projeto MAWI e representam aproximadamente 15 minutos de tráfego de um link de backbone.

| Característica | 2007 | 2024 |
|---|---:|---:|
| Identificador | `200702101400` | `202402101400` |
| Duração | 900,33 s | 899,78 s |
| Pacotes | 14.487.390 | 138.789.798 |
| Throughput médio | 94,30 Mbps | 1.228,90 Mbps |
| Resolução original | 10 ms | 10 ms |

Fontes originais:

- [MAWI — Trace de 2007](https://mawi.wide.ad.jp/mawi/samplepoint-F/2007/200702101400.html)
- [MAWI — Trace de 2024](https://mawi.wide.ad.jp/mawi/samplepoint-F/2024/202402101400.html)

Os dados utilizados na modelagem são agregados em intervalos de **1 segundo**, e o throughput é expresso em Mbps.

## 6. Parte 1 — Análise exploratória de dados

O notebook `01_EDA.ipynb` caracteriza o comportamento do tráfego nos dois anos.

### Estatísticas descritivas

Foram calculados média, desvio-padrão, mínimo, quartis e máximo do throughput por segundo, considerando:

- Tráfego total;
- TCP;
- UDP.

Os resultados mostram que o throughput médio total aumentou de **94,29 Mbps em 2007 para 1.229,11 Mbps em 2024**, aproximadamente 13 vezes.

O crescimento foi acompanhado por maior variabilidade temporal.

### Visualizações

Foram produzidos três gráficos comparativos:

1. **Throughput ao longo do tempo:** evolução das taxas de transmissão durante os traces.
2. **Histogramas TCP × UDP:** distribuição do throughput por segundo de cada protocolo.
3. **Distribuição do tamanho dos pacotes:** comparação percentual dos tamanhos dos pacotes TCP e UDP.

Os resultados evidenciam diferenças significativas na intensidade, na variabilidade e na composição do tráfego entre os dois períodos.

## 7. Parte 2 — Modelamento preditivo com LSTM

O notebook `02_LSTM.ipynb` implementa uma rede neural recorrente para prever o próximo valor do throughput a partir de observações anteriores.

### Arquitetura

A arquitetura utilizada é composta por:

```text
Entrada: janela temporal de throughput
           │
           ▼
     LSTM (32 unidades)
           │
           ▼
       Dense (1)
           │
           ▼
   Throughput previsto
```

### Hiperparâmetros

| Parâmetro | Configuração |
|---|---|
| Camadas | 1 LSTM + 1 Dense |
| Unidades LSTM | 32 |
| Janelas avaliadas | 10, 20 e 30 segundos |
| Épocas máximas | 50 |
| Batch size | 32 |
| Otimizador | Adam |
| Função de perda | MSE |
| Treinamento | 80% da série |
| Teste | 20% da série |
| Validação | 10% dos dados de treinamento |
| EarlyStopping | Paciência de 10 épocas |
| Semente aleatória | 42 |

A divisão dos dados respeita a ordem temporal, sem embaralhamento.

O modelo é comparado com um baseline de **persistência**, que utiliza o último valor observado como previsão do próximo.

### Sensibilidade ao tamanho da janela

Foram treinados seis modelos, combinando os dois anos com as três janelas temporais.

| Ano | Janela | MSE (Mbps²) | RMSE (Mbps) | RMSE/média |
|---|---:|---:|---:|---:|
| 2007 | 10 | 40,71 | 6,38 | 6,64% |
| 2007 | 20 | 41,05 | 6,41 | 6,67% |
| **2007** | **30** | **33,20** | **5,76** | **5,99%** |
| 2024 | 10 | 46.410,53 | 215,43 | 19,66% |
| **2024** | **20** | **38.509,89** | **196,24** | **17,91%** |
| 2024 | 30 | 65.628,41 | 256,18 | 23,38% |

A seleção dos melhores modelos foi realizada pela **menor perda de validação**, sem utilizar os resultados de teste para escolher os hiperparâmetros.

As configurações selecionadas foram:

- **2007:** janela de 30 segundos.
- **2024:** janela de 20 segundos.

Ambos os modelos apresentaram resultados ligeiramente superiores à persistência em seus respectivos conjuntos de teste.

## 8. Generalização temporal — 2007 × 2024

Para investigar a capacidade de transferência, cada modelo foi testado tanto no seu ano de treinamento quanto no outro ano.

Foi mantido o mesmo `MinMaxScaler` ajustado durante o treinamento de cada modelo.

### Matriz de resultados

| Modelo treinado em | Testado em | RMSE (Mbps) | RMSE/média |
|---|---|---:|---:|
| 2007 | 2007 | 5,76 | 5,99% |
| 2007 | 2024 | 888,50 | 81,08% |
| 2024 | 2007 | 203,11 | 211,29% |
| 2024 | 2024 | 196,24 | 17,91% |

Os modelos apresentaram desempenho satisfatório nos dados de seus respectivos anos, mas erros elevados quando avaliados no outro período.

O modelo de 2007 subestimou sistematicamente o throughput de 2024, enquanto o modelo de 2024 superestimou o tráfego de 2007.

Esse comportamento evidencia a dificuldade de generalização diante de mudanças na escala e na distribuição dos dados (*distribution shift*).

## 9. Principais conclusões

A análise permitiu observar que:

1. O throughput médio do trace de 2024 foi aproximadamente 13 vezes superior ao de 2007.
2. O tráfego de 2024 apresentou maior variabilidade e picos de transmissão mais pronunciados.
3. O tamanho da janela temporal influenciou o desempenho das redes LSTM.
4. Os melhores modelos superaram ligeiramente o método de persistência nos testes do próprio ano.
5. A transferência entre anos apresentou erros elevados, indicando baixa capacidade de generalização temporal.

Os resultados mostram a importância de considerar mudanças na distribuição do tráfego ao desenvolver modelos preditivos para redes de computadores.

**Limitação:** os traces correspondem a um único ponto de medição, durante aproximadamente 15 minutos em cada ano. Portanto, os resultados não devem ser generalizados para todo o tráfego da Internet nos respectivos períodos.

## 10. Como executar

1. Clone o repositório:

```bash
git clone https://github.com/carolkekas28/MC833.git
cd MC833/lab3
```

2. Instale as dependências indicadas na seção 4.

3. Abra a pasta no VS Code e selecione o ambiente Python como kernel do Jupyter.

4. Execute os notebooks na seguinte ordem:

   - `notebooks/01_EDA.ipynb`
   - `notebooks/02_LSTM.ipynb`

O notebook `00_preprocessamento_MAWI.ipynb` é opcional, pois os arquivos Parquet já estão disponíveis.

Ao executar o `02_LSTM.ipynb`, os melhores modelos serão salvos na pasta configurada por `PASTA_MODELOS`.

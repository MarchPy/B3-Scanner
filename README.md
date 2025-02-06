# InvestTrade

## Descrição
InvestTrade é uma ferramenta automatizada para coleta de dados fundamentalistas de ativos financeiros, como ações, BDRs e FIIs, utilizando a biblioteca Selenium para web scraping. O programa acessa o site [Investidor10](https://investidor10.com.br/) e extrai informações relevantes para análise financeira.

## Funcionalidades
- Coleta dados fundamentalistas de ações, BDRs e FIIs
- Utiliza Selenium para navegar e extrair dados de forma automatizada
- Suporte para execução headless do navegador
- Tratamento de erros para elementos inexistentes na página
- Exibição de logs coloridos usando `rich.console`

## Requisitos
Certifique-se de ter as seguintes dependências instaladas antes de rodar o programa:

```sh
pip install lxml==5.3.0 numpy==2.2.1 rich==13.9.4 pandas==2.2.3 openpyxl==3.1.5 yfinance==0.2.51 selenium==4.27.1 webdriver_manager==4.0.2
```

## Como Usar
1. Configure o arquivo `settings.json` com os ativos que deseja coletar.
2. Instale as dependências necessárias.
3. Execute o script principal para iniciar a coleta de dados.

## Estrutura do Projeto
```
InvestTrade/
│── src/
│   ├── Exceptions.py   # Exceções personalizadas
│   ├── InvestTrade.py  # Script principal
│   ├── Setups.py       # Classe com setups de investimento
│── run.py              # Arquivo de inicialização
│── README.md           # Documentação do projeto
│── settings.json       # Configuração de ativos a serem coletados e ferramentas
```

## Exemplo de Uso
```sh
python3.13 .\run.py --fetch <tipo_de_coleta>
```

## Tratamento de Erros
Caso um ativo não seja encontrado, a aplicação exibirá uma mensagem de erro e seguirá para o próximo ativo da lista. Se um tipo de busca inválido for fornecido, uma exceção `TypeFetchNotExists` será levantada.

## Autor
João Pedro Alexandre Marchiori - MarchPy

## Licença
Este projeto é distribuído sob a licença MIT.


# Faturas-bot

## Description

Python script to validate PT receipts from [Portal das Financas](https://faturas.portaldasfinancas.gov.pt/).

Notes: 
1. After logging in the portal, copy the `Cookie` header from a request. Set `COOKIE` env variable or hard-code in the code to run authenticated requests.
2. Set env variables `DATA_INICIO` and `DATA_FIM` for the start and end dates filter to limit the range of the receipts to be processed.
3. NIF mappings need to be adjusted accordingly in var `AMBITO_AQUISICAO_MAP_NIF`.
4. There could be ocasional throttles when calling the update endpoint multiple times in a short time period. A manual retry needs to be performed.

### Run

    python3 src/faturas.py

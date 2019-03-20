from ...apis import transactions

urls = [
    "/v1/transactions/confirms", transactions.Confirms,
    "/v1/transactions/transfer", transactions.Transfer,
    "/v1/transactions/getutxoes", transactions.GetUtxoes,
    "/v1/transactions/gettransactions", transactions.GetTransactions
]

reset() {
    sleep 1m
    clear
}

printf "\n-- Testes CRUD Ok e NOk --\n"
pytest test_cliente.py -vv
reset

printf "\n-- Teste de iteração --\n"
pytest test_execution.py -vv
reset

printf "\n-- Teste de recuperação de estado --\n"
rm logs.log
pytest test_recovery.py -vv
reset

printf "\n-- Teste de concorrência --\n"
pytest test_concurrency.py -vv
reset

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
# TODO

printf "\n-- Teste de concorrência --\n"
# TODO
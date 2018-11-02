## Abrir novo terminal
```bash
xterm -title "App 1" -e "mycommand; mysecondcommand" 
```

## Executar comando bash pelo python
```py

# mantem a bash aberta
os.system("gnome-terminal -e 'bash -c \"sudo apt-get update; exec bash\"'")

# fecha a bash após comando
os.system("gnome-terminal -e 'sudo apt-get update'")

```
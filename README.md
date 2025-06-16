## 📁 Estrutura do Projeto

```
trabalhoSO-feat-feat/
│
├── main.py                  # Arquivo principal que inicializa o grid e os robôs
├── robot.py                 # Classe Robot, define o comportamento individual dos robôs
├── auxiliar.py              # Funções auxiliares para manipular o grid e estados
├── global_configs.py        # Configurações globais como tamanho do grid, cores, delays
├── visualizador_pygame.py   # Função viewer() que renderiza o grid com pygame
├── requirements.txt        
├── .gitignore              
└── README.md               
```

### Rodando a aplicação

1. Clonando o repositório
```bash
git clone https://github.com/thifx/trabalhoSO.git
cd trabalhoSO
```
2. Instalando as dependências

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

3. Inicie a aplicação
```bash
python3 main.py
```

---

## 📃 Licença

Uso educacional apenas.

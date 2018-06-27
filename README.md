# Taskbot
![PyPI - Python Version](https://img.shields.io/badge/python-3-blue.svg?longCache=true&style=flat-square)
![TecProg](https://img.shields.io/badge/TecProg-2018.1-red.svg?Cache=true&style=flat-square)

### **Virtualenv**

##### **1. Instale o Pip**
Para visualizar se você possui o pip instalado, use:
```shell
$ pip --version
```

Caso não tenha o pip instalado, use:
```shell
$ sudo apt-get install python3-pip
```


##### **2. Instale o Virtualenv**
Para visualizar se você possui o virtualenv instalado, use:
```shell
$ virtualenv --version
```

Caso não tenha o pip instalado, use:   
```shell
$ sudo pip3 install virtualenv
```


##### **3. Crie um Virtualenv com Python3**
```shell
$ virtualenv -p python3 env
```


##### **4. Entre no Virtualenv**
Entre na pasta que contém seu virtualenv e use:  

```shell 
$ source env/bin/activate
```

---

### **Começando a mexer no seu bot**
- Seguir o tutorial de criação de bots [BotFather](https://core.telegram.org/bots#6-botfather)
- Adicionar o TOKEN no local indicado no código
- Cada grupo deve me enviar o TOKEN através do formulário disponibilizado no moodle

#### **5. Atualizando Dependências**
O primeiro comando instala a biblioteca requests. O segundo comando instala todas as dependências que existem no arquivo requirements.txt .

```shell
$ pip install requests
```
```shell
$ pip install -r requirements.txt 
```
---

### **6. Rode o projeto**
```shell
$ python taskbot.py
```
---

- Para checar as funcionalidades do seu Bot: 
```shell
/help
```
---

### Issues
- As issues cadastradas são de novas features, bugs e requisitos de segurança
- O grupo estava encarregado de resolver as [issues deste repositório](https://github.com/TecProg-20181/Taskbot)

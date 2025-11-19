# 🚀 Qodo PDV - Sistema Completo de Ponto de Venda

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen.svg)

**A biblioteca Python que acelera o desenvolvimento de sistemas PDV**

[Documentação](https://github.com/Gilderlan0101/qodo-pdv) • [Exemplos](#-como-usar) • [Reportar Bug](https://github.com/Gilderlan0101/qodo-pdv/issues)

</div>

<hr>

## 📋 Índice

- [🎯 Por que criar essa biblioteca?](#-por-que-criar-essa-biblioteca)
- [✨ Funcionalidades](#-funcionalidades)
- [🛠️ Tecnologias](#️-tecnologias)
- [⚡ Quick Start](#-quick-start)
- [🚀 Como usar](#-como-usar)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [🔧 Configuração](#-configuração)
- [📚 API Reference](#-api-reference)
- [🤝 Contribuindo](#-contribuindo)
- [📄 Licença](#-licença)
- [📞 Contato](#-contato)

<hr>

## 🎯 Por que criar essa biblioteca?

Desenvolver um sistema de PDV do zero costuma ser trabalhoso: copiar e replicar código, corrigir bugs e lidar com tarefas repetitivas consomem tempo e diminuem a produtividade. Pensando nisso, a **Qodo** criou uma biblioteca para acelerar o desenvolvimento e reduzir a complexidade dessas etapas.

**Problemas que resolvemos:**
- ✅ **Evita retrabalho** - Endpoints prontos para funcionalidades comuns
- ✅ **Padronização** - Estrutura consistente para todos os projetos
- ✅ **Manutenção simplificada** - Atualizações centralizadas
- ✅ **Documentação completa** - APIs bem documentadas e exemplos práticos
- ✅ **Comunidade** - Soluções testadas e validadas pela comunidade

**Assim nasceu o PyPDV**, uma biblioteca Python com endpoints prontos, construída em FastAPI e MySQL, projetada para tornar o desenvolvimento de sistemas de PDV mais simples, rápido e eficiente.

<hr>

## ✨ Funcionalidades

### 🛒 **Vendas & Carrinho**
- ✅ Gestão completa de vendas
- ✅ Carrinho dinâmico em tempo real
- ✅ Cancelamento de vendas
- ✅ Múltiplos métodos de pagamento
- ✅ Vendas parceladas
- ✅ Controle de troco

### 📦 **Produtos & Estoque**
- ✅ Cadastro e gestão de produtos
- ✅ Controle de inventário inteligente
- ✅ Upload de imagens
- ✅ Categorização e tickets
- ✅ Alertas de estoque baixo
- ✅ Validação de data de validade

### 👥 **Clientes & Funcionários**
- ✅ CRM integrado
- ✅ Gestão de equipe
- ✅ Controle de acesso multi-nível
- ✅ Sistema de crédito para clientes
- ✅ Histórico de compras

### 💳 **Pagamentos**
- ✅ Múltiplos métodos de pagamento
- ✅ PIX integrado com QR Code
- ✅ Pagamentos parcelados
- ✅ Controle de contas bancárias
- ✅ Reconciliação financeira

### 🚚 **Delivery**
- ✅ Gestão completa de entregas
- ✅ Rastreamento em tempo real
- ✅ Atribuição automática de entregadores
- ✅ Controle de status
- ✅ Relatórios de performance

### 📊 **Dashboard & Analytics**
- ✅ Relatórios em tempo real
- ✅ Métricas de performance
- ✅ Analytics de vendas
- ✅ Indicadores financeiros
- ✅ Gráficos e visualizações

### 🏢 **Fornecedores**
- ✅ Cadastro completo de fornecedores
- ✅ Gestão de contatos
- ✅ Controle de prazos de pagamento
- ✅ Histórico de compras

<hr>

## 🛠️ Tecnologias

**Backend:**
- ![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-green) - Framework web moderno e rápido
- ![Python](https://img.shields.io/badge/Python-3.8+-blue) - Linguagem principal
- ![SQLModel](https://img.shields.io/badge/SQLModel-0.0.27+-orange) - ORM moderno
- ![TortoiseORM](https://img.shields.io/badge/Tortoise_ORM-0.25.1+-yellow) - ORM assíncrono
- ![Pydantic](https://img.shields.io/badge/Pydantic-2.0+-blue) - Validação de dados

**Banco de Dados:**
- ![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange) - Banco relacional principal
- ![SQLite](https://img.shields.io/badge/SQLite-3.0+-lightgrey) - Alternativa para desenvolvimento

**Autenticação & Segurança:**
- ![JWT](https://img.shields.io/badge/JWT-Bearer_Tokens-red) - Autenticação stateless
- ![bcrypt](https://img.shields.io/badge/bcrypt-4.3.0+-green) - Hash de senhas
- ![CORS](https://img.shields.io/badge/CORS-Enabled-blue) - Cross-Origin Resource Sharing

**Outras Dependências:**
- ![Uvicorn](https://img.shields.io/badge/Uvicorn-0.38.0+-purple) - Servidor ASGI
- ![Python-JOSE](https://img.shields.io/badge/Python--JOSE-3.5.0+-yellow) - Criptografia JWT
- ![Faker](https://img.shields.io/badge/Faker-38.0.0+-lightblue) - Dados de teste

<hr>

## ⚡ Quick Start

### Instalação

```bash
# Instalação via pip
pip install qodo-pdv

# Ou instalação em modo desenvolvimento
git clone [https://github.com/Gilderlan0101/qodo-pdv.git](https://github.com/Gilderlan0101/qodo-pdv.git)
cd qodo-pdv
pip install -e .
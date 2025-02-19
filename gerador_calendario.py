from itertools import permutations
import os
import random

def solicitar_times():
    if os.path.exists("times.txt"):
        with open("times.txt", "r") as arquivo:
            times = [linha.strip() for linha in arquivo.readlines()]
        return times
    
    num_times = int(input("Digite o número de times na competição: "))
    times = []
    for i in range(num_times):
        time = input(f"Digite o nome do {i+1}º time: ")
        times.append(time)
    
    with open("times.txt", "w") as arquivo:
        for time in times:
            arquivo.write(time + "\n")
    
    return times

def gerar_confrontos(times):
    num_times = len(times)
    rodadas = []
    random.shuffle(times)  # Aleatoriza a ordem dos times
    
    for rodada in range(num_times - 1):
        confrontos = []
        for i in range(num_times // 2):
            casa = times[i]
            fora = times[num_times - 1 - i]
            confrontos.append((casa, fora))
        rodadas.append(confrontos)
        times.insert(1, times.pop())  # Rotaciona os times (exceto o primeiro)
    
    return rodadas

def carregar_resultados():
    try:
        with open("resultados.txt", "r") as arquivo:
            resultados = [linha.strip() for linha in arquivo.readlines()]
        return resultados
    except FileNotFoundError:
        return []

def salvar_resultados(resultados):
    with open("resultados.txt", "w") as arquivo:
        for resultado in resultados:
            arquivo.write(resultado + "\n")

def inserir_resultados(rodadas):
    resultados = carregar_resultados()
    novos_resultados = resultados[:]
    index = 0
    
    for turno in range(2):  # Primeiro e segundo turno
        for rodada_idx, rodada in enumerate(rodadas):
            for jogo_idx, jogo in enumerate(rodada):
                if turno == 1:  # Inverter mando de campo no returno
                    jogo = (jogo[1], jogo[0])
                
                if index < len(novos_resultados) and "Rodada" in novos_resultados[index]:
                    print(f"{novos_resultados[index]}")
                    index += 1
                    continue
                
                resultado = input(f"Digite o resultado para {jogo[0]} x {jogo[1]} (ex: 2 1 ou Enter para pular): ")
                if resultado.strip() == "":
                    resultado = "-"
                linha_resultado = f"Rodada {rodada_idx + 1 + (turno * len(rodadas))}: {jogo[0]} x {jogo[1]} - {resultado}"
                if index < len(novos_resultados):
                    novos_resultados[index] = linha_resultado
                else:
                    novos_resultados.append(linha_resultado)
                index += 1
    
    salvar_resultados(novos_resultados)

def exibir_calendario(rodadas):
    num_rodadas = len(rodadas)
    separador = "=" * 40
    resultados = carregar_resultados()
    
    index = 0
    nome_max = max(len(time) for time in solicitar_times()) + 2  # Ajustar espaçamento com base no maior nome
    for turno in range(2):  # Primeiro e segundo turno
        for i, rodada in enumerate(rodadas):
            print(separador)
            print(f"Rodada {i+1 + (turno * num_rodadas)}".center(40))
            print(separador)
            for j, jogo in enumerate(rodada, 1):
                if turno == 1:
                    jogo = (jogo[1], jogo[0])  # Inverte o mando de campo no returno
                placar = resultados[index] if index < len(resultados) else "-"
                print(f"{j}. {jogo[0]:<{nome_max}} vs {jogo[1]:<{nome_max}} - {placar}")
                index += 1
            print()

def calcular_classificacao():
    times = solicitar_times()
    resultados = carregar_resultados()
    tabela = {time: {'Pontos': 0, 'Vitórias': 0, 'Derrotas': 0, 'Saldo': 0,  'Feitos': 0, 'Sofridos': 0} for time in times}
    
    for linha in resultados:
        if "Rodada" not in linha or "-" not in linha:
            continue
        try:
            partes = linha.split(": ")[1]
            confronto, placar = partes.split(" - ")
            time_casa, time_fora = confronto.split(" x ")
            gols_casa, gols_fora = map(int, placar.split())

            tabela[time_casa]['Feitos'] += gols_casa
            tabela[time_casa]['Sofridos'] += gols_fora
            tabela[time_fora]['Feitos'] += gols_fora
            tabela[time_fora]['Sofridos'] += gols_casa

            # Se o placar não for um número válido, pula essa linha
            if placar.strip() == "-":
                continue  

            time_casa, time_fora = confronto.split(" x ")
            gols_casa, gols_fora = map(int, placar.split())

            if gols_casa > gols_fora:
                #tabela[time_casa]['Pontos'] += 3
                tabela[time_casa]['Vitórias'] += 1
                tabela[time_fora]['Derrotas'] += 1
                
            elif gols_fora > gols_casa:
                #tabela[time_fora]['Pontos'] += 3
                tabela[time_fora]['Vitórias'] += 1
                tabela[time_casa]['Derrotas'] += 1
                #Essa simulação não usa empates, mas se usasse seria o abaixo
            #else:
                #tabela[time_casa]['Pontos'] += 1
                #tabela[time_fora]['Pontos'] += 1

            tabela[time_casa]['Saldo'] = tabela[time_casa]['Feitos'] - tabela[time_casa]['Sofridos']
            tabela[time_fora]['Saldo'] = tabela[time_fora]['Feitos'] - tabela[time_fora]['Sofridos']

        except ValueError:
            print(f"Jogo ainda sem resultado: {linha}")
            continue

    classificacao = sorted(tabela.items(), key=lambda x: (x[1]['Vitórias'], x[1]['Saldo']), reverse=True)
    
    with open("classificacao.txt", "w") as arquivo:
        nome_max = max(len(time) for time in solicitar_times()) + 2  # Ajustar espaçamento com base no maior nome
        arquivo.write("Classificação:\n")
        arquivo.write("=" * 60 + "\n")
        #arquivo.write(f"{'Time':<15}{'Pontos':<10}{'Vitórias':<10}{'Derrotas':<10}{'Saldo':<10}\n")
        arquivo.write(f"{'Time':{nome_max}}{'Vitórias':>10}{'Derrotas':>10}{'Saldo':>10}\n")
        arquivo.write("-" * 60 + "\n")
        for time, stats in classificacao:
            arquivo.write(f"{time:{nome_max}}{stats['Vitórias']:>10}{stats['Derrotas']:>10}{stats['Saldo']:>10}\n")
            #arquivo.write(f"{time:<15}{stats['Pontos']:<10}{stats['Vitórias']:<10}{stats['Derrotas']:<10}{'Saldo':<10}\n")
        arquivo.write("=" * 60 + "\n")
    
    print("Classificação salva em classificacao.txt")

# Execução
times = solicitar_times()
rodadas = gerar_confrontos(times)
exibir_calendario(rodadas)
inserir_resultados(rodadas)
calcular_classificacao()

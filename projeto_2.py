import sqlite3
import json
import pandas as pd
import numpy as np

con = sqlite3.connect('Oficinas.db')
cursor = con.cursor()

def criar_tabelas():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Oficinas (
        id_oficina INTEGER PRIMARY KEY,
        nome TEXT NOT NULL,
        morada TEXT,
        concelho TEXT,
        populacao_concelho INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Veiculos (
        id_veiculo INTEGER PRIMARY KEY,
        id_oficina INTEGER,
        matricula TEXT NOT NULL,
        marca TEXT,
        data_hora TEXT,
        tipo_combustivel INTEGER,
        km_ultima_revisao INTEGER,
        num_portas INTEGER,
        nivel_oleo INTEGER,
        num_alarmes INTEGER,
        espessura_discos INTEGER,
        previsao_revisao INTEGER,
        decisao_mecanico INTEGER,
        FOREIGN KEY(id_oficina) REFERENCES Oficinas(id_oficina)
    )
    ''')
    con.commit()
    print("-> Sistema: Estrutura de tabelas criada e pronta.")


def importar_oficina(caminho_json):
    try:
        with open(caminho_json, 'r', encoding='utf-8') as f:
            dados_brutos = json.load(f)
        if isinstance(dados_brutos, dict):
            dados_brutos = [dados_brutos]
            
        for oficina in dados_brutos:
            cursor.execute('''
                INSERT OR REPLACE INTO Oficinas (id_oficina, nome, morada, concelho, populacao_concelho)
                VALUES (?, ?, ?, ?, ?)
            ''', (oficina['id_oficina'], oficina['nome'], oficina['morada'], oficina['concelho'], oficina['populacao_concelho']))
        con.commit()
        print("-> Sucesso: Dados da empresa carregados a partir do JSON.")
    except Exception as e:
        print(f"Erro ao ler o ficheiro JSON: {e}")

def consultar_oficina(id_oficina):
    cursor.execute("SELECT * FROM Oficinas WHERE id_oficina = ?", (id_oficina,))
    return cursor.fetchone()

def eliminar_oficina(id_oficina):
    cursor.execute("DELETE FROM Oficinas WHERE id_oficina = ?", (id_oficina,))
    con.commit()
    print(f"-> Remoção: Oficina com ID {id_oficina} foi retirada do sistema.")


def importar_veiculos(caminho_csv):
    try:
        dados_carros = pd.read_csv(caminho_csv)
        
        for id_v in dados_carros['id_veiculo']:
            cursor.execute("DELETE FROM Veiculos WHERE id_veiculo = ?", (int(id_v),))
        con.commit()

        dados_carros.to_sql('Veiculos', con, if_exists='append', index=False)
        con.commit()
        print("-> Sucesso: Fichas de veículos inseridas a partir do CSV.")
    except Exception as e:
        print(f"Erro ao processar ficheiro CSV: {e}")


def calcular_previsoes():
    tabela_veiculos = pd.read_sql_query("SELECT * FROM Veiculos", con)
    if tabela_veiculos.empty:
        print("-> Aviso: Não há veículos registados para calcular previsões.")
        return

    KM = tabela_veiculos['km_ultima_revisao'].to_numpy()
    ED = tabela_veiculos['espessura_discos'].to_numpy()

    mediaKM = np.mean(KM)
    desvioKM = np.std(KM)
    limite = mediaKM + 2 * desvioKM
    medianaKM = np.median(KM)
    KM_corrigido = np.where(KM > limite, medianaKM, KM)

    idV = np.where(ED != -1)
    if len(idV[0]) > 0:
        mediaED = np.mean(ED[idV])
    else:
        mediaED = 35.0
    ED_corrigido = np.where(ED == -1, mediaED, ED)

    ponto_corte_KM = 15.0
    ponto_corte_ED = 20.0

    condicao_revisao = (ED_corrigido < ponto_corte_ED) | (KM_corrigido > ponto_corte_KM)
    tabela_veiculos['previsao_revisao'] = np.where(condicao_revisao, 1, 0)

    lista_atualizar = tabela_veiculos[['previsao_revisao', 'id_veiculo']].to_records(index=False).tolist()
    cursor.executemany("UPDATE Veiculos SET previsao_revisao = ? WHERE id_veiculo = ?", lista_atualizar)
    con.commit()
    print("->Limpeza e análise estatística aplicadas aos dados dos veículos.")


def relatorio(id_oficina, data_inicio, data_fim):
    comando_procura = """
        SELECT veic.*, ofic.nome as nome_da_oficina, ofic.concelho, ofic.populacao_concelho 
        FROM Veiculos veic
        INNER JOIN Oficinas ofic ON veic.id_oficina = ofic.id_oficina
        WHERE veic.id_oficina = ?
    """
    dados_totais = pd.read_sql_query(comando_procura, con, params=(id_oficina,))
    if dados_totais.empty:
        print("-> Erro: Falta de dados para construir o relatório desta oficina.")
        return

    dados_totais['data_hora'] = pd.to_datetime(dados_totais['data_hora'])
    dados_totais.set_index('data_hora', inplace=True)
    dados_totais.sort_index(inplace=True)
    
    dados_periodo = dados_totais.loc[data_inicio:data_fim]
    if dados_periodo.empty:
        print(f"-> Limite: Sem dados encontrados no intervalo de {data_inicio} a {data_fim}.")
        return

    total_veiculos_oficina = len(dados_periodo)
    populacao_concelho = dados_periodo['populacao_concelho'].iloc[0]
    veiculos_per_capita = total_veiculos_oficina / populacao_concelho if populacao_concelho > 0 else 0
    
    deve_revisar = dados_periodo[dados_periodo['previsao_revisao'] == 1].shape[0]
    nao_deve_revisar = dados_periodo[dados_periodo['previsao_revisao'] == 0].shape[0]
    faltam_verificar = dados_periodo[dados_periodo['decisao_mecanico'].isna()].shape[0]

    print("\n" + "="*55)
    print(f"RELATÓRIO ESTATÍSTICO: {dados_periodo['nome_da_oficina'].iloc[0]}")
    print(f"Período Analisado: {data_inicio} a {data_fim}")
    print("="*55)
    print(f"População do Concelho ({dados_periodo['concelho'].iloc[0]}): {populacao_concelho} hab.")
    print(f"Veículos Automóveis per Capita: {veiculos_per_capita:.6f}")
    print(f"Veículos com indicação de Revisão : {deve_revisar}")
    print(f"Veículos dispensados de Revisão   : {nao_deve_revisar}")
    print(f"Veículos PENDENTES de verificação : {faltam_verificar}") 
    print(f"Volume Total de Atendimentos: {total_veiculos_oficina}")
    print("="*55 + "\n")


def consultar_ficha_veiculo(id_veiculo):
    cursor.execute("SELECT * FROM Veiculos WHERE id_veiculo = ?", (id_veiculo,))
    return cursor.fetchone()


def mostrar_carro(id_veiculo):
    carro = consultar_ficha_veiculo(id_veiculo)
    if carro:
        print("\n--- [PAINEL DO MECÂNICO] CONSULTA DE FICHA ---")
        print(f"ID Veículo: {carro[0]} | Matrícula: {carro[2]} | Marca: {carro[3]}")
        print(f"Quilometragem: {carro[6]}k km | Espessura Discos: {carro[10]} mm")
        print(f"-> Previsão (Projeto-I): {'1 [REVISAR]' if carro[11] == 1 else '0 (OK)'}")
        
        if carro[12] is None:  
            print("-> Decisão Final do Mecânico: Pendente")
        elif carro[12] == 1:
            print(f"-> Decisão Final do Mecânico: {carro[12]} [REVISAR]")
        else:
            print(f"-> Decisão Final do Mecânico: {carro[12]} [NÃO REVISAR]")
        print("-" * 44)
    else:
        print("-> Erro: O veículo pedido não foi encontrado.")


def gravar_decisao(id_veiculo, decisao_final):
    if decisao_final in [0, 1]:
        cursor.execute("UPDATE Veiculos SET decisao_mecanico = ? WHERE id_veiculo = ?", (decisao_final, id_veiculo))
        con.commit()
        if decisao_final == 1:
            print(f"-> Registo: Carro {id_veiculo} marcado como [PRECISA REVISAR].")
        else:
            print(f"-> Registo: Carro {id_veiculo} marcado como [NÃO PRECISA REVISAR].")
    else:
        print("-> Erro: Escolha inválida. Use apenas 1 (Revisar) ou 0 (Dispensar).")


if __name__ == "__main__":
    criar_tabelas()
    
    importar_oficina('oficina_dados.json')
    importar_veiculos('veiculos_dados.csv')
    
    calcular_previsoes()
    
    mostrar_carro(1050)
    gravar_decisao(1050, 1) 
    
    relatorio(10, '2026-05-01', '2026-06-1')
    
    con.close()

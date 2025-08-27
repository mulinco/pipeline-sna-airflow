import asyncio
import websockets
import json
import csv
import os
import re

async def save_data(matrix, title, output_folder="extracted_data"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    sane_title = re.sub(r'[\\/*?:"<>|]', "", title).replace(" ", "_")
    filename = os.path.join(output_folder, f"{sane_title}.csv")
    print(f"📝 Salvando dados de '{title}' em: {filename}")
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Categoria', 'Valor'])
        for row in matrix:
            if len(row) >= 2:
                writer.writerow([row[0].get("qText", "N/A"), row[1].get("qText", "N/A")])
    print("✅ Arquivo salvo!")

async def victory_lap_extractor():
    uri = "wss://paineisanalytics.cnj.jus.br/app/ccd72056-8999-4434-b913-f74b5b5b31a2?reloadUri=https%3A%2F%2Fpaineisanalytics.cnj.jus.br%2Fsingle%2F%3Fappid%3Dccd72056-8999-4434-b913-f74b5b5b31a2%26sheet%3D937a1045-cf2b-45a7-8ae1-4f61d7eeb3cf%26lang%3Dpt-BR%26opt%3Dctxmenu%2Ccurrsel%26select%3Dclearall"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    origin = "https://paineisanalytics.cnj.jus.br"

    # Conexão com os argumentos corrigidos e específicos
    async with websockets.connect(
        uri,
        user_agent_header=user_agent,
        origin=origin,
        ping_interval=None
    ) as websocket:
        print("✅ Conexão estabelecida!")
        await websocket.recv(); await websocket.recv()

        open_doc_msg = {"jsonrpc": "2.0", "id": 2, "method": "OpenDoc", "handle": -1, "params": ["ccd72056-8999-4434-b913-f74b5b5b31a2"]}
        await websocket.send(json.dumps(open_doc_msg))
        open_doc_response = json.loads(await websocket.recv())
        doc_handle = open_doc_response["result"]["qReturn"]["qHandle"]
        print(f"✅ Painel aberto. Handle: {doc_handle}")

        
        chart_definition = {
            "qInfo": {"qType": "Chart"},
            "qHyperCubeDef": {
                "qDimensions": [{"qDef": {"qFieldDefs": ["=SNA_VA_DSC_REGIAO"]}}],
                "qMeasures": [{"qLibraryId": "31a79380-ea6c-4b4e-8ace-fb2c715d4314", "qDef": {}}],
                "qInitialDataFetch": [{"qTop": 0, "qLeft": 0, "qWidth": 2, "qHeight": 10}]
            }
        }

        create_object_msg = {
            "handle": doc_handle, "method": "CreateSessionObject", "params": [chart_definition], "id": 3, "jsonrpc": "2.0"
        }
        print("\n>> Construindo objeto com a receita correta...")
        await websocket.send(json.dumps(create_object_msg))
        create_object_response = json.loads(await websocket.recv())
        object_handle = create_object_response["result"]["qReturn"]["qHandle"]
        print(f"✅ Objeto temporário criado. Handle: {object_handle}")

        get_layout_msg = {"jsonrpc": "2.0", "id": 4, "method": "GetLayout", "handle": object_handle, "params": []}
        print("\n>> Pedindo os dados do objeto...")
        await websocket.send(json.dumps(get_layout_msg))
        layout_response = json.loads(await websocket.recv())

        print("\n--- DADOS FINAIS EXTRAÍDOS ---")
        try:
            matrix = layout_response["result"]["qLayout"]["qHyperCube"]["qDataPages"][0]["qMatrix"]
            await save_data(matrix, "Dados_Por_Regiao_VITORIA_FINAL")
        except KeyError:
            print("❌ Falha ao extrair os dados. Resposta do servidor:")
            print(json.dumps(layout_response, indent=2))

    print("\n--- Pipeline Final concluído! ---")

if __name__ == "__main__":
    asyncio.run(victory_lap_extractor())

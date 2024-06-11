import flet as ft
import datetime
import requests
import webbrowser


def main(page: ft.Page):
    page.adaptive = True
    page.title = "Controle de Validade Digital"
    produtos = []

    produtos_list_view = ft.ListView(expand=1, spacing=5, padding=20, auto_scroll=True)
    produtos_list_view.adaptive = True

    def excluir_produto(index):
        produtos.pop(index)
        produtos_list_view.controls.pop(index)
        page.update()

    def limpar_tudo(e):
        produtos.clear()
        produtos_list_view.controls.clear()
        page.update()
        description.focus()

    def adc(e):
        description_value = description.value
        if not description_value:
            mostrar_snackbar("Por favor, insira uma descrição.")
            description.focus()
            return

        ean_value = ean_pdt.value
        if not ean_value:
            mostrar_snackbar("Por favor, insira um EAN válido.")
            ean_pdt.focus()
            return

        try:
            quantidade_value = int(quantidade.value)
        except ValueError:
            mostrar_snackbar("Por favor, insira a quantidade.")
            quantidade.focus()
            return

        data_value = data.value.strftime("%d/%m/%Y") if data.value else None

        produto = {
            "descrição": description_value,
            "ean": ean_value,
            "quantidade": quantidade_value,
            "validade": data_value
        }
        produtos.append(produto)

        index = len(produtos) - 1
        produtos_list_view.controls.append(
            ft.ListTile(
                title=ft.Text(f"Descrição: {description_value} | EAN: {ean_value} | Quantidade: {quantidade_value} | Validade: {data_value}"),
                trailing=ft.IconButton(
                    icon=ft.icons.DELETE,
                    on_click=lambda e, idx=index: excluir_produto(idx)
                )
            )
        )

        limpar_campos()

    def limpar_campos():
        ean_pdt.value = ""
        quantidade.value = ""
        description.value = ""
        page.update()
        description.focus()

    def mostrar_snackbar(mensagem, erro=False):
        page.snack_bar = ft.SnackBar(ft.Text(mensagem), bgcolor='red' if erro else None)
        page.snack_bar.open = True
        page.update()

    def salvar_relatorio(e):
        if not produtos:
            mostrar_snackbar("Nenhum produto para salvar.")
            return

        # Enviar os dados para o servidor Flask
        url = 'https://web-production-7ce3.up.railway.app//save_report'
        headers = {'Content-Type': 'application/json'}
        data = {"data": produtos}
        
        try:
            response = requests.post(url, json=data, headers=headers, verify=False)
            print("Status code:", response.status_code)
            print("Response content:", response.content)
            if response.status_code == 200:
                # Se a resposta foi bem-sucedida, abrir o link para fazer o download do relatório
                link_url = response.url
                webbrowser.open(link_url)
            else:
                # Se ocorreu um erro, mostrar uma mensagem de falha
                mostrar_snackbar("Falha ao salvar o relatório.", erro=True)
        except Exception as ex:
            print("Error:", ex)
            mostrar_snackbar("Erro ao enviar solicitação para o servidor.", erro=True)

    description = ft.TextField(label="Descrição", autofocus=True)
    ean_pdt = ft.TextField(label="EAN do Produto")
    quantidade = ft.TextField(label="Quantidade")
    data = ft.DatePicker(datetime.datetime.now())
    enviar = ft.TextButton(icon=ft.icons.SAVE, text="Salvar relatório", on_click=salvar_relatorio)

    page.bottom_appbar = ft.BottomAppBar(
        bgcolor=ft.colors.TRANSPARENT, content=ft.Row(controls=[enviar])
    )

    adc_button = ft.FloatingActionButton("Adicionar", on_click=adc, width=100)
    list_container = ft.Container(content=produtos_list_view, height=300, expand=True)
    botao_data = ft.ElevatedButton("Validade do Produto", icon=ft.icons.CALENDAR_MONTH, on_click=lambda _: data.pick_date())
    clean_button = ft.FloatingActionButton("Limpar Lista", on_click=limpar_tudo, width=100)

    page.add(
        ft.Column([description, ean_pdt, quantidade, botao_data,
                   ft.Row([adc_button, clean_button]), list_container,
                   ft.Container(padding=5)], expand=True)
    )

ft.app(target=main)

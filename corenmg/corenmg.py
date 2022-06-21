from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep
import csv

import corenmg.constants as const
import os
import datetime


class CorenMG(webdriver.Chrome):
    def __init__(self, teardown=False):

        self.driver_path = const.DRIVER_PATH
        self.teardown = teardown
        # self.env = const.ENV
        os.environ['PATH'] += os.pathsep + self.driver_path

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--lang=pt_BR')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-notifications")
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--incognito")
        options.add_argument("--disable-infobars")
        options.add_argument("start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")

        super(CorenMG, self).__init__(options=options)
        # super(CorenMG, self).__init__()
        self.implicitly_wait(15)
        self.maximize_window()
        # self.set_window_size(1920, 1080)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    def load_consultar_inscricao(self):
        self.get(const.BASE_URL)

    def consulta_cpf(self, cpf):
        registros = []
        self.find_element(By.XPATH, '//*[@id="formConsultarInscrito"]/label[2]').click()  # escolhe a opção CPF
        self.find_element(By.XPATH, '//*[@id="formConsultarInscrito"]/div/input[1]').send_keys(cpf)
        self.find_element(By.XPATH, '//*[@id="formConsultarInscrito"]/div/input[2]').click()

        resultado = self.find_element(By.XPATH, '//*[@id="result-consulta-inscrito"]')

        if resultado.find_element(By.TAG_NAME, 'h2').text == 'CONSULTA':  #encontrou inscrições

            nome = resultado.find_element(By.XPATH, './div/a/span').text
            registros_inscricao = self.find_elements(By.XPATH, '//*[@id="inscrito0"]/div[1]/div/div')

            for r in registros_inscricao:
                if 'active' not in r.get_attribute('class'):
                    self.find_element(By.XPATH, '//*[@id="inscrito0"]/div[2]/button[2]').click()
                    sleep(0.5)
                registro = {'cpf': cpf,
                            'nome': nome,
                            'cargo': r.find_element(By.XPATH, './li/div[1]/span').text,
                            'coren': r.find_element(By.XPATH, './li/div[2]/span').text,
                            'data_inscricao': r.find_element(By.XPATH, './li/div[3]/span').text,
                            'data_cancelamento': r.find_element(By.XPATH, './li/div[4]/span').text,
                            'status': r.find_element(By.XPATH, './li/div[5]/span').text,
                            'data_hora_atualizacao': datetime.datetime.now().strftime("%d/%m/%Y %X")
                            }

                registros.append(registro)

        else:
            registro = {'cpf': cpf,
                        'nome': '',
                        'cargo': '',
                        'coren': '',
                        'data_inscricao': '',
                        'data_cancelamento': '',
                        'status': 'NÃO ENCONTRADO'}   #resultado.find_element(By.TAG_NAME, 'h2').text.split(':')[0]}
            registros.append(registro)

        self.find_element(By.XPATH, '//*[@id="ConsultaInscrito"]/span').click()  # fecha o modal da consulta
        self.find_element(By.XPATH, '//*[@id="formConsultarInscrito"]/div/input[1]').clear()

        return registros


    def gravar_consultas(self):

        source = csv.DictReader(open('ENFERMEIROS.csv', newline='', encoding='utf-8-sig'), delimiter=';')

        with open('resultado_consulta_COREN.csv', 'w', newline='', encoding='windows-1252') as csvfilewriter:
            fields = ['cpf', 'nome', 'cargo', 'coren', 'data_inscricao', 'data_cancelamento', 'status', 'data_hora_atualizacao']
            writer = csv.DictWriter(csvfilewriter, fieldnames=fields, delimiter=';')
            writer.writeheader()

            i = 0
            for row in source:
                i += 1
                registros_incricao = self.consulta_cpf(row['CPF'])
                for r in registros_incricao:
                    writer.writerow(r)
                # strftime = datetime.now().strftime('%c')
                # print(str(i) + ' - ' + strftime)
                print(i)

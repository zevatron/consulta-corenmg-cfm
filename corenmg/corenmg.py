from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep
from random import randint
import csv
import corenmg.constants as const
import os
import datetime


class CorenMG(webdriver.Remote):
    def __init__(self, teardown=False):

        self._teardown = teardown

        options = Options()
        options.add_argument(f'user-agent={const.USERAGENTS[randint(0, len(const.USERAGENTS) - 1)]}')
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

        super(CorenMG, self).__init__(command_executor='http://127.0.0.1:4444/wd/hub',
                                      desired_capabilities=DesiredCapabilities.CHROME,
                                      options=options)

        self.implicitly_wait(15)
        self.maximize_window()
        self.set_window_size(1920, 1080)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._teardown:
            self.quit()

    def load_consultar_inscricao(self):
        self.get(const.BASE_URL)

    def alterar_user_agent(self):
        self.execute_cdp_cmd('Network.setUserAgentOverride',
                             {'userAgent': f'{const.USERAGENTS[randint(0, len(const.USERAGENTS) - 1)]}'})

    def consulta_cpf(self, cpf):
        registros = []
        self.find_element(By.XPATH, '//*[@id="form-consulta-inscrito"]/label[2]').click()  # escolhe a opção CPF
        self.find_element(By.XPATH, '//*[@id="form-consulta-inscrito"]/div/input[1]').send_keys(cpf)
        # sleep(0.5)
        self.find_element(By.XPATH, '//*[@id="form-consulta-inscrito"]/div/input[2]').click()

        encontrado = 'Resultado' in self.find_element(By.XPATH, '//*[@id="content"]/article/i').text

        if encontrado:  # encontrou inscrições

            resultado = self.find_element(By.XPATH, '//*[@id="content"]/article/div[2]')

            nome = resultado.find_element(By.XPATH, './div[1]/div[1]/b').text

            registros_inscricao = resultado.find_elements(By.CLASS_NAME, 'loop')

            for r in registros_inscricao:
                # if 'active' not in r.get_attribute('class'):
                #     self.find_element(By.XPATH, '//*[@id="inscrito0"]/div[2]/button[2]').click()
                #     sleep(0.5)
                cargo = r.find_element(By.XPATH, './div[1]').text.split('\n')
                coren = r.find_element(By.XPATH, './div[2]').text.split('\n')
                data_inscricao = r.find_element(By.XPATH, './div[3]').text.split('\n')
                data_cancelamento = r.find_element(By.XPATH, './div[4]').text.split('\n')
                status = r.find_element(By.XPATH, './div[5]').text.split('\n')

                registro = {'cpf': cpf,
                            'nome': nome,
                            'cargo': cargo[1] if len(cargo) > 1 else '',
                            'coren': coren[1] if len(coren) > 1 else '',
                            'data_inscricao': data_inscricao[1] if len(data_inscricao) > 1 else '',
                            'data_cancelamento': data_cancelamento[1] if len(data_cancelamento) > 1 else '',
                            'status': status[1] if len(status) > 1 else '',
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
                        'status': 'NÃO ENCONTRADO'}
            registros.append(registro)

        self.find_element(By.XPATH, '//*[@id="form-consulta-inscrito"]/div/input[1]').clear()
        sleep(0.5)
        return registros

    def gravar_consultas(self):

        hoje = datetime.datetime.now().strftime("%Y%m%d")

        source = csv.DictReader(open('ENFERMEIROS.csv', newline='', encoding='utf-8-sig'), delimiter=';')

        with open(f'resultado_consulta_COREN_{hoje}.csv', 'w', newline='', encoding='windows-1252') as csvfilewriter:
            fields = ['cpf', 'nome', 'cargo', 'coren', 'data_inscricao', 'data_cancelamento', 'status',
                      'data_hora_atualizacao']
            writer = csv.DictWriter(csvfilewriter, fieldnames=fields, delimiter=';')
            writer.writeheader()

            for row in source:

                result_ok = False

                while not result_ok:
                    try:
                        registros_incricao = self.consulta_cpf(row['CPF'])
                        result_ok = True
                        self.alterar_user_agent()
                    except Exception as e:
                        print(e)
                        sleep(180)
                        self.refresh()
                        self.alterar_user_agent()
                        sleep(2)
                        self.refresh()
                        self.load_consultar_inscricao()
                        sleep(5)
                        result_ok = False

                for r in registros_incricao:
                    print(r)
                    writer.writerow(r)

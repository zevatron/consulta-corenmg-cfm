from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from time import sleep
from random import randint
import datetime
import csv
import cfm.constants as const
import os


class CFM(webdriver.Remote):
    def __init__(self, teardown=False):
        self.driver_path = const.DRIVER_PATH
        self.teardown = teardown

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
        # options.add_argument("start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")

        super(CFM, self).__init__(command_executor='http://127.0.0.1:4444/wd/hub',
                                  desired_capabilities=DesiredCapabilities.CHROME,
                                  options=options)
        self.implicitly_wait(15)
        self.maximize_window()
        self.set_window_size(1920, 1080)
        self.delete_all_cookies()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    def load_buscar_medicos(self):
        self.get(const.BASE_URL)

        try:
            WebDriverWait(self, 2).until(expected_conditions.alert_is_present())
        except:
            pass
        else:
            alerta = self.switch_to.alert
            sleep(1)
            alerta.accept()

        try:
            aceita_cookie = self.find_element(By.XPATH, '//*[@id="page"]/div[4]/div[2]/button')
        except:
            pass
        else:
            aceita_cookie.click()

    def consulta_crm(self, crms, uf):
        registros = []
        crms = ','.join(crms)
        sucesso = False

        while not sucesso:
            print(crms)
            self.find_element(By.ID, "uf").find_element(By.XPATH, "//option[. = '{}']".format(uf)).click()
            sleep(1)
            input_crm = self.find_element(By.XPATH, '//*[@id="buscaForm"]/div/div[1]/div[3]/div/input')
            input_crm.clear()
            input_crm.send_keys(crms)
            self.find_element(By.XPATH, '//*[@id="buscaForm"]/div/div[4]/div[2]/button').click()
            sleep(5)
            try:
                registros_inscricao = self.find_elements(By.CLASS_NAME, "card-body")
            except Exception as e:
                print('erro na busca....')
                print(e)
                sucesso = False
                try:
                    WebDriverWait(self, 2).until(expected_conditions.alert_is_present())
                except:
                    pass
                else:
                    alerta = self.switch_to.alert
                    sleep(1)
                    alerta.accept()
            else:
                if len(registros_inscricao) > 0:
                    for r in registros_inscricao:
                        medico = {'nome': r.find_element(By.TAG_NAME, 'h4').text,
                                  'crm': r.find_element(By.XPATH, './div[1]/div[1]').text.split(': ')[1].split('-')[0],
                                  'situacao': r.find_element(By.XPATH, './div[2]/div[2]').text.split(': ')[1],
                                  'especialidade': r.find_element(By.XPATH, './div[5]/div').text.replace('\n', ' / '),
                                  'data_hora_atualizacao': datetime.datetime.now().strftime("%d/%m/%Y %X"),
                                  'uf': uf
                                  }
                        registros.append(medico)
                        print(medico)
                    sucesso = True
        return registros

    def gravar_consultas(self):

        grouped_crm = {}
        hoje = datetime.datetime.now().strftime("%Y%m%d")

        with open('MEDICOS.csv', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                crm = row['CRM']
                uf = row['UF']
                if uf not in grouped_crm.keys():
                    grouped_crm[uf] = [crm]
                else:
                    grouped_crm[uf].append(crm)

        with open(f'resultado_consulta_CFM_{hoje}.csv', 'w', newline='', encoding='windows-1252') as csvfilewriter:
            fields = ['nome', 'crm', 'uf', 'situacao', 'especialidade', 'data_hora_atualizacao']
            writer = csv.DictWriter(csvfilewriter, fieldnames=fields, delimiter=';')
            writer.writeheader()

            for uf, crms in grouped_crm.items():
                while len(crms) > 0:
                    lista10 = [crms.pop() for i in range(10) if len(crms) > 0]
                    registros_incricao = self.consulta_crm(lista10, uf)
                    for r in registros_incricao:
                        writer.writerow(r)

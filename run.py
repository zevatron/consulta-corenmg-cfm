from corenmg.corenmg import CorenMG
from cfm.cfm import CFM

with CorenMG(teardown=True) as coren:
    coren.load_consultar_inscricao()
    # coren.start_session(capabilities=DesiredCapabilities.CHROME)
    coren.gravar_consultas()

with CFM(teardown=True) as cfm:
    cfm.load_buscar_medicos()
    cfm.gravar_consultas()

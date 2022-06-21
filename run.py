from corenmg.corenmg import CorenMG
from cfm.cfm import CFM

with CorenMG(teardown=False) as coren:

    coren.load_consultar_inscricao()
    # coren.gravar_consultas()

    print(coren.consulta_cpf('05446081609'))
    # print(coren.consulta_cpf('07157259630'))
    # print("exiting....")
    # coren.consulta_CPF('01237822603')
    # sleep(5)

# with CFM(teardown=True) as cfm:
#     cfm.load_buscar_medicos()
#     cfm.gravar_consultas()

    # cfm.consulta_crm(['29824', '057332', '57149', '23236', '21403'],'MG')

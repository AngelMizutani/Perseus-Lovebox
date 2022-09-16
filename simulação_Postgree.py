import datetime
import time
import psycopg2

#Configurações da conexão do banco de dados
dbconnect = psycopg2.connect(
    host="localhost",
    database="lovebox",
    user="postgres",
    password="lovebox123")

cursor = dbconnect.cursor()

def atualizarHorario(horario_dose, tempo_alerta_especifico, id_dose):
    cursor.execute('''
        UPDATE cadastros_dosestratamento
        SET horario_dose = %s
        , tempo_alerta_especifico = %s
        WHERE id = %s;
    ''', (horario_dose, tempo_alerta_especifico, id_dose))
    dbconnect.commit()

def atualizarStatusIngestao(status_ingestao, id_dose):
    cursor.execute('''
        UPDATE cadastros_dosestratamento
        SET status_ingestao = %s
        WHERE id = %s;
    ''', (status_ingestao, id_dose))
    dbconnect.commit()

def mensagemDisplay(horario, paciente, medicamento, dosagem, unidadeMedida):
    #lcdi2c.lcd_clear()
    hora = str('Horario: ' + horario)
    pac = str('Paciente: ' + paciente)
    medicacao = str('Medic.: ' + medicamento)
    dose = str('Dosagem: ' + str(dosagem) + unidadeMedida)

    print("%s,%s,%s,%s"%(hora,pac,medicacao,dose))
    #lcdi2c.lcd_display_string(hora, 1, 0)
    #lcdi2c.lcd_display_string(pac, 2, 0)
    #lcdi2c.lcd_display_string(medicacao, 3, 0)
    #lcdi2c.lcd_display_string(dose, 4, 0)

# Atualizando o horário da medicação (para testes)
atualizarHorario('2022-09-09 15:39:00-03', 5, 1)
atualizarHorario('2022-09-09 15:29:00-03', 5, 2)

# Atualizando o status de ingestão para 0 (para testes)
atualizarStatusIngestao(False, 1)
atualizarStatusIngestao(False, 2)


# Criando um loop infinito
while(True):

    cursor.execute('SELECT * FROM cadastros_dosestratamento WHERE status_tratamento = true AND status_ingestao = false')
    dadosBD = cursor.fetchall
    
    for dadoBD in dadosBD():
        hora_atual = datetime.datetime.now().strftime("%H:%M") # Armazena o horário atual em uma variável

        # Mudando os índices dos dados do banco para deixar o código mais intuitivo
        dados = dict()
        dados['id'] = dadoBD[0]
        dados['dosagem'] = dadoBD[2]
        dados['medicamento'] = dadoBD[4]
        dados['paciente'] = dadoBD[5]
        dados['status_ingestao'] = dadoBD[6]
        dados['tempo_alerta_especifico'] = ("%s:%s"%(dadoBD[13].hour,dadoBD[13].minute+dadoBD[7]))
        dados['status_tratamento'] = dadoBD[8]
        dados['horario_dose'] = ("%s:%s"%(dadoBD[13].hour,dadoBD[13].minute))
        dados['compartimento'] = dadoBD[14]
        dados['um'] = dadoBD[15]
    
    # Se for o horário da medicação e ela não tiver sido ingerida
        if ((hora_atual == dados['horario_dose']) and (dados['status_ingestao'] == 0)):
            # Exibe a mensagem no dispaly
            mensagemDisplay(dados['horario_dose'], dados['paciente'], dados['medicamento'], dados['dosagem'], dados['um'])

            # Acende o LED do compartimento do medicamento
            #GPIO.output(ledCompartimento[(dados['compartimento'])], True)
            print("Led {} - Aceso".format(dados['compartimento']))      
            
            # Toca o alarme
            #ledAlarmeState = False
            for cont in range(0, 6):
                print("Alarme tocando")
            #    buzzState = not buzzState
            #    GPIO.output(buzzer, buzzState)

            #    ledAlarmeState = not ledAlarmeState
            #    GPIO.output(ledAlarme, ledAlarmeState)
            time.sleep(1)

            time.sleep(5)

            botao = int(input("Digite 1 se o medicamento foi tomado: "))
            if (botao == 1):
                atualizarStatusIngestao(True, dados['id']) # Status de ingestão vai para 1
                #semAlarme(dados['compartimento']) # O LED do compartimento apaga e a mensagem some
                print("Apaga botão compartimento")
                #displayMedicIngerido() # Exibe uma mensagem no display
                print("Medicamento foi ingerido")

        elif((hora_atual > dados['horario_dose']) and (hora_atual < dados['tempo_alerta_especifico']) and (dados['status_ingestao'] == 0)):
            # Exibe a mensagem no dispaly
            mensagemDisplay(hora_atual, dados['paciente'], dados['medicamento'], dados['dosagem'], dados['um'])

            # Acende o LED do compartimento do medicamento
            #GPIO.output(ledCompartimento[(dados['compartimento'])], True)
            print("Led {} - Aceso".format(dados['compartimento']))

            # Acende o LED alarme
            #ledAlarmeState = True
            #GPIO.output(ledAlarme, ledAlarmeState)
            print("Led alarme aceso")

            time.sleep(5)
            
            # Se o botão for apertado
            botao = int(input("Digite 1 se o medicamento foi tomado: "))
            if (botao == 1):
                atualizarStatusIngestao(True, dados['id']) # Status de ingestão vai para 1
                #semAlarme(dados['compartimento']) # O LED do compartimento apaga e a mensagem some
                print("Apaga botão compartimento")
                #displayMedicIngerido() # Exibe uma mensagem no display
                print("Medicamento foi ingerido")

        # Se for o horário limite para ingerir a medicação e ela não tiver sido ingerida
        elif ((hora_atual == dados['tempo_alerta_especifico']) and (dados['status_ingestao'] == 0)):
            # Exibe a mensagem no dispaly
            mensagemDisplay(dados['tempo_alerta_especifico'], dados['paciente'], dados['medicamento'], dados['dosagem'], dados['um'])

            # Acende o LED do compartimento do medicamento
            #GPIO.output(ledCompartimento[(dados['compartimento'])], True)
            print("Led {} - Aceso".format(dados['compartimento']))
            
            # Toca o alarme
            #ledAlarmeState = False
            for cont in range(0, 6):
                print("Alarme tocando")
            #    buzzState = not buzzState
            #    GPIO.output(buzzer, buzzState)

            #    ledAlarmeState = not ledAlarmeState
            #    GPIO.output(ledAlarme, ledAlarmeState)
                time.sleep(1)


            time.sleep(5)

        # Se o botão for pressionado
            botao = int(input("Digite 1 se o medicamento foi tomado: "))
            if (botao == 1):
                atualizarStatusIngestao(True, dados['id']) # Status de ingestão vai para 1
                #semAlarme(dados['compartimento']) # O LED do compartimento apaga e a mensagem some
                print("Apaga botão compartimento")
                #displayMedicIngerido() # Exibe uma mensagem no display
                print("Medicamento foi ingerido")

            time.sleep(5)

        elif ((hora_atual > dados['tempo_alerta_especifico']) and (dados['status_ingestao'] == 0)):
            #semAlarme(dados['compartimento']) # O LED do compartimento apaga e a mensagem some
            print("Alarme desligado e mensagem apagada!")
            time.sleep(5)

    time.sleep(10)
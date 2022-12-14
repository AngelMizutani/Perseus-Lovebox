# Importando as bibliotecas
import RPi.GPIO as GPIO
import time
import datetime
import psycopg2
import I2C_LCD_driver


# Definindo como configurar a GPIO (físico)
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)


# Definindo os pinos dos componentes
ledAlarme = int(40)
ledCompartimento = [int(38), int(36)]
buzzer = int(32)
botao = int(26)


# Definindo os pinos dos LED's e do buzzer como saídas
GPIO.setup(ledAlarme, GPIO.OUT)
for compartimento in range(0,2):
    GPIO.setup(ledCompartimento[compartimento], GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT)


# Definindo o pino do botão como entrada
GPIO.setup(botao, GPIO.IN)


# Configurações iniciais do bando de dados, do I2C, do buzzer e do LED de alarme
dbconnect = psycopg2.connect(
    host="localhost",
    database="lovebox",
    user="postgres",
    password="lovebox123")

cursor = dbconnect.cursor()
lcdi2c = I2C_LCD_driver.lcd()
buzzState = False
ledAlarmeState = False


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

def mensagemDisplay(horario, paciente, medicamento, dosagem, unidade_medida):
    lcdi2c.lcd_clear()
    hora = str('Horario: ' + horario)
    pac = str('Paciente: ' + paciente)
    medicacao = str('Medic.: ' + medicamento)
    dose = str('Dosagem: ' + str(dosagem) + unidade_medida)

    lcdi2c.lcd_display_string(hora, 1, 0)
    lcdi2c.lcd_display_string(pac, 2, 0)
    lcdi2c.lcd_display_string(medicacao, 3, 0)
    lcdi2c.lcd_display_string(dose, 4, 0)

def semAlarme(compartimento):
    lcdi2c.lcd_clear()
    GPIO.output(ledCompartimento[compartimento], False)
    ledAlarmeState = False
    GPIO.output(ledAlarme, ledAlarmeState)

def displayMedicIngerido():
    lcdi2c.lcd_clear()
    lcdi2c.lcd_display_string('Medicamento ingerido', 2, 0)
    time.sleep(3)
    lcdi2c.lcd_clear()


# Atualizando o horário da medicação (para testes)
atualizarHorario('2022-09-09 15:39:00-03', 5, 1)
atualizarHorario('2022-09-09 15:29:00-03', 5, 2)


# Atualizando o status de ingestão para 0 (para testes)
atualizarStatusIngestao(False, 1)
atualizarStatusIngestao(False, 2)


# Criando um loop infinito
while(True):
    # Selecionando os dados do banco de dados
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
            GPIO.output(ledCompartimento[(dados['compartimento'])], True)            
            
            # Toca o alarme
            ledAlarmeState = False
            for cont in range(0, 6):
                buzzState = not buzzState
                GPIO.output(buzzer, buzzState)

                ledAlarmeState = not ledAlarmeState
                GPIO.output(ledAlarme, ledAlarmeState)
                time.sleep(1)

            time.sleep(5)

            # Se o botão for apertado
            if (GPIO.input(botao) == True):
                atualizarStatusIngestao(True, dados['id']) # Status de ingestão vai para 1
                semAlarme(dados['compartimento']) # O LED do compartimento apaga e a mensagem some
                displayMedicIngerido() # Exibe uma mensagem no display
        
        
        # Se estiver no intervalo do tempo de ingestão e a medicação não tiver sido ingerida
        elif((hora_atual > dados['horario_dose']) and (hora_atual < dados['tempo_alerta_especifico']) and (dados['status_ingestao'] == 0)):
            # Exibe a mensagem no dispaly
            mensagemDisplay(hora_atual, dados['paciente'], dados['medicamento'], dados['dosagem'], dados['um'])

            # Acende o LED do compartimento do medicamento
            GPIO.output(ledCompartimento[(dados['compartimento'])], True)

            # Acende o LED alarme
            ledAlarmeState = True
            GPIO.output(ledAlarme, ledAlarmeState)

            time.sleep(5)
            
            # Se o botão for apertado
            if (GPIO.input(botao) == True):
                atualizarStatusIngestao(True, dados['id']) # Status de ingestão vai para 1
                semAlarme(dados['compartimento']) # O LED do compartimento apaga e a mensagem some
                displayMedicIngerido() # Exibe uma mensagem no display
        
        
        # Se for o horário limite para ingerir a medicação e ela não tiver sido ingerida
        elif ((hora_atual == dados['tempo_alerta_especifico']) and (dados['status_ingestao'] == 0)):
            # Exibe a mensagem no dispaly
            mensagemDisplay(dados['tempo_alerta_especifico'], dados['paciente'], dados['medicamento'], dados['dosagem'], dados['um'])

            # Acende o LED do compartimento do medicamento
            GPIO.output(ledCompartimento[(dados['compartimento'])], True)
            
            # Toca o alarme
            ledAlarmeState = False
            for cont in range(0, 6):
                buzzState = not buzzState
                GPIO.output(buzzer, buzzState)

                ledAlarmeState = not ledAlarmeState
                GPIO.output(ledAlarme, ledAlarmeState)
                time.sleep(1)

            time.sleep(5)

            # Se o botão for pressionado
            if (GPIO.input(botao) == True):
                atualizarStatusIngestao(True, dados['id']) # Status de ingestão vai para 1
                semAlarme(dados['compartimento']) # O LED do compartimento apaga e a mensagem some
                displayMedicIngerido() # Exibe uma mensagem no display


        # Se a medicação não tiver sido ingerida dentro do tempo limite
        elif ((hora_atual > dados['tempo_alerta_especifico']) and (dados['status_ingestao'] == 0)):
            semAlarme(dados['compartimento']) # O LED do compartimento apaga e a mensagem some
            time.sleep(5)

     
    time.sleep(10)
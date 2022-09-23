# Importando as bibliotecas
import RPi.GPIO as GPIO
import time
import datetime
import I2C_LCD_driver

executar = True
statusIngestao = 0
contador = 0

# Definindo como configurar a GPIO (físico)
# GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


# Definindo os pinos dos componentes
# ledAlarme = int(40)
ledAlarme = 13
# ledCompartimento = [int(38), int(36)]
ledCompartimento = [12, 5]
# buzzer = int(32)
buzzer = 23
# botao = int(22)
botao = 26


# Definindo os pinos dos LED's e do buzzer como saídas
GPIO.setup(ledAlarme, GPIO.OUT)
for compartimento in range(0,2):
    GPIO.setup(ledCompartimento[compartimento], GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT)


# Definindo o pino do botão como entrada
GPIO.setup(botao, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Configurações iniciais do I2C, do buzzer e do LED de alarme
lcdi2c = I2C_LCD_driver.lcd()
buzzState = False
ledAlarmeState = False


def exibirMensagem(horario, paciente, medicamento, dosagem, unidadeMedida):
    hora = str('Horario: ' + horario)
    pac = str('Paciente: ' + paciente)
    medicacao = str('Medic.: ' + medicamento)
    dose = str('Dosagem: ' + str(dosagem) + ' ' + unidadeMedida)

    lcdi2c.lcd_clear()
    lcdi2c.lcd_display_string(hora, 1, 0)
    lcdi2c.lcd_display_string(pac, 2, 0)
    lcdi2c.lcd_display_string(medicacao, 3, 0)
    lcdi2c.lcd_display_string(dose, 4, 0)

def dispararAlarme():
    buzzState = False
    ledAlarmeState = False
    for cont in range(0, 6):
        # buzzState = not buzzState
        # GPIO.output(buzzer, buzzState)

        ledAlarmeState = not ledAlarmeState
        GPIO.output(ledAlarme, ledAlarmeState)
        time.sleep(1)
    time.sleep(3)

def semAlarme(compartimento):
    time.sleep(3)
    lcdi2c.lcd_clear()
    GPIO.output(ledCompartimento[compartimento], False)

def sair(channel):
    lcdi2c.lcd_clear()
    lcdi2c.lcd_display_string("Saindo...", 1, 0)
    # time.sleep(1)

    lcdi2c.lcd_clear()
    lcdi2c.backlight(0)
    executar = False

# Criando um loop infinito
while(executar):
    
    lcdi2c.lcd_display_string("Pressione o botao para simular", 1, 0)
    # time.sleep(1)

    if (GPIO.input(botao) == False):
        statusIngestao = 0
        horario = datetime.datetime.now().strftime("%H:%M")

        while (statusIngestao == 0 and contador < 3):
            exibirMensagem(horario, 'Maria', 'Losartana', '1','comp')
            GPIO.output(ledCompartimento[0], True)
            dispararAlarme()
            
            if (GPIO.input(botao) == False):
                lcdi2c.lcd_clear()
                lcdi2c.lcd_display_string("Medicamento ingerido", 1, 0)
                # time.sleep(1)
                statusIngestao = 1
                contador = 0
                semAlarme(0)
            
            contador+=1

        if (statusIngestao == 0 and contador >= 3):
            semAlarme(0)
            lcdi2c.lcd_clear()
            lcdi2c.lcd_display_string("Paciente atrasou medicacao", 1, 0)
            contador = 0
            # time.sleep(2)

        lcdi2c.lcd_clear()
        lcdi2c.lcd_display_string("Pressione para sair...", 1, 0)
        # time.sleep(1)

        GPIO.add_event_detect(botao, GPIO.FALLING, callback=sair, bouncetime=2000)

        # if (GPIO.input(botao) == False):
        #     lcdi2c.lcd_clear()
        #     lcdi2c.lcd_display_string("Saindo...", 1, 0)
        #     # time.sleep(1)

        #     lcdi2c.lcd_clear()
        #     lcdi2c.backlight(0)
        #     executar = False
        time.sleep(1)
    time.sleep(2)

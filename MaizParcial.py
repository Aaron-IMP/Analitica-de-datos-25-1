import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

from selenium.webdriver.chrome.options import Options #SIRVE PARA CHROME DRIVER

from selenium.webdriver.common.by import By  

#SIRVE PARA PODER ESPERAR A QUE LA PAGINA CARGUE
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
import os
import pandas as pd


def iniciar_chrome():


    ruta = ChromeDriverManager().install() #AÑADIMOS LOG_LEVEL PARA UNA SALIDA LIMPIA EN LA TERMINAL

    #OPCIONES DE CHGROME
    options = Options()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}") #DEFINE EL AGENTE PERSONALIZADO
    options.add_argument("--disable-web-security") #Esto es útil cuando estás haciendo scraping o automatización en sitios donde necesitas interactuar con recursos externos (CDN, APIs, iframes, etc.).
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications") #BLOQUE LAS NOTIFICACIONES DE CHROME
    options.add_argument("--ignore-certificate-errors") #SIRVE PARA QUE NO NOS MUESTRE: ERROR SU CONEXION NO ES PRIVADA
    #options.add_argument("--no-sandbox") # NO USAR SI SON SITIOS VULNERABLES
    options.add_argument("--allow-running-insecure-content") # DESACTIVA EL AVISO "NO SEGURO"
    options.add_argument("--no-default-browser-check") # DESACTIVA EL AVISO "CHROME NO ES EL NAVEGADOR PREDETERMINADO"
    options.add_argument("--no-proxy-server") 
    options.add_argument("--disable-blink-features=AutomationControlled") # evitar que las páginas web detecten que estás usando Selenium
    

    
    options.add_argument("--headless") #IDEAL PARA CUANDO NO QUEREMOS QUE SE ABRA EL CHROME AL MANDAR EL CODIGO

    """
    Especificar una carpeta de descarga
    
    prefs = {"download.default_directory": "/path/to/folder"}
    options.add_experimental_option("prefs", prefs)
    
    """
    # PARAMETROS PARA OMITIR EN EL INCIIO DE CHROMEDRIVER
    exp_opt = [
        "enable-automation", #PARA QUE NO MUESTRE LA NOTIFICACION
        "ignore-certificate-errors", #PARA IGNORAR ERRORES DE CERTIFICADOS
        "enable-logging" #PARA Q NO SE MUESTRE EN LA TERMINAL DEVTOOLS LISTENING ON
    ]
    options.add_experimental_option("excludeSwitches", exp_opt)

    # PARAMETROS QUE DEFINEN PREFERENCIAS DEL CHROMEDRIVER
    prefs = {
        "profile.default_content_setting_values.notifications" : 2, # NOTIFICACIONES: 0 = preguntar, 1 = permitir, 2 = no permitir 
        "credentials_enable_service": False # para evitar que chrome nos diga si queremos guardar la contra
    }
    options.add_experimental_option("prefs", prefs)

    s = Service(ruta) #INSTANCIAMOS EL SERVICIO CHROMEDRIVER

    driver = webdriver.Chrome(service=s, options=options) # AÑADIMOS LAS OPCIONES

    return driver

if __name__ == "__main__":
    driver = iniciar_chrome()
    url = "https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PN01685PM/html"
    driver.get(url)

    #OBTENIENDO LOS HEADERS DE LA TABLA
    wait = WebDriverWait(driver, 10)
    #PULSANDO EL ULTIMO MES
    boton_mes = wait.until(EC.presence_of_element_located((By.ID, 'mes2')))
    # boton_mes.click()
    pulsar_mes_dic = boton_mes.find_elements(By.TAG_NAME,"option")
    pulsar_mes_dic[-1].click()

    #PULSANDO EL ULTIMO AÑO
    boton_anio = wait.until(EC.presence_of_element_located((By.ID, 'anio2')))
    pulsar_ultimo_anio = boton_anio.find_elements(By.TAG_NAME,"option")
    pulsar_ultimo_anio[0].click()

    boton_actualizar = wait.until(EC.presence_of_element_located((By.ID,"btnBuscar")))
    boton_actualizar.click()
    time.sleep(1)
    div_tabla = wait.until(EC.presence_of_element_located((By.CLASS_NAME,"barra-resultados")))
    
    tr_div_tabla = div_tabla.find_elements(By.TAG_NAME,"tr")
    tabla_completa = []
    header = ["Fecha","Precios de productos sujetos al sistema de franjas de precios (US$ por toneladas) - Maíz"]
    num = 0
    for i in tr_div_tabla:
        if(num == 0):
            num = num+1
            continue
        else:
            texto = i.text.split(" ")
            tabla_completa.append(texto)
    #print(tabla_completa)
    #input("Enter para cerrar")
    driver.quit()
    """
    # Creamos un DataFrame con nombres de columnas
    df = pd.DataFrame(tabla_completa, columns=header)

    # Exportamos el DataFrame a un archivo CSV
    df.to_csv('datos_mensuales.csv', index=False, encoding='utf-8')

    print("Archivo CSV creado exitosamente.")
    """
    #print(tabla_completa)
    conjunto = set()
    for i in tabla_completa:
        sufijo = i[0][-2:]  # Extrae los dos últimos caracteres
        conjunto.add(sufijo)
    lista_ordenada_conjunto = sorted(conjunto)
    
    cantidad_columnas = len(lista_ordenada_conjunto)
    #TABLA POR FECHAS
    tabla_por_fechas = []
    for i in range(cantidad_columnas):
        tabla_por_fechas.append([])
    indice = 0
    indice_tabla_fechas = 0
    for i,j in enumerate(lista_ordenada_conjunto):
        for m in tabla_completa:
            if (m[0][-2:] == j):
                tabla_por_fechas[i].append(m)
    """
    for i in tabla_por_fechas:
        print("tabla")
        print(i)
        print("\n")
    
    """
    
    # Ruta base donde guardarás tus carpetas de datos
    ruta_base = "datos_maiz_por_anio"
    os.makedirs(ruta_base, exist_ok=True)

    # Recorremos cada subtabla (por año) y guardamos
    for subtabla in tabla_por_fechas:
        if not subtabla:
            continue  # saltar si está vacía

        # Obtener el año del primer registro (por ejemplo, 'Ene-21' → '2021')
        fecha = subtabla[0][0]
        if fecha[-2:] > "91":
            anio = "19" + fecha[-2:]  # '92' → '1992'
        else:
            anio = "20" + fecha[-2:]  # '21' → '2021'
    
        # Crear carpeta del año si no existe
        ruta_carpeta = os.path.join(ruta_base, anio)
        os.makedirs(ruta_carpeta, exist_ok=True)
    
        # Crear DataFrame y guardar como CSV
        df = pd.DataFrame(subtabla, columns=header)
        ruta_csv = os.path.join(ruta_carpeta, f"datos_{anio}.csv")
        df.to_csv(ruta_csv, index=False, encoding='utf-8')
    
        #print(f"Guardado: {ruta_csv}")
import os
import fitz
import re
import csv
from datetime import datetime
import locale    

def writeResults(rows):
    with open('resultados.csv', mode='w', newline='') as resultsFile:
        resultsWriter = csv.writer(resultsFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)        
        resultsWriter.writerows(rows)

def readBiofast(doc, rows):
    for results in doc:
        pdfString = results.getText()
        personName = re.search(r'Nombre \.\.\.\.: (.*?)\nCodigo', pdfString, re.DOTALL).group(1)

        testDate = re.search(r'Validación: (.*?202[0-9])', pdfString).group(1)
        testDate = datetime.strptime(testDate, '%d/%m/%Y').strftime("%d-%m-%Y")

        pId = re.search(r'CI \.\.\.\.\.:\n([0-9]{8})\n \nProcedencia', pdfString).group(1)
        personId = f'{pId[0]}.{pId[1:4]}.{pId[4:7]}-{pId[7]}'

        testResult = 'Positvo' if "POSITIVO" in pdfString else 'Negativo'
        rows.append([personId, personName.casefold(), testDate, testResult])


def readGenia(pdfString, rows):
    personName = re.search(r'202.\n(.*?)\nS/D', pdfString, re.DOTALL).group(1)

    testDate = re.search(r'(.*?202[0-9])', pdfString).group(1)
    testDate = datetime.strptime(testDate, '%d de %B del %Y').strftime("%d-%m-%Y")

    personId = re.search(r'[0-9]{1}\.[0-9]{3}\.[0-9]{3}-[0-9]', pdfString).group(0)
    testResult = 'Positvo' if "Se detectó la presencia de SARS-CoV-2 en la muestra analizada." in pdfString else 'Negativo'
    rows.append([personId, personName.casefold(), testDate, testResult])


def readATgen(pdfString, rows):
    personName = re.search(r'Pac. : (.*?)\nDoc.', pdfString, re.DOTALL).group(1)

    testDate = re.search(r'Fecha\n: (.*?202[0-9])', pdfString).group(1)
    testDate = datetime.strptime(testDate, '%d/%m/%Y').strftime("%d-%m-%Y")

    pId = re.search(r'Doc. : ([0-9]{8})\nF.Nac:', pdfString).group(1)
    personId = f'{pId[0]}.{pId[1:4]}.{pId[4:7]}-{pId[7]}'

    testResult = 'Positvo' if "Se detecta la presencia de ARN de SARS-CoV-2." in pdfString else 'Negativo'
    rows.append([personId, personName.casefold(), testDate, testResult])
    

def main():
    locale.setlocale(locale.LC_ALL, "es_UY.utf8")
    rows = []
    for filename in os.listdir(os.getcwd()):
        if ".pdf" in filename:
            doc = fitz.open(filename)
            pdfString = doc.loadPage(0).getText("text")

            labName = re.search(r'www.(.*?).com.uy|laboratorio(.*?).com| www.(.*?).com.uy ', pdfString)

            #PARA IMPRIMIR RESULTADOS DE BIOFAST
            if labName.group(1) == 'biofast':
                readBiofast(doc, rows)

            #PARA IMPRIMIR RESULTADOS DE GENIA
            elif labName.group(2) == 'genia':
                readGenia(pdfString, rows)
            
            #PARA IMPRIMIR RESULTADOS DE ATGEN
            elif labName.group(3) == "atgen":
                readATgen(pdfString, rows)

    writeResults(rows)
        

if __name__ == "__main__":
    main()

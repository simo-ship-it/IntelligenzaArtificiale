import cv2
import pytesseract

# Configurazione per Tesseract (Assicurati che Tesseract sia installato nel sistema)
# Su Windows, specifica il percorso di Tesseract:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def remove_table_borders(image):
    # Converti l'immagine in scala di grigi
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Applica la soglia per ottenere un'immagine binaria
    _, binary_image = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Rimuovi le linee orizzontali e verticali
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
    remove_horizontal = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
    remove_vertical = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

    # Sottrai le linee dall'immagine binaria
    borders_removed = binary_image - remove_horizontal - remove_vertical

    # Inverti l'immagine
    borders_removed = cv2.bitwise_not(borders_removed)

    return borders_removed

def extract_and_organize_text(image):
    # Utilizza pytesseract per estrarre il testo e le coordinate dei box
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(image, config=custom_config)
    
    # Organizza il testo per riga
    lines = text.splitlines()
    cleaned_lines = [line.strip() for line in lines if line.strip()]  # Rimuovi spazi vuoti e linee vuote
    
    return cleaned_lines

def main(image_path):
    # Leggi l'immagine con OpenCV
    image = cv2.imread(image_path)

    # Rimuovi i bordi della tabella
    processed_image = remove_table_borders(image)

    # Estrai e organizza il testo
    sorted_rows = extract_and_organize_text(processed_image)

    # Crea un array per memorizzare i risultati
    result_array = []

    # Stampa le righe estratte con un "-" alla fine e aggiungi all'array
    print("Contenuto della tabella riconosciuto:")
    for row in sorted_rows:
        # formatted_row = row + " -"
        print(row)
        result_array.append(row)
        result_array = [elemento.replace(" ", "") for elemento in result_array] # Rimuovi gli spazi vuoti tra le lettere

    # Puoi ora utilizzare result_array come desideri
    print("\nArray dei risultati:", result_array)
    # print("\n Primo elemento seconda lettera: ", result_array[0][1]) # esempio per stampare il secondo carattere della prima riga

if __name__ == "__main__":
    # Specifica il percorso dell'immagine da elaborare
    image_path = 'bordi.png'  # Sostituisci con il percorso della tua immagine

    # Esegui il programma
    main(image_path)

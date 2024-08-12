import cv2
import pytesseract

# Configurazione per Tesseract (Assicurati che Tesseract sia installato nel sistema)
# Su Windows, specifica il percorso di Tesseract:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image_path):
    # Leggi l'immagine con OpenCV
    img = cv2.imread(image_path)

    # Converti l'immagine in scala di grigi
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Applica la soglia per ottenere un'immagine binaria
    _, binary_image = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Facoltativo: Rimuovi il rumore e applica dilatazione o erosione
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    processed_image = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)

    return img, processed_image

def extract_text_and_boxes(processed_image):
    # Utilizza pytesseract per estrarre il testo e le coordinate dei box
    custom_config = r'--oem 3 --psm 6'
    boxes = pytesseract.image_to_boxes(processed_image, config=custom_config)
    return boxes

def organize_text_by_rows(boxes):
    rows = {}
    for box in boxes.splitlines():
        box = box.split(' ')
        char = box[0]
        x, y, x2, y2 = int(box[1]), int(box[2]), int(box[3]), int(box[4])
        row = y2 // 10  # raggruppa per riga usando la coordinata y superiore
        if row not in rows:
            rows[row] = []
        rows[row].append((x, char))
    
    # Ordina le righe e i caratteri all'interno di ciascuna riga
    sorted_rows = []
    for row in sorted(rows.keys(), reverse=True):  # Ordinamento inverso poiché le coordinate y sono dall'alto in basso
        sorted_row = sorted(rows[row], key=lambda item: item[0])
        sorted_rows.append(''.join([char for _, char in sorted_row]))
    
    return sorted_rows

def main(image_path):
    # Pre-processa l'immagine
    original_image, processed_image = preprocess_image(image_path)

    # Estrai i box delle lettere dall'immagine pre-processata
    boxes = extract_text_and_boxes(processed_image)

    # Organizza le lettere riga per riga
    sorted_rows = organize_text_by_rows(boxes)

    # Stampa le righe con "-" alla fine di ciascuna riga
    print("Testo organizzato per righe:")
    for row in sorted_rows:
        print(row + "-")

    # Facoltativo: puoi mantenere la parte di visualizzazione e salvataggio dell'immagine

if __name__ == "__main__":
    # Specifica il percorso dell'immagine da elaborare
    image_path = 'test_image.png'  # Sostituisci con il percorso della tua immagine

    # Esegui il programma
    main(image_path)

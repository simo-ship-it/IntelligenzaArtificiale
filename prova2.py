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
    text = pytesseract.image_to_string(processed_image, config=custom_config)
    boxes = pytesseract.image_to_boxes(processed_image, config=custom_config)
    return text, boxes

def draw_boxes(image, boxes):
    h, w, _ = image.shape
    for box in boxes.splitlines():
        box = box.split(' ')
        x, y, x2, y2 = int(box[1]), int(box[2]), int(box[3]), int(box[4])
        # Calcola il centro del box per disegnare il cerchio
        center_x = (x + x2) // 2
        center_y = h - (y + y2) // 2  # Inverti y perché OpenCV ha origine in alto a sinistra
        radius = max((x2 - x) // 2, (y2 - y) // 2)
        # Disegna un cerchio rosso attorno alla lettera
        cv2.circle(image, (center_x, center_y), radius, (0, 0, 255), 2)
    return image

def main(image_path):
    # Pre-processa l'immagine
    original_image, processed_image = preprocess_image(image_path)

    # Estrai il testo e i box dall'immagine pre-processata
    text, boxes = extract_text_and_boxes(processed_image)

    # Stampa il testo riconosciuto
    print("Testo riconosciuto:")
    print(text)

    # Disegna i box (cerchi) sull'immagine originale
    image_with_boxes = draw_boxes(original_image, boxes)

    # Mostra l'immagine con le lettere cerchiate
    cv2.imshow('Lettere riconosciute', image_with_boxes)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Salva l'immagine risultante
    output_path = 'output_image.png'
    cv2.imwrite(output_path, image_with_boxes)
    print(f"Immagine salvata come {output_path}")

if __name__ == "__main__":
    # Specifica il percorso dell'immagine da elaborare
    image_path = 'test_image.png'  # Sostituisci con il percorso della tua immagine

    # Esegui il programma
    main(image_path)

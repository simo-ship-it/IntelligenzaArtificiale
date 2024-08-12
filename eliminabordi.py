import cv2
import numpy as np

def remove_table_borders(image_path, output_path):
    # Carica l'immagine a colori
    img = cv2.imread(image_path)
    # Converti in scala di grigi
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Applica una soglia binaria inversa per evidenziare le righe nere
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
    
    # Usa un kernel per rilevare le linee orizzontali e verticali
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    
    # Rileva le linee orizzontali
    detect_horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)
    # Rileva le linee verticali
    detect_vertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)
    
    # Combina le linee orizzontali e verticali
    table_borders = cv2.add(detect_horizontal, detect_vertical)
    
    # Dilata i bordi per assicurarti che coprano completamente le righe della tabella
    dilated_borders = cv2.dilate(table_borders, np.ones((3, 3), np.uint8), iterations=1)
    
    # Crea una maschera inversa per selezionare le linee della tabella
    table_borders_inv = cv2.bitwise_not(dilated_borders)
    
    # Copre le linee della tabella con bianco
    img[table_borders == 255] = [255, 255, 255]
    
    # Salva l'immagine risultante
    cv2.imwrite(output_path, img)

# Esempio di utilizzo
input_image = 'bordi.png'  # Usa il nome dell'immagine che hai
output_image = 'test_image.png'  # Specifica il nome dell'immagine di output
remove_table_borders(input_image, output_image)

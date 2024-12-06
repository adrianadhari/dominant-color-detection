import cv2
import numpy as np
from sklearn.cluster import KMeans
from colormath.color_objects import LabColor
from colormath.color_diff import delta_e_cie2000
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64

# Fungsi untuk segmentasi gambar menggunakan metode GrabCut
def segment_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    _, mask = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)

    mask[mask == 255] = cv2.GC_FGD
    mask[mask == 0] = cv2.GC_BGD
    rect = (10, 10, image.shape[1] - 10, image.shape[0] - 10)

    try:
        cv2.grabCut(image, mask, rect, np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64), 5, cv2.GC_INIT_WITH_RECT)
        mask = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        return image * mask[:, :, np.newaxis]
    except Exception:
        return image  # Jika terjadi kesalahan, kembalikan gambar asli

# Fungsi untuk menghitung perbedaan warna menggunakan model CIEDE2000
def color_difference(color1, color2):
    lab1 = LabColor(lab_l=color1[0], lab_a=color1[1], lab_b=color1[2])
    lab2 = LabColor(lab_l=color2[0], lab_a=color2[1], lab_b=color2[2])
    return delta_e_cie2000(lab1, lab2)

# Fungsi untuk menyaring dan mengurutkan warna dominan
def filter_and_sort_colors(colors, threshold=10):
    filtered_colors = []
    for color in colors:
        if all(color_difference(color, c) > threshold for c in filtered_colors):
            filtered_colors.append(color)
    return filtered_colors

# Konfigurasi aplikasi Flask
app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_image():
    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    image_data = np.frombuffer(file.read(), np.uint8)
    image = cv2.cvtColor(cv2.imdecode(image_data, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)

    # Proses segmentasi
    segmented_image = segment_image(image)

    # Ambil piksel untuk clustering
    pixels = segmented_image[segmented_image.sum(axis=-1) > 0].reshape((-1, 3)).astype(np.float32)

    # Deteksi warna dominan
    kmeans = KMeans(n_clusters=1, random_state=42).fit(pixels)
    dominant_colors = kmeans.cluster_centers_.astype(int).tolist()

    # Filter warna dominan
    sorted_colors = filter_and_sort_colors(dominant_colors)

    # Konversi gambar ke format base64
    original_image_base64 = base64.b64encode(cv2.imencode('.png', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))[1]).decode('utf-8')
    segmented_image_base64 = base64.b64encode(cv2.imencode('.png', cv2.cvtColor(segmented_image, cv2.COLOR_RGB2BGR))[1]).decode('utf-8')

    return jsonify({
        'dominant_colors': sorted_colors,
        'original_image_base64': original_image_base64,
        'segmented_image_base64': segmented_image_base64
    })

if __name__ == '__main__':
    app.run(debug=True)

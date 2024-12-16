import { useState } from "react";
import axios from "axios";

function App() {
  const [originalImage, setOriginalImage] = useState(null);
  const [segmentedImage, setSegmentedImage] = useState(null);
  const [dominantColors, setDominantColors] = useState(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false); // State untuk loading

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async () => {
    if (!file) return;

    setLoading(true); // Aktifkan loading

    const formData = new FormData();
    formData.append("imag e", file);

    try {
      const response = await axios.post("https://pc.adrianadhari.my.id/api/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setOriginalImage(`data:image/png;base64,${response.data.original_image_base64}`);
      setSegmentedImage(`data:image/png;base64,${response.data.segmented_image_base64}`);
      setDominantColors(response.data.dominant_colors);
    } catch (error) {
      console.error("Error uploading image:", error);
    } finally {
      setLoading(false); // Matikan loading setelah proses selesai
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="p-6 bg-white shadow-lg rounded-lg">
        <h1 className="text-2xl font-bold text-gray-700 mb-4">
          Dominant Color Detection
        </h1>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="block mb-4"
        />
        <button
          onClick={handleSubmit}
          className={`bg-blue-500 text-white px-4 py-2 rounded ${
            loading ? "opacity-50 cursor-not-allowed" : ""
          }`}
          disabled={loading} // Nonaktifkan tombol jika sedang loading
        >
          {loading ? "Processing..." : "Submit"}
        </button>

        {/* Indikator Loading */}
        {loading && (
          <div className="flex justify-center items-center mt-4">
            <div className="w-16 h-16 border-t-4 border-blue-500 border-solid rounded-full animate-spin"></div>
            <p className="ml-4 text-gray-600">Processing your image...</p>
          </div>
        )}


        <div className="flex space-x-4 mt-4">
          {originalImage && (
            <div>
              <h2 className="text-lg font-semibold mb-2">Original Image</h2>
              <img
                src={originalImage}
                alt="Original"
                className="w-48 h-48 object-contain border"
              />
            </div>
          )}
          {segmentedImage && (
            <div>
              <h2 className="text-lg font-semibold mb-2">Segmented Image</h2>
              <img
                src={segmentedImage}
                alt="Segmented"
                className="w-48 h-48 object-contain border"
              />
            </div>
          )}
          {dominantColors && (
            <div>
              <h2 className="text-lg font-semibold mb-2">Dominant Colors</h2>
              <div className="flex space-x-2">
                {dominantColors.map((color, index) => (
                  <div
                    key={index}
                    className="w-16 h-16 border"
                    style={{ backgroundColor: `rgb(${color.join(",")})` }}
                  />
                ))}
              </div>
              <p className="text-gray-600 mt-2">
                RGB Values:{" "}
                {dominantColors.map((color) => color.join(", ")).join(" | ")}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;

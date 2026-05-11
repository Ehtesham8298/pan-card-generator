# PAN Card Generator

A Flask web application that generates filled PAN Card PDFs from user-submitted form data.

## Features

- Upload passport-size photo (auto center-cropped, HDR enhanced)
- Enter PAN Number, Full Name, Father's Name, Date of Birth
- Upload Signature image (auto enhanced)
- All data is placed at exact positions on the PAN Card PDF
- Downloads a premium quality filled PDF instantly

## Screenshots

| Form UI | Generated PDF |
|---------|--------------|
| Dark glassmorphism premium form | Ultra quality filled PAN Card PDF |

## Tech Stack

- **Backend:** Python, Flask
- **PDF Processing:** PyMuPDF (fitz)
- **Image Processing:** Pillow (PIL)
- **Frontend:** HTML, CSS (Glassmorphism), Flatpickr (date picker)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Ehtesham8298/pan-card-generator.git
   cd pan-card-generator
   ```

2. Install dependencies:
   ```bash
   pip install flask pymupdf pillow
   ```

3. Run the app:
   ```bash
   python pan_form.py
   ```

4. Open browser and go to:
   ```
   http://localhost:5000
   ```

## Usage

1. Open `http://localhost:5000` in your browser
2. Upload applicant photo
3. Enter PAN Number (10 characters)
4. Enter Full Name
5. Enter Father's Name
6. Select Date of Birth
7. Upload Signature image
8. Click **Generate PAN Card PDF**
9. PDF will be downloaded automatically

## Requirements

```
flask
pymupdf
pillow
```

## Project Structure

```
pan-card-generator/
├── pan_form.py          # Main Flask application
├── Pan Card Output2.pdf # PAN Card template (photo & signature removed)
└── README.md
```

## Notes

- The template PDF (`Pan Card Output2.pdf`) has the photo and signature area cleared
- New photo and signature are placed at exact coordinates
- Text is placed at calibrated positions matching original PAN card layout

## License

MIT License

from flask import Flask, request, send_file, render_template_string
import fitz
from PIL import Image, ImageEnhance, ImageFilter
import io, os

app = Flask(__name__)

TEMPLATE_PDF  = os.path.join(os.path.dirname(__file__), "templates", "Pan Card Output2.pdf")

PHOTO_RECT    = fitz.Rect(18.5, 68.0, 65.5, 115.2)
NAME_POS      = (24, 135)
FATHER_POS    = (24, 156)
DOB_POS       = (24, 183)
PAN_NUM_POS   = (103, 101)
SIGN_RECT     = fitz.Rect(109.077, 157.966, 156.982, 176.391)

FONT_SIZE     = 6.5
PAN_FONT_SIZE = 8

def enhance_photo_hdr(pil_img):
    pil_img = ImageEnhance.Sharpness(pil_img).enhance(2.2)
    pil_img = ImageEnhance.Contrast(pil_img).enhance(1.25)
    pil_img = ImageEnhance.Color(pil_img).enhance(1.35)
    pil_img = ImageEnhance.Brightness(pil_img).enhance(1.05)
    return pil_img

def center_crop(pil_img, target_ratio):
    img_w, img_h = pil_img.size
    img_ratio = img_w / img_h
    if img_ratio > target_ratio:
        new_w = int(img_h * target_ratio)
        left  = (img_w - new_w) // 2
        pil_img = pil_img.crop((left, 0, left + new_w, img_h))
    else:
        new_h = int(img_w / target_ratio)
        top   = (img_h - new_h) // 2
        pil_img = pil_img.crop((0, top, img_w, top + new_h))
    return pil_img

HTML_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PAN Card Generator</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
<script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Inter', Arial, sans-serif;
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 40px 20px;
  }

  .wrapper {
    width: 100%;
    max-width: 520px;
  }

  .header {
    text-align: center;
    margin-bottom: 28px;
  }
  .header h1 {
    color: #fff;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: 1px;
  }
  .header p {
    color: rgba(255,255,255,0.55);
    font-size: 13px;
    margin-top: 6px;
  }

  .card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 36px 40px;
    box-shadow: 0 24px 60px rgba(0,0,0,0.4);
  }

  .field { margin-bottom: 22px; }

  label {
    display: block;
    font-size: 12px;
    font-weight: 600;
    color: rgba(255,255,255,0.7);
    margin-bottom: 8px;
    letter-spacing: 0.8px;
    text-transform: uppercase;
  }

  input[type="text"], input[type="date"] {
    width: 100%;
    padding: 12px 16px;
    background: rgba(255,255,255,0.08);
    border: 1.5px solid rgba(255,255,255,0.15);
    border-radius: 10px;
    font-size: 14px;
    color: #fff;
    outline: none;
    transition: border 0.2s, background 0.2s;
    font-family: 'Inter', Arial, sans-serif;
  }
  input[type="text"]::placeholder { color: rgba(255,255,255,0.3); }
  input[type="date"] { color-scheme: dark; }
  input:focus {
    border-color: rgba(100,180,255,0.7);
    background: rgba(255,255,255,0.12);
  }

  /* Upload areas */
  .upload-row {
    display: flex;
    gap: 20px;
    margin-bottom: 22px;
  }

  .photo-upload-area {
    width: 100px;
    height: 118px;
    border: 2px dashed rgba(255,255,255,0.25);
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    overflow: hidden;
    position: relative;
    background: rgba(255,255,255,0.05);
    transition: border-color 0.2s, background 0.2s;
    flex-shrink: 0;
  }
  .photo-upload-area:hover {
    border-color: rgba(100,180,255,0.6);
    background: rgba(255,255,255,0.1);
  }
  .photo-upload-area img {
    width: 100%; height: 100%;
    object-fit: cover;
    position: absolute; top: 0; left: 0;
  }
  .photo-upload-area .hint {
    font-size: 10px;
    color: rgba(255,255,255,0.4);
    text-align: center;
    line-height: 1.5;
    pointer-events: none;
    z-index: 1;
  }
  .photo-upload-area input[type="file"] {
    position: absolute; inset: 0;
    opacity: 0; cursor: pointer;
    width: 100%; height: 100%;
  }

  .photo-label-col {
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  .photo-label-col label {
    margin-bottom: 6px;
  }
  .photo-label-col .sub {
    font-size: 11px;
    color: rgba(255,255,255,0.35);
    line-height: 1.5;
  }

  .sign-upload-area {
    width: 100%;
    height: 72px;
    border: 2px dashed rgba(255,255,255,0.25);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    overflow: hidden;
    position: relative;
    background: rgba(255,255,255,0.05);
    transition: border-color 0.2s, background 0.2s;
  }
  .sign-upload-area:hover {
    border-color: rgba(100,180,255,0.6);
    background: rgba(255,255,255,0.1);
  }
  .sign-upload-area img {
    max-width: 100%; max-height: 100%;
    object-fit: contain; position: absolute;
  }
  .sign-upload-area .hint {
    font-size: 11px;
    color: rgba(255,255,255,0.4);
    pointer-events: none;
  }
  .sign-upload-area input[type="file"] {
    position: absolute; inset: 0;
    opacity: 0; cursor: pointer;
  }

  .divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.1);
    margin: 8px 0 22px;
  }

  button[type="submit"] {
    width: 100%;
    padding: 14px;
    background: linear-gradient(135deg, #1a6fc4, #2196f3);
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    letter-spacing: 0.5px;
    transition: opacity 0.2s, transform 0.1s;
    box-shadow: 0 6px 20px rgba(33,150,243,0.35);
    margin-top: 4px;
    position: relative;
  }
  button[type="submit"]:hover { opacity: 0.92; transform: translateY(-1px); }
  button[type="submit"]:active { transform: translateY(0); }
  button[type="submit"].loading { opacity: 0.7; pointer-events: none; }

  .spinner {
    display: none;
    width: 18px; height: 18px;
    border: 2px solid rgba(255,255,255,0.4);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    margin: 0 auto;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
</head>
<body>
<div class="wrapper">
  <div class="header">
    <h1>PAN Card Generator</h1>
    <p>Fill in the details to generate your PAN Card PDF</p>
  </div>

  <div class="card">
    <form method="POST" action="/generate" enctype="multipart/form-data" onsubmit="handleSubmit(this)">

      <!-- Photo upload -->
      <div class="upload-row">
        <div class="photo-upload-area" id="photoBox">
          <span class="hint">📷<br>Photo</span>
          <input type="file" name="photo" accept="image/*" onchange="previewImg(event,'photoBox')">
        </div>
        <div class="photo-label-col">
          <label>Applicant Photo</label>
          <div class="sub">Click the box to upload<br>passport size photo</div>
        </div>
      </div>

      <hr class="divider">

      <!-- PAN Number -->
      <div class="field">
        <label>PAN Number</label>
        <input type="text" name="pan_number" placeholder="ABCDE1234F" maxlength="10"
               style="text-transform:uppercase; letter-spacing:2px; font-weight:600; font-size:15px;" required>
      </div>

      <!-- Full Name -->
      <div class="field">
        <label>Full Name</label>
        <input type="text" name="name" placeholder="e.g. AMIT KUMAR" required>
      </div>

      <!-- Father's Name -->
      <div class="field">
        <label>Father's Name</label>
        <input type="text" name="father_name" placeholder="e.g. AMAN SHARMA" required>
      </div>

      <!-- DOB -->
      <div class="field">
        <label>Date of Birth</label>
        <input type="text" name="dob" id="dob" placeholder="DD/MM/YYYY" autocomplete="off" required>
      </div>

      <hr class="divider">

      <!-- Signature -->
      <div class="field">
        <label>Signature</label>
        <div class="sign-upload-area" id="signBox">
          <span class="hint">✍️ &nbsp; Click to upload signature image</span>
          <input type="file" name="signature" accept="image/*" onchange="previewImg(event,'signBox')">
        </div>
      </div>

      <button type="submit" id="submitBtn">
        <span id="btnText">Generate PAN Card PDF</span>
        <div class="spinner" id="spinner"></div>
      </button>

    </form>
  </div>
</div>

<script>
function previewImg(event, boxId) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(e) {
    const box = document.getElementById(boxId);
    let img = box.querySelector('img');
    if (!img) { img = document.createElement('img'); box.appendChild(img); }
    img.src = e.target.result;
    const hint = box.querySelector('.hint');
    if (hint) hint.style.display = 'none';
  };
  reader.readAsDataURL(file);
}

flatpickr("#dob", {
  dateFormat: "d/m/Y",
  allowInput: true,
  maxDate: "today",
  disableMobile: true,
  theme: "dark",
});

function handleSubmit(form) {
  const btn = document.getElementById('submitBtn');
  const txt = document.getElementById('btnText');
  const spin = document.getElementById('spinner');
  btn.classList.add('loading');
  txt.style.display = 'none';
  spin.style.display = 'block';
  setTimeout(() => {
    btn.classList.remove('loading');
    txt.style.display = 'block';
    spin.style.display = 'none';
  }, 8000);
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_FORM)

@app.route("/generate", methods=["POST"])
def generate():
    pan_number  = request.form.get("pan_number", "").upper()
    name        = request.form.get("name", "").upper()
    father_name = request.form.get("father_name", "").upper()
    dob_raw     = request.form.get("dob", "")
    photo_file  = request.files.get("photo")
    sign_file   = request.files.get("signature")

    dob = dob_raw  # Flatpickr already sends DD/MM/YYYY

    doc  = fitz.open(TEMPLATE_PDF)
    page = doc[0]

    # ── Photo insert (HDR enhanced) ──
    if photo_file and photo_file.filename:
        img_bytes = photo_file.read()
        pil_img   = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        box_ratio = PHOTO_RECT.width / PHOTO_RECT.height
        pil_img   = center_crop(pil_img, box_ratio)
        pil_img   = pil_img.resize((int(PHOTO_RECT.width * 6), int(PHOTO_RECT.height * 6)), Image.LANCZOS)
        pil_img   = enhance_photo_hdr(pil_img)

        buf = io.BytesIO()
        pil_img.save(buf, format="PNG", optimize=False, compress_level=1)
        page.insert_image(PHOTO_RECT, stream=buf.getvalue(), keep_proportion=False, overlay=True)

    # ── PAN Number ──
    if pan_number:
        x_cur, y_pan = PAN_NUM_POS
        for ch in pan_number:
            page.insert_text((x_cur, y_pan), ch, fontsize=PAN_FONT_SIZE, color=(0, 0, 0), fontname="Helvetica-Bold")
            x_cur += fitz.get_text_length(ch, fontname="Helvetica-Bold", fontsize=PAN_FONT_SIZE) + 0.5

    # ── Name / Father / DOB ──
    page.insert_text(NAME_POS,   name,        fontsize=FONT_SIZE, color=(0, 0, 0), fontname="Helvetica-Bold")
    page.insert_text(FATHER_POS, father_name, fontsize=FONT_SIZE, color=(0, 0, 0), fontname="Helvetica-Bold")
    page.insert_text(DOB_POS,    dob,         fontsize=FONT_SIZE, color=(0, 0, 0), fontname="Helvetica-Bold")

    # ── Signature insert (enhanced) ──
    if sign_file and sign_file.filename:
        sig_bytes = sign_file.read()
        pil_sig   = Image.open(io.BytesIO(sig_bytes)).convert("RGBA")

        r, g, b, a = pil_sig.split()
        rgb = Image.merge("RGB", (r, g, b))
        rgb = ImageEnhance.Contrast(rgb).enhance(1.8)
        rgb = ImageEnhance.Sharpness(rgb).enhance(2.0)
        pil_sig = Image.merge("RGBA", (*rgb.split(), a))

        orig_w, orig_h = pil_sig.size
        aspect  = orig_w / orig_h
        fixed_h = SIGN_RECT.height
        calc_w  = fixed_h * aspect
        cx      = (SIGN_RECT.x0 + SIGN_RECT.x1) / 2
        sign_place = fitz.Rect(cx - calc_w/2, SIGN_RECT.y0, cx + calc_w/2, SIGN_RECT.y1)

        buf = io.BytesIO()
        pil_sig.save(buf, format="PNG", optimize=False, compress_level=1)
        page.insert_image(sign_place, stream=buf.getvalue(), keep_proportion=True)

    # ── Save ultra high quality PDF ──
    output = io.BytesIO()
    doc.save(output,
             garbage=4,
             deflate=True,
             deflate_images=False,
             deflate_fonts=True,
             clean=True)
    doc.close()
    output.seek(0)

    return send_file(
        output,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="PAN_Card_Filled.pdf"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

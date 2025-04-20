from flask import Flask, render_template, request
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'csv', 'xlsx'}  

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='Tidak ada file yang diunggah.')

        file = request.files['file']

        if file.filename == '':
            return render_template('index.html', error='Tidak ada file yang dipilih.')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                file_ext = filename.rsplit('.', 1)[1].lower()
                if file_ext == 'csv':
                    df = pd.read_csv(filepath)
                elif file_ext == 'xlsx':
                    df = pd.read_excel(filepath)  # Gunakan pd.read_excel untuk file Excel
                else:
                    os.remove(filepath)
                    return render_template('index.html', error='Jenis file tidak dikenali.')

                if 'hadir' not in df.columns or 'total' not in df.columns:
                    os.remove(filepath)
                    return render_template('index.html', error="File harus memiliki kolom 'hadir' dan 'total'.")

                df['persentase'] = (df['hadir'] / df['total']) * 100
                df['persentase'] = df['persentase'].round(2)

                results = df.to_dict('records')
                os.remove(filepath)
                return render_template('result.html', results=results)

            except Exception as e:
                os.remove(filepath)
                return render_template('index.html', error=f'Terjadi kesalahan dalam memproses file: {e}')

        else:
            return render_template('index.html', error='Jenis file tidak diizinkan.')

    return render_template('index.html', error=None)

if __name__ == '__main__':
    app.run(debug=True)

#Flask menerima file yang diunggah.
#File disimpan sementara di folder uploads.
#Pandas membaca file CSV menjadi DataFrame.
#Aplikasi memeriksa apakah DataFrame memiliki kolom 'hadir' dan 'total'.
#Kolom 'persentase' dihitung berdasarkan rumus (hadir / total) * 100.
#Hasil persentase dibulatkan menjadi dua desimal.
#DataFrame diubah menjadi list of dictionaries.
#File CSV yang diunggah dihapus.
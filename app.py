from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename  # Correct import
import pandas as pd
import matplotlib.pyplot as plt
import os
import io
import base64

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def plot_to_base64(plt):
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    base64_img = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()
    return base64_img

def plot_connection_growth(data):
    data['Connected On'] = pd.to_datetime(data['Connected On'], format='%d %b %Y')
    connection_growth = data['Connected On'].dt.to_period('M').value_counts().sort_index()

    plt.figure(figsize=(12, 6))
    connection_growth.plot(kind='line', marker='o')
    plt.title('Connection Growth Over Time')
    plt.xlabel('Month')
    plt.ylabel('Number of Connections')
    plt.grid(True)
    return plot_to_base64(plt)

def plot_top_companies(data):
    top_companies = data['Company'].value_counts().head(10)

    plt.figure(figsize=(12, 10))
    top_companies.plot(kind='bar')
    plt.title('Top Companies by Number of Connections')
    plt.xlabel('Company')
    plt.ylabel('Number of Connections')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.grid(True)
    return plot_to_base64(plt)

def plot_positions_distribution(data):
    positions_distribution = data['Position'].value_counts().head(10)

    plt.figure(figsize=(12, 6))
    positions_distribution.plot(kind='bar')
    plt.title('Top Positions by Number of Connections')
    plt.xlabel('Position')
    plt.ylabel('Number of Connections')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.grid(True)
    return plot_to_base64(plt)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST' and 'csvfile' in request.files:
        file = request.files['csvfile']
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        data = pd.read_csv(filepath)
        growth_img = plot_connection_growth(data)
        companies_img = plot_top_companies(data)
        positions_img = plot_positions_distribution(data)
        return render_template('charts.html', growth_img=growth_img, companies_img=companies_img, positions_img=positions_img)
    return render_template('upload.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

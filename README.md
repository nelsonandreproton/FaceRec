# 🎯 Face Recognition System

A comprehensive facial recognition system with web-based validation interface, automatic model retraining, and real-time processing capabilities.

## ✨ Features

- **Real-time Face Recognition**: Process images and identify faces using pre-trained models
- **Web Validation Interface**: Review and correct misidentified faces through an intuitive web UI
- **Automatic Model Retraining**: Improve accuracy by retraining models with corrected data
- **Database Management**: SQLite-based storage for people, detections, and feedback
- **Home Assistant Integration**: Connect with Home Assistant for smart home automation
- **Processing Indicators**: Visual feedback during model training with time tracking
- **Statistics Dashboard**: Monitor system accuracy and performance metrics

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd FaceRec
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Linux/Mac
   source venv/bin/activate
   
   # On Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env file with your settings
   ```

5. **Initialize database**
   ```bash
   python create_database.py
   ```

6. **Train initial model** (optional)
   ```bash
   python train_model.py
   ```

## ⚙️ Configuration

Copy `.env.example` to `.env` and configure the following variables:

```bash
# Database Configuration
DB_PATH=face_recognition.db

# Web Server Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=true

# Paths Configuration
IMAGES_BASE_PATH=test_images
MODEL_PATH=models/face_model.pkl
TEMPLATES_PATH=templates
STATIC_PATH=static

# Model Configuration
CONFIDENCE_THRESHOLD=0.6
FACE_TOLERANCE=0.6
MAX_DETECTIONS_LIMIT=50

# Home Assistant Configuration (optional)
HA_ENABLED=false
HA_URL=http://localhost:8123
HA_TOKEN=your_ha_token_here
```

## 🎮 Usage

### 1. Web Validation Interface

Start the web validation server:

```bash
python web_validation.py
```

Visit http://localhost:5000 to:
- Review pending face detections
- Correct misidentified faces
- Trigger model retraining
- View system statistics

### 2. Face Recognition Processing

Process images with face recognition:

```bash
python face_recognizer.py path/to/image.jpg
```

### 3. Model Training

Train or retrain the face recognition model:

```bash
# Initial training with existing data
python train_model.py

# Retrain with feedback corrections
python retrain_model.py
```

### 4. Database Management

Create or reset the database:

```bash
python create_database.py
```

## 📁 Project Structure

```
FaceRec/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env.example             # Environment configuration template
├── .env                     # Your environment configuration (not in git)
├── .gitignore              # Git ignore rules
│
├── main_processor.py        # Main processing logic
├── face_recognizer.py       # Core face recognition functionality
├── web_validation.py        # Web interface for validation
├── train_model.py           # Initial model training
├── retrain_model.py         # Model retraining with feedback
├── create_database.py       # Database initialization
├── ha_integration.py        # Home Assistant integration
│
├── templates/               # HTML templates
│   ├── validation.html      # Main validation interface
│   └── stats.html          # Statistics dashboard
│
├── static/                  # Static web assets
├── models/                  # Trained face recognition models
├── test_images/            # Image storage directory
└── venv/                   # Virtual environment (not in git)
```

## 🌐 Web Interface

### Validation Page Features

- **Detection Cards**: Visual display of detected faces with confidence scores
- **Validation Controls**: Mark detections as correct or incorrect
- **Correction Panel**: Select the correct person for misidentified faces
- **Real-time Updates**: Instant feedback and card removal after validation
- **Processing Indicators**: Visual feedback during model retraining
- **Statistics**: Live accuracy metrics and processing statistics

### API Endpoints

- `GET /` - Main validation interface
- `POST /api/validate` - Validate a detection
- `POST /api/retrain` - Trigger model retraining
- `GET /stats` - Statistics dashboard
- `GET /images/<filename>` - Serve detection images

## 🔄 Model Retraining Workflow

1. **Feedback Collection**: System collects corrections from validation interface
2. **Processing**: Extract face encodings from corrected images
3. **Model Update**: Update person encodings with new data
4. **Rebuild**: Reconstruct the face recognition model
5. **Validation**: Mark processed feedback to avoid reprocessing

## 📊 Database Schema

### Tables

- **people**: Known individuals with face encodings
- **detections**: Face detection results with metadata
- **feedback**: Validation corrections for model improvement

### Key Fields

- `face_encoding`: Serialized face recognition vectors
- `confidence_score`: Recognition confidence (0.0 - 1.0)
- `is_verified`: Validation status
- `feedback_type`: Correction type (correction, unknown)

## 🏠 Home Assistant Integration

Enable Home Assistant integration by setting `HA_ENABLED=true` in your `.env` file:

```bash
HA_ENABLED=true
HA_URL=http://your-ha-instance:8123
HA_TOKEN=your_long_lived_access_token
```

Features:
- Send detection events to Home Assistant
- Trigger automations based on face recognition
- Update sensor states with recognition data

## 🔧 Development

### Adding New Features

1. **Database Changes**: Update `create_database.py` with schema modifications
2. **Model Changes**: Modify training logic in `train_model.py` or `retrain_model.py`
3. **Web Interface**: Update templates in `templates/` directory
4. **API Endpoints**: Add new routes in `web_validation.py`

### Testing

```bash
# Test face recognition with sample image
python face_recognizer.py test_images/sample.jpg

# Test web interface
python web_validation.py
# Visit http://localhost:5000

# Test model training
python train_model.py
```

## 🐛 Troubleshooting

### Common Issues

1. **"No faces found" errors**
   - Ensure images have clear, well-lit faces
   - Check image format (JPG, PNG supported)
   - Adjust `CONFIDENCE_THRESHOLD` in `.env`

2. **Web interface not loading**
   - Check if port 5000 is available
   - Verify Flask installation: `pip show Flask`
   - Check console output for error messages

3. **Model training failures**
   - Ensure sufficient training images (3+ per person)
   - Check image accessibility and permissions
   - Verify database connectivity

4. **Database errors**
   - Run `python create_database.py` to reset database
   - Check file permissions on database file
   - Ensure SQLite is properly installed

### Performance Optimization

- **Image Size**: Resize large images before processing
- **Database**: Regular cleanup of old detections
- **Model**: Periodic retraining with accumulated feedback
- **Memory**: Monitor memory usage during batch processing

## 📈 Monitoring

### Key Metrics

- **Accuracy**: Percentage of correct identifications
- **Processing Time**: Average time per image
- **Detection Rate**: Faces detected vs total images
- **Feedback Volume**: Corrections submitted over time

### Logs

Check application logs for debugging:
- Console output during script execution
- Web server logs in Flask debug mode
- Database query logs (if enabled)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [face_recognition](https://github.com/ageitgey/face_recognition) - Core face recognition library
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [OpenCV](https://opencv.org/) - Computer vision library
- [SQLite](https://www.sqlite.org/) - Embedded database

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Search existing issues on GitHub
3. Create a new issue with detailed description
4. Include error messages and environment details

---

**Made with ❤️ for smart home automation and security**
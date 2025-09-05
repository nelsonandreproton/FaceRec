# 🎯 Face Recognition System

A comprehensive facial recognition system with web-based validation interface, automatic model retraining, and real-time processing capabilities.

## ✨ Features

### 🎯 **Core Functionality**
- **Real-time Face Recognition**: Process images and identify faces using pre-trained models
- **Intelligent Learning**: Automatic model improvement through user feedback and corrections
- **Database Management**: SQLite-based storage for people, detections, and feedback
- **Home Assistant Integration**: Connect with Home Assistant for smart home automation

### 🌐 **Web Interface** 
- **Landing Page**: System overview with color-coded navigation to all features
- **Validation Interface** (🟢): Review and correct misidentified faces with intuitive controls
- **Training Dashboard** (🔵): Dedicated retraining interface with progress tracking and time estimates
- **Statistics Portal** (🟣): Comprehensive performance metrics and analytics dashboard

### 🚀 **User Experience**
- **Color-Coded Navigation**: Green (validation), Blue (training), Purple (statistics)
- **Real-time Feedback**: Instant confirmation of actions and status updates
- **Progress Tracking**: Visual indicators during model training with time estimates
- **Mobile Responsive**: Optimized interface works on desktop, tablet, and mobile
- **Intuitive Design**: Clean, modern interface with consistent navigation patterns

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

### 1. Web Interface

Start the web application server:

```bash
python web_validation.py
```

Visit http://localhost:5000 to access the complete web interface. See the [Web Interface](#-web-interface) section below for detailed page descriptions.

### 2. Face Recognition Processing

#### Current Implementation
The system currently processes images from files stored in the `test_images/` directory:

```bash
python face_recognizer.py path/to/image.jpg
```

**Image Processing Workflow:**
1. Place images in the `test_images/` folder
2. Run the face recognition script with the image path
3. The system detects and identifies faces in the image
4. Results are stored in the database for validation
5. Use the web interface to review and correct any misidentifications

**Supported Image Formats:** JPG, JPEG, PNG, BMP, TIFF

#### 🔮 **Planned Camera Integration**
The next major enhancement will add real-time camera capture capabilities:

**Planned Features:**
- **📷 Camera Integration**: Direct integration with USB cameras or Raspberry Pi camera modules
- **🔍 Motion Detection**: PIR motion sensor triggering automatic photo capture
- **⚡ Real-time Processing**: Automatic face recognition on captured images
- **🔔 Smart Notifications**: Instant alerts via Home Assistant when faces are detected
- **📁 Automatic Storage**: Captured images automatically saved to `captured_images/` directory
- **🎯 Continuous Monitoring**: 24/7 face recognition with motion-triggered activation

**Hardware Requirements (Future):**
- USB Camera or Raspberry Pi Camera Module
- PIR Motion Sensor
- Raspberry Pi or PC with camera support

**Integration Benefits:**
- No manual image handling required
- Reduced power consumption with motion triggering
- Seamless smart home integration
- Automatic security monitoring

### 3. Model Training

Train or retrain the face recognition model:

```bash
# Initial training with existing data
python train_model.py

# Retrain with feedback corrections (command line)
python retrain_model.py

# Or use the web interface at http://localhost:5000/retrain
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
│   ├── index.html          # Landing page
│   ├── validation.html      # Validation interface  
│   ├── retrain.html        # Training interface
│   └── stats.html          # Statistics dashboard
│
├── static/                  # Static web assets
├── models/                  # Trained face recognition models
├── test_images/            # Current: Image storage for manual processing
├── captured_images/        # Future: Auto-captured images from camera
└── venv/                   # Virtual environment (not in git)
```

## 🌐 Web Interface

### Navigation & Design

The web interface features a **color-coded design** for easy navigation:
- **🟢 Green Theme**: Validation pages - for reviewing and correcting detections
- **🔵 Blue Theme**: Training pages - for model retraining and improvement  
- **🟣 Purple Theme**: Statistics pages - for performance monitoring and analytics

### Page Structure

**📋 Navigation Menu** (consistent across all pages):
- **Home** (🏠) - System overview and feature access
- **Validation** (🔍) - Detection review and correction
- **Training** (🔄) - Model retraining interface
- **Statistics** (📈) - Performance metrics and analytics

### Key Features

#### **Landing Page (/)**
- **System Overview**: Feature descriptions and getting started guide
- **Quick Access**: Direct navigation to all major functions
- **Color-Coded Cards**: Visual organization by function type

#### **Validation Page (/validation)** 🟢
- **Detection Cards**: Visual display of detected faces with confidence scores
- **Validation Controls**: Mark detections as correct or incorrect  
- **Correction Panel**: Select the correct person for misidentified faces
- **Real-time Updates**: Instant feedback and card removal after validation
- **Statistics Bar**: Live accuracy metrics and processing statistics

#### **Training Page (/retrain)** 🔵
- **Training Data Overview**: Statistics on feedback and corrections
- **Progress Indicators**: Visual feedback during model retraining with time tracking
- **Recent Corrections**: History of user feedback and model improvements
- **One-Click Retraining**: Simple interface to trigger model updates

#### **Statistics Page (/stats)** 🟣
- **Performance Metrics**: System accuracy and detection rates
- **Progress Tracking**: Visual charts showing verification progress  
- **Trend Analysis**: Historical performance data and improvements
- **Action Alerts**: Notifications when retraining is recommended

### API Endpoints

- `GET /` - Landing page with system overview
- `GET /validation` - Detection validation interface
- `GET /retrain` - Model retraining interface
- `GET /stats` - Statistics and analytics dashboard
- `POST /api/validate` - Validate a detection
- `POST /api/retrain` - Trigger model retraining
- `GET /images/<filename>` - Serve detection images

## 🔄 Model Retraining Workflow

### Web Interface Workflow
1. **Validation** (🟢): Review and correct face detections on `/validation` page
2. **Training** (🔵): Monitor feedback and trigger retraining on `/retrain` page  
3. **Analytics** (🟣): Track improvements and performance on `/stats` page

### Technical Process
1. **Feedback Collection**: System collects corrections from validation interface
2. **Processing**: Extract face encodings from corrected images
3. **Model Update**: Update person encodings with new data
4. **Rebuild**: Reconstruct the face recognition model with progress tracking
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

## 🗺️ Roadmap

### 🎯 **Current Version (v1.0)**
- ✅ File-based image processing
- ✅ Web validation interface with color-coded navigation
- ✅ Automatic model retraining with user feedback
- ✅ Statistics dashboard and performance monitoring
- ✅ Home Assistant integration
- ✅ Mobile-responsive design

### 🔮 **Upcoming Features (v2.0)**
- 📷 **Real-time Camera Integration** (see [Face Recognition Processing](#2-face-recognition-processing) for details)
- 🔄 **Enhanced Automation**: Continuous monitoring and smart notifications
- 📊 **Advanced Analytics**: Time-based analytics and custom reporting

### 💡 **Future Considerations**
- Multi-camera support
- Cloud storage integration  
- Advanced privacy controls
- API for third-party integrations

---

**Made with ❤️ for smart home automation and security**
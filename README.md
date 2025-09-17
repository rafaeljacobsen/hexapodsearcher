# 🐛 Hexapod Family Explorer

A beautiful web application that allows you to explore hexapod (insect) families by fetching and displaying images from the iNaturalist API. Simply enter a family name and get stunning research-grade observation photos with detailed information.

## Features

- **🔍 Smart Search**: Search for any hexapod family by scientific name
- **📸 High-Quality Images**: Displays research-grade observation photos from iNaturalist
- **📊 Rich Information**: Shows scientific names, common names, observation dates, locations, and observers
- **🎨 Beautiful UI**: Modern, responsive design with smooth animations
- **⚡ Fast API**: Efficient Flask backend with proper error handling
- **📱 Mobile Friendly**: Responsive design that works on all devices

## API Endpoints

### Get Family Images (Default: 5 images)
```
GET /api/family/<family_name>
```

### Get Family Images (Custom count)
```
GET /api/family/<family_name>/count/<number>
```

**Parameters:**
- `family_name`: Scientific name of the hexapod family (e.g., "Formicidae", "Lepidoptera")
- `number`: Number of images to return (1-20, default: 5)

**Example Response:**
```json
{
  "family_name": "Formicidae",
  "family_id": 47208,
  "total_found": 5,
  "observations": [
    {
      "id": 123456789,
      "species_guess": "Carpenter Ant",
      "scientific_name": "Camponotus pennsylvanicus",
      "common_name": "Black Carpenter Ant",
      "observed_on": "2023-08-15",
      "location": "Central Park, New York, NY, USA",
      "user": "nature_photographer",
      "photos": [
        {
          "url": "https://static.inaturalist.org/photos/123456/large.jpg",
          "medium_url": "https://static.inaturalist.org/photos/123456/medium.jpg",
          "attribution": "nature_photographer"
        }
      ],
      "url": "https://www.inaturalist.org/observations/123456789"
    }
  ]
}
```

## Installation & Setup

### Prerequisites
- Python 3.7+
- pip (Python package installer)

### Quick Start

1. **Clone or download this repository**
   ```bash
   git clone <your-repo-url>
   cd hexapodfamilies
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser and visit**
   ```
   http://localhost:5000
   ```

## Usage

### Web Interface
1. Open the application in your browser
2. Enter a hexapod family name (e.g., "Formicidae" for ants)
3. Optionally adjust the number of images (1-20)
4. Click "Search" or press Enter
5. Explore the beautiful images and detailed information!

### API Usage
You can also use the API directly:

```bash
# Get 5 images of the ant family
curl http://localhost:5000/api/family/Formicidae

# Get 10 images of the butterfly family  
curl http://localhost:5000/api/family/Lepidoptera/count/10

# Get 3 images of the beetle family
curl http://localhost:5000/api/family/Coleoptera/count/3
```

## Popular Hexapod Families to Try

- **Formicidae** - Ants
- **Lepidoptera** - Butterflies and Moths  
- **Coleoptera** - Beetles
- **Apidae** - Bees
- **Libellulidae** - Dragonflies
- **Coccinellidae** - Ladybugs
- **Mantidae** - Praying Mantises
- **Cicadidae** - Cicadas
- **Papilionidae** - Swallowtail Butterflies
- **Chrysididae** - Cuckoo Wasps

## Technical Details

### How It Works
1. **Family Search**: The API first searches iNaturalist's taxonomy database for the specified family name
2. **Observation Filtering**: Finds research-grade observations with photos for that family
3. **Image Selection**: Selects the highest-voted observations to ensure quality
4. **Data Processing**: Extracts relevant information and image URLs
5. **Response**: Returns structured JSON data with all observation details

### Rate Limiting
The application follows iNaturalist's API best practices:
- Respects rate limits (max 100 requests/minute)
- Uses appropriate timeouts
- Handles errors gracefully

### Error Handling
- Invalid family names return helpful error messages
- Network issues are handled with retries
- Missing images are gracefully hidden
- All errors are logged for debugging

## Development

### Project Structure
```
hexapodfamilies/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # Frontend interface
└── README.md          # This file
```

### Adding Features
The codebase is designed to be easily extensible:
- Add new API endpoints in `app.py`
- Modify the frontend in `templates/index.html`
- Add new search filters or sorting options
- Implement caching for better performance

## Troubleshooting

### Common Issues

**"Family not found" errors:**
- Make sure you're using the correct scientific family name
- Try searching for the family on iNaturalist.org first
- Some families might not have research-grade observations with photos

**Slow loading:**
- This is normal for the first search as it contacts iNaturalist's API
- Subsequent searches for the same family will be faster

**No images displayed:**
- Check your internet connection
- Some observations might have broken image links
- Try a different family with more observations

### Logs
Check the console output where you ran `python app.py` for detailed error messages and API responses.

## Contributing

We welcome contributions! Feel free to:
- Report bugs or suggest features via GitHub issues
- Submit pull requests with improvements
- Add support for more taxonomic ranks
- Improve the user interface
- Add more search filters

## Credits

- **iNaturalist**: This project uses the iNaturalist API and displays content from their amazing community of citizen scientists
- **Flask**: Web framework
- **Beautiful UI**: Custom CSS with modern design principles

## License

This project is open source. Please respect iNaturalist's terms of service when using their API and content.

---

Happy exploring! 🐛✨ # hexapodsearcher

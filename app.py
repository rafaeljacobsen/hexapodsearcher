from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# iNaturalist API base URL
INATURALIST_API_BASE = "https://api.inaturalist.org/v1"

def search_hexapod_taxon_observations(taxon_name, limit=5):
    """
    Search for observations of a specific hexapod taxon from iNaturalist
    
    Args:
        taxon_name (str): The name of the hexapod taxon (family, superfamily, or order)
        limit (int): Number of observations to return (default: 5)
    
    Returns:
        list: List of observation data with images
    """
    try:
        # First, search for the taxon ID
        taxa_url = f"{INATURALIST_API_BASE}/taxa"
        taxa_params = {
            'q': taxon_name,
            'rank': ['family', 'superfamily', 'order'],
            'iconic_taxa': 'Insecta',  # Filter for insects (hexapods)
            'per_page': 1
        }
        
        taxa_response = requests.get(taxa_url, params=taxa_params, timeout=10)
        taxa_response.raise_for_status()
        taxa_data = taxa_response.json()
        
        if not taxa_data['results']:
            return {'error': f'Taxon "{taxon_name}" not found in hexapods'}
        
        taxon_id = taxa_data['results'][0]['id']
        taxon_scientific_name = taxa_data['results'][0]['name']
        taxon_rank = taxa_data['results'][0]['rank']
        
        # Now search for observations of this family with photos
        # Get more observations to filter for diversity
        # Add randomization to prevent getting the same images
        import random
        
        obs_url = f"{INATURALIST_API_BASE}/observations"
        obs_params = {
            'taxon_id': taxon_id,
            'has': ['photos'],
            'quality_grade': 'research',
            'per_page': min(50, limit * 10),  # Get more to filter for diversity
            'order_by': random.choice(['votes', 'created_at', 'observed_on']),
            'order': random.choice(['desc', 'asc']),
            'page': random.randint(1, 3)  # Randomize which page we get
        }
        
        obs_response = requests.get(obs_url, params=obs_params, timeout=10)
        obs_response.raise_for_status()
        obs_data = obs_response.json()
        
        # Extract relevant information and filter for diversity
        observations = []
        seen_species = set()
        seen_genera = set()
        
        for obs in obs_data['results']:
            if obs['photos'] and obs.get('taxon'):  # Ensure there are photos and taxon info
                taxon = obs['taxon']
                species_name = taxon.get('name', 'Unknown')
                
                # Extract genus from scientific name (first word)
                genus = species_name.split()[0] if species_name != 'Unknown' else 'Unknown'
                
                # Skip if we already have this species
                if species_name in seen_species:
                    continue
                
                # Prefer different genera, but allow same genus if we have space
                if genus in seen_genera and len(observations) < limit:
                    continue
                
                photo_info = []
                for photo in obs['photos'][:1]:  # Take first photo only
                    # iNaturalist often returns only square thumbnails, so we need to construct larger URLs
                    base_url = photo.get('url', '')
                    
                    # Transform URL to get larger versions
                    # Replace 'square' with 'medium' or 'large' for better quality
                    if 'square.jpeg' in base_url or 'square.jpg' in base_url:
                        large_url = base_url.replace('square.jpeg', 'large.jpeg').replace('square.jpg', 'large.jpg')
                        medium_url = base_url.replace('square.jpeg', 'medium.jpeg').replace('square.jpg', 'medium.jpg')
                    else:
                        # Fallback to original URLs if available
                        large_url = photo.get('large_url') or photo.get('medium_url') or photo.get('original_url') or photo['url']
                        medium_url = photo.get('medium_url') or photo.get('large_url') or photo['url']
                    
                    photo_info.append({
                        'url': large_url,  # Use large image as primary
                        'medium_url': medium_url,
                        'square_url': base_url,  # Keep original for fallback
                        'attribution': photo.get('attribution', 'Unknown')
                    })
                
                observation_info = {
                    'id': obs['id'],
                    'scientific_name': species_name,
                    'common_name': taxon.get('preferred_common_name', 'Unknown'),
                    'photos': photo_info,
                    'url': f"https://www.inaturalist.org/observations/{obs['id']}"
                }
                
                observations.append(observation_info)
                seen_species.add(species_name)
                seen_genera.add(genus)
                
                # Stop when we have enough observations
                if len(observations) >= limit:
                    break
        
        return {
            'taxon_name': taxon_scientific_name,
            'taxon_id': taxon_id,
            'taxon_rank': taxon_rank,
            'total_found': len(observations),
            'observations': observations
        }
        
    except requests.exceptions.RequestException as e:
        return {'error': f'API request failed: {str(e)}'}
    except Exception as e:
        return {'error': f'An error occurred: {str(e)}'}

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    """Serve the quiz page"""
    return render_template('quiz.html')

@app.route('/api/family/<family_name>')
def get_family_images(family_name):
    """
    API endpoint to get images for a hexapod taxon
    
    Args:
        family_name (str): Name of the hexapod taxon
    
    Returns:
        JSON response with observation data and images
    """
    result = search_hexapod_taxon_observations(family_name)
    return jsonify(result)

@app.route('/api/family/<family_name>/count/<int:count>')
def get_family_images_with_count(family_name, count):
    """
    API endpoint to get a specific number of images for a hexapod taxon
    
    Args:
        family_name (str): Name of the hexapod taxon
        count (int): Number of images to return
    
    Returns:
        JSON response with observation data and images
    """
    # Limit count to reasonable range
    count = max(1, min(count, 20))
    result = search_hexapod_taxon_observations(family_name, limit=count)
    return jsonify(result)

@app.route('/api/validate/taxon/<taxon_name>')
def validate_taxon_name(taxon_name):
    """
    Validate if a taxon name exists in hexapods and check for overlaps
    
    Args:
        taxon_name (str): Name of the taxon to validate
    
    Returns:
        JSON response with validation result
    """
    try:
        # Search for the taxon in iNaturalist's taxonomy
        taxa_url = f"{INATURALIST_API_BASE}/taxa"
        taxa_params = {
            'q': taxon_name,
            'rank': ['family', 'superfamily', 'order'],
            'iconic_taxa': 'Insecta',  # Filter for insects (hexapods)
            'per_page': 5
        }
        
        taxa_response = requests.get(taxa_url, params=taxa_params, timeout=10)
        taxa_response.raise_for_status()
        taxa_data = taxa_response.json()
        
        if not taxa_data['results']:
            return jsonify({
                'valid': False,
                'error': f'"{taxon_name}" is not a valid hexapod family, superfamily, or order'
            })
        
        # Find exact match
        exact_match = None
        for result in taxa_data['results']:
            if result['name'].lower() == taxon_name.lower():
                exact_match = result
                break
        
        if not exact_match:
            exact_match = taxa_data['results'][0]  # Use first result if no exact match
        
        return jsonify({
            'valid': True,
            'taxon_name': exact_match['name'],
            'taxon_id': exact_match['id'],
            'rank': exact_match['rank'],
            'ancestry': exact_match.get('ancestry', '')
        })
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': f'Error validating taxon name: {str(e)}'
        })

@app.route('/api/validate/overlap', methods=['POST'])
def check_taxonomic_overlap():
    """
    Check if a new taxon overlaps with existing taxa in the quiz
    
    Expects JSON: {"new_taxon": {"name": "...", "id": ..., "rank": "...", "ancestry": "..."}, "existing_taxa": [...]}
    Returns: {"overlap": true/false, "overlapping_taxon": "...", "reason": "..."}
    """
    try:
        data = request.get_json()
        new_taxon = data.get('new_taxon', {})
        existing_taxa = data.get('existing_taxa', [])
        
        new_id = str(new_taxon.get('taxon_id', ''))
        new_ancestry = new_taxon.get('ancestry', '')
        new_rank = new_taxon.get('rank', '')
        new_name = new_taxon.get('taxon_name', '')
        
        # Create ancestry sets for comparison
        new_ancestry_set = set(new_ancestry.split('/')) if new_ancestry else set()
        new_ancestry_set.add(new_id)
        
        for existing_taxon in existing_taxa:
            existing_id = str(existing_taxon.get('taxon_id', ''))
            existing_ancestry = existing_taxon.get('ancestry', '')
            existing_name = existing_taxon.get('taxon_name', '')
            
            existing_ancestry_set = set(existing_ancestry.split('/')) if existing_ancestry else set()
            existing_ancestry_set.add(existing_id)
            
            # Check for overlap: if either taxon is an ancestor of the other
            if new_id in existing_ancestry_set:
                return jsonify({
                    'overlap': True,
                    'overlapping_taxon': existing_name,
                    'reason': f'{new_name} ({new_rank}) is a parent/ancestor of {existing_name}'
                })
            
            if existing_id in new_ancestry_set:
                return jsonify({
                    'overlap': True,
                    'overlapping_taxon': existing_name,
                    'reason': f'{existing_name} is a parent/ancestor of {new_name} ({new_rank})'
                })
        
        return jsonify({'overlap': False})
        
    except Exception as e:
        return jsonify({
            'overlap': True,
            'error': f'Error checking overlap: {str(e)}'
        })

@app.route('/api/quiz/save', methods=['POST'])
def save_quiz_setup():
    """
    Save a quiz setup with a custom name
    
    Expects JSON: {"name": "My Quiz", "families": ["Formicidae", "Apidae", ...]}
    Returns: {"success": True, "message": "Quiz saved"}
    """
    try:
        data = request.get_json()
        quiz_name = data.get('name', '').strip()
        families = data.get('families', [])
        
        if not quiz_name:
            return jsonify({'error': 'Quiz name is required'})
        
        if not families or len(families) < 2:
            return jsonify({'error': 'At least 2 families are required'})
        
        # Create quizzes directory if it doesn't exist
        import os
        quiz_dir = 'saved_quizzes'
        if not os.path.exists(quiz_dir):
            os.makedirs(quiz_dir)
        
        # Save quiz to JSON file
        import json
        quiz_data = {
            'name': quiz_name,
            'families': families,
            'created_at': str(datetime.now()),
            'family_count': len(families)
        }
        
        # Use safe filename
        safe_filename = "".join(c for c in quiz_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{quiz_dir}/{safe_filename}.json"
        
        with open(filename, 'w') as f:
            json.dump(quiz_data, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'Quiz "{quiz_name}" saved successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to save quiz: {str(e)}'})

@app.route('/api/quiz/list')
def list_saved_quizzes():
    """
    List all saved quiz setups
    
    Returns: {"quizzes": [{"name": "...", "families": [...], ...}, ...]}
    """
    try:
        import os
        import json
        
        quiz_dir = 'saved_quizzes'
        quizzes = []
        
        if os.path.exists(quiz_dir):
            for filename in os.listdir(quiz_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(quiz_dir, filename), 'r') as f:
                            quiz_data = json.load(f)
                            quizzes.append(quiz_data)
                    except Exception:
                        continue  # Skip corrupted files
        
        # Sort by creation date (newest first)
        quizzes.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return jsonify({'quizzes': quizzes})
        
    except Exception as e:
        return jsonify({'error': f'Failed to load quizzes: {str(e)}'})

@app.route('/api/quiz/delete/<quiz_name>', methods=['DELETE'])
def delete_quiz_setup(quiz_name):
    """
    Delete a saved quiz setup
    
    Args:
        quiz_name (str): Name of the quiz to delete
    
    Returns: {"success": True, "message": "..."}
    """
    try:
        import os
        
        quiz_dir = 'saved_quizzes'
        safe_filename = "".join(c for c in quiz_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{quiz_dir}/{safe_filename}.json"
        
        if os.path.exists(filename):
            os.remove(filename)
            return jsonify({
                'success': True,
                'message': f'Quiz "{quiz_name}" deleted successfully'
            })
        else:
            return jsonify({'error': 'Quiz not found'})
            
    except Exception as e:
        return jsonify({'error': f'Failed to delete quiz: {str(e)}'})

@app.route('/api/quiz/question', methods=['POST'])
def get_quiz_question():
    """
    Get a random quiz question for the specified families
    
    Expects JSON: {"families": ["Formicidae", "Apidae", ...]}
    Returns: {"family_name": "Formicidae", "image_url": "...", "options": [...]}
    """
    try:
        data = request.get_json()
        families = data.get('families', [])
        
        if not families:
            return jsonify({'error': 'No families provided'})
        
        # Pick a random family from the list
        import random
        correct_family = random.choice(families)
        
        # Get one image for the correct taxon
        result = search_hexapod_taxon_observations(correct_family, limit=1)
        
        if 'error' in result or not result.get('observations'):
            return jsonify({'error': f'Could not get image for {correct_family}'})
        
        observation = result['observations'][0]
        
        return jsonify({
            'correct_answer': correct_family,
            'image_url': observation['photos'][0]['url'],
            'scientific_name': observation['scientific_name'],
            'observation_url': observation['url']
        })
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
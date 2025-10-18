"""
MJAPI Server for MahjongCopilot compatibility
This server provides an HTTP API compatible with @latorc/MahjongCopilot's MJAPI interface
using the mjai protocol for communication.

API Documentation: https://pastebin.com/wks80EsZ
Password: EaSXeZycr4
"""
import json
import argparse
import logging
import sys
import os
import uuid
import time
from flask import Flask, request, jsonify
from typing import Dict, Optional

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

try:
    import torch
    from mahjong.agent import AiAgent
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available. MJAPI server will use random decisions.")

app = Flask(__name__)

# Global state
users: Dict[str, dict] = {}  # username -> {secret, token, usage, limit}
sessions: Dict[str, dict] = {}  # token -> {bot, id, bound, model, seq}
available_models = ["mjbot-default"]

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_token_from_header():
    """Extract bearer token from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header[7:]
    return None


def verify_token():
    """Verify token and return user info, or None if invalid"""
    token = get_token_from_header()
    if not token:
        return None
    
    # Find user by token
    for username, user_data in users.items():
        if user_data.get('token') == token:
            return username, user_data
    
    return None


@app.route('/user/register', methods=['POST'])
def register():
    """Register a new user with a name"""
    try:
        data = request.get_json()
        name = data.get('name')
        
        if not name:
            return jsonify({"error": "Name is required"}), 400
        
        if name in users:
            return jsonify({"error": "User already exists"}), 400
        
        # Generate random secret
        secret = str(uuid.uuid4())
        
        users[name] = {
            'secret': secret,
            'token': None,
            'usage': 0,
            'limit': 10000  # Default limit
        }
        
        logger.info(f"Registered new user: {name}")
        
        return jsonify({
            'name': name,
            'secret': secret
        }), 200
        
    except Exception as e:
        logger.error(f"Error in register: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/user/login', methods=['POST'])
def login():
    """Login with name and secret, returns token (id)"""
    try:
        data = request.get_json()
        name = data.get('name')
        secret = data.get('secret')
        
        if not name or not secret:
            return jsonify({"error": "Name and secret are required"}), 400
        
        if name not in users:
            return jsonify({"error": "User not found"}), 404
        
        if users[name]['secret'] != secret:
            return jsonify({"error": "Invalid secret"}), 401
        
        # Generate new token
        token = str(uuid.uuid4())
        users[name]['token'] = token
        
        logger.info(f"User logged in: {name}")
        
        return jsonify({
            'id': token,
            'name': name
        }), 200
        
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/user', methods=['GET'])
def get_user_info():
    """Get current user info"""
    result = verify_token()
    if not result:
        return jsonify({"error": "Unauthorized"}), 401
    
    username, user_data = result
    
    return jsonify({
        'name': username,
        'usage': user_data['usage'],
        'limit': user_data['limit']
    }), 200


@app.route('/user/logout', methods=['POST'])
def logout():
    """Logout the current user"""
    result = verify_token()
    if not result:
        return jsonify({"error": "Unauthorized"}), 401
    
    username, user_data = result
    token = user_data.get('token')
    
    # Stop bot session if active
    if token in sessions:
        del sessions[token]
    
    # Clear token
    user_data['token'] = None
    
    logger.info(f"User logged out: {username}")
    
    return jsonify({"result": "success"}), 200


@app.route('/mjai/list', methods=['GET'])
def list_models():
    """Return list of available models"""
    result = verify_token()
    if not result:
        return jsonify({"error": "Unauthorized"}), 401
    
    return jsonify({
        'models': available_models
    }), 200


@app.route('/mjai/usage', methods=['GET'])
def get_usage():
    """Get mjai query usage"""
    result = verify_token()
    if not result:
        return jsonify({"error": "Unauthorized"}), 401
    
    username, user_data = result
    
    return jsonify({
        'used': user_data['usage']
    }), 200


@app.route('/mjai/limit', methods=['GET'])
def get_limit():
    """Get mjai query limit"""
    result = verify_token()
    if not result:
        return jsonify({"error": "Unauthorized"}), 401
    
    username, user_data = result
    
    return jsonify({
        'limit': user_data['limit'],
        'used': user_data['usage']
    }), 200


@app.route('/mjai/start', methods=['POST'])
def start_bot():
    """Start mjai bot with specified parameters"""
    result = verify_token()
    if not result:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        username, user_data = result
        token = user_data.get('token')
        data = request.get_json()
        
        bot_id = data.get('id')
        bound = data.get('bound', 256)
        model = data.get('model', 'mjbot-default')
        
        if model not in available_models:
            return jsonify({"error": f"Model {model} not found"}), 404
        
        # Initialize bot session
        bot = None
        if TORCH_AVAILABLE:
            try:
                bot = AiAgent()
                logger.info(f"Initialized AI agent for user {username}")
            except Exception as e:
                logger.warning(f"Failed to initialize AI agent: {e}")
        
        sessions[token] = {
            'bot': bot,
            'id': bot_id,
            'bound': bound,
            'model': model,
            'seq': 0,
            'game_state': {}  # Store game state for mjai protocol
        }
        
        logger.info(f"Started bot session for user {username} with model {model}")
        
        return jsonify({
            'result': 'success'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in start_bot: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/mjai/stop', methods=['POST'])
def stop_bot():
    """Stop the mjai bot"""
    result = verify_token()
    if not result:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        username, user_data = result
        token = user_data.get('token')
        
        if token in sessions:
            del sessions[token]
            logger.info(f"Stopped bot session for user {username}")
        
        return jsonify({
            'result': 'success'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in stop_bot: {str(e)}")
        return jsonify({"error": str(e)}), 500


def process_mjai_message(msg: dict, session: dict, username: str) -> Optional[dict]:
    """
    Process a single mjai message and return bot's reaction if any
    
    Args:
        msg: mjai protocol message
        session: bot session data
        username: username for logging
    
    Returns:
        mjai protocol reaction message or None
    """
    msg_type = msg.get('type')
    
    # Update game state based on message
    game_state = session['game_state']
    
    # Handle different message types
    if msg_type == 'start_game':
        game_state['started'] = True
        game_state['seat'] = msg.get('id', 0)
        return None
    
    elif msg_type == 'start_kyoku':
        game_state['kyoku_started'] = True
        game_state['bakaze'] = msg.get('bakaze')
        game_state['kyoku'] = msg.get('kyoku')
        game_state['honba'] = msg.get('honba')
        game_state['oya'] = msg.get('oya')
        game_state['scores'] = msg.get('scores', [])
        game_state['dora_marker'] = msg.get('dora_marker')
        
        # Handle initial hand
        if 'tehais' in msg:
            tehais = msg['tehais']
            if isinstance(tehais, list) and len(tehais) > game_state.get('seat', 0):
                game_state['hand'] = tehais[game_state['seat']]
        
        return None
    
    elif msg_type == 'tsumo':
        actor = msg.get('actor')
        pai = msg.get('pai')
        
        # If it's our turn, we need to decide what to discard
        if actor == game_state.get('seat'):
            if pai:
                game_state['tsumo_pai'] = pai
                # Add to hand
                if 'hand' not in game_state:
                    game_state['hand'] = []
                game_state['hand'].append(pai)
            
            # Check if we can act (should be indicated by can_act flag)
            if msg.get('can_act', True):
                # Bot should decide to discard
                reaction = make_dahai_decision(game_state, session)
                return reaction
        
        return None
    
    elif msg_type == 'dahai':
        actor = msg.get('actor')
        pai = msg.get('pai')
        
        # Update game state
        if actor == game_state.get('seat') and pai in game_state.get('hand', []):
            game_state['hand'].remove(pai)
            if 'tsumo_pai' in game_state:
                del game_state['tsumo_pai']
        
        # Check if we can react (pon, chi, kan, ron)
        if msg.get('can_act', False) and actor != game_state.get('seat'):
            # For now, just pass (none)
            return {'type': 'none'}
        
        return None
    
    elif msg_type == 'reach':
        actor = msg.get('actor')
        if actor == game_state.get('seat'):
            game_state['reached'] = True
        return None
    
    elif msg_type == 'dora':
        dora_marker = msg.get('dora_marker')
        if dora_marker:
            if 'doras' not in game_state:
                game_state['doras'] = []
            game_state['doras'].append(dora_marker)
        return None
    
    # For other message types, just track state without reaction
    return None


def make_dahai_decision(game_state: dict, session: dict) -> dict:
    """
    Make a discard (dahai) decision based on current game state
    
    Args:
        game_state: current game state
        session: bot session data
    
    Returns:
        mjai protocol dahai message
    """
    bot = session.get('bot')
    hand = game_state.get('hand', [])
    
    if not hand:
        return {'type': 'none'}
    
    # If we have an AI bot, use it
    if bot is not None and TORCH_AVAILABLE:
        try:
            # For now, use simple random selection
            # TODO: Implement proper AI decision using the bot
            import random
            selected_pai = random.choice(hand)
            
            return {
                'type': 'dahai',
                'pai': selected_pai,
                'actor': game_state.get('seat', 0)
            }
        except Exception as e:
            logger.warning(f"Error using AI bot: {e}, falling back to random")
    
    # Fallback: random selection
    import random
    selected_pai = random.choice(hand)
    
    return {
        'type': 'dahai',
        'pai': selected_pai,
        'actor': game_state.get('seat', 0)
    }


@app.route('/mjai/act', methods=['POST'])
def act():
    """Query mjai bot with a single action"""
    result = verify_token()
    if not result:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        username, user_data = result
        token = user_data.get('token')
        
        if token not in sessions:
            return jsonify({"error": "Bot not started"}), 400
        
        data = request.get_json()
        seq = data.get('seq')
        msg_data = data.get('data')
        
        session = sessions[token]
        
        # Update usage
        user_data['usage'] += 1
        
        # Process message and get reaction
        reaction = process_mjai_message(msg_data, session, username)
        
        if reaction:
            return jsonify({
                'act': reaction
            }), 200
        else:
            return '', 200
        
    except Exception as e:
        logger.error(f"Error in act: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/mjai/batch', methods=['POST'])
def batch():
    """Query mjai bot with multiple actions"""
    result = verify_token()
    if not result:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        username, user_data = result
        token = user_data.get('token')
        
        if token not in sessions:
            return jsonify({"error": "Bot not started"}), 400
        
        actions = request.get_json()
        
        if not isinstance(actions, list):
            return jsonify({"error": "Expected list of actions"}), 400
        
        session = sessions[token]
        
        # Update usage
        user_data['usage'] += len(actions)
        
        # Process all messages, return last reaction
        last_reaction = None
        for action in actions:
            seq = action.get('seq')
            msg_data = action.get('data')
            
            reaction = process_mjai_message(msg_data, session, username)
            if reaction:
                last_reaction = reaction
        
        if last_reaction:
            return jsonify({
                'act': last_reaction
            }), 200
        else:
            return '', 200
        
    except Exception as e:
        logger.error(f"Error in batch: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "torch_available": TORCH_AVAILABLE,
        "models": available_models
    }), 200


def main():
    parser = argparse.ArgumentParser(description='MJAPI Server for MahjongCopilot compatibility')
    parser.add_argument('-H', '--host', type=str, default='0.0.0.0',
                        help='Host to bind the server to (default: 0.0.0.0)')
    parser.add_argument('-p', '--port', type=int, default=5001,
                        help='Port to bind the server to (default: 5001)')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debug mode')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    
    logger.info(f"Starting MJAPI server on {args.host}:{args.port}")
    logger.info(f"Available models: {available_models}")
    
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()

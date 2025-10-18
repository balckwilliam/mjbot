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
        return jsonify({"error": "Registration failed"}), 500


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
        return jsonify({"error": "Login failed"}), 500


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
        
        bot_id = data.get('id', 0)  # Default to 0 if not provided
        bound = data.get('bound', 256)
        model = data.get('model', 'mjbot-default')
        
        # Validate bot_id is a valid integer
        if bot_id is None:
            bot_id = 0
        elif not isinstance(bot_id, int):
            try:
                bot_id = int(bot_id)
            except (ValueError, TypeError):
                bot_id = 0
        
        # Ensure bot_id is in valid range (0-3 for 4 players)
        if bot_id < 0 or bot_id > 3:
            return jsonify({"error": "Invalid 'id': must be 0-3"}), 400
        
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
            'game_state': {'seat': bot_id}  # Initialize with seat from id
        }
        
        logger.info(f"Started bot session for user {username} with model {model}, id={bot_id}")
        
        return jsonify({
            'result': 'success'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in start_bot: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to start bot"}), 500


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
        return jsonify({"error": "Failed to stop bot"}), 500


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
    # Validate message is not None
    if msg is None:
        logger.warning(f"Received None message for user {username}")
        return None
    
    msg_type = msg.get('type')
    
    # Update game state based on message
    game_state = session['game_state']
    
    # Initialize seat from session if not already set
    # Ensure seat is always an integer (default to 0)
    if 'seat' not in game_state:
        seat_value = session.get('id')
        game_state['seat'] = 0 if seat_value is None else seat_value
    
    # Handle different message types
    if msg_type == 'start_game':
        game_state['started'] = True
        # Get seat from message id, fallback to session id, then to 0
        seat_value = msg.get('id', session.get('id'))
        game_state['seat'] = 0 if seat_value is None else seat_value
        return None
    
    elif msg_type == 'start_kyoku':
        game_state['kyoku_started'] = True
        game_state['bakaze'] = msg.get('bakaze')
        game_state['kyoku'] = msg.get('kyoku')
        game_state['honba'] = msg.get('honba')
        game_state['oya'] = msg.get('oya')
        game_state['scores'] = msg.get('scores', [])
        
        # Validate and store dora_marker
        dora_marker = msg.get('dora_marker')
        if dora_marker:
            if validate_mjai_tile(dora_marker):
                game_state['dora_marker'] = dora_marker
                logger.debug(f"Dora marker: {dora_marker} ({mjai_tile_to_display_string(dora_marker)})")
            else:
                logger.warning(f"Invalid dora_marker: {dora_marker}")
                game_state['dora_marker'] = dora_marker  # Store anyway but log warning
        
        # Handle initial hand
        if 'tehais' in msg:
            tehais = msg['tehais']
            seat = game_state.get('seat', 0)
            # Ensure seat is a valid integer before using as index
            if seat is not None and isinstance(tehais, list) and isinstance(seat, int) and len(tehais) > seat:
                hand = tehais[seat]
                # Validate hand tiles
                invalid_tiles = [tile for tile in hand if not validate_mjai_tile(tile)]
                if invalid_tiles:
                    logger.warning(f"Invalid tiles in initial hand: {invalid_tiles}")
                game_state['hand'] = hand
                logger.debug(f"Initial hand for seat {seat}: {hand}")
        
        return None
    
    elif msg_type == 'tsumo':
        actor = msg.get('actor')
        pai = msg.get('pai')
        
        # Validate tile
        if pai and not validate_mjai_tile(pai):
            logger.warning(f"Invalid tile in tsumo: {pai}")
        
        # If it's our turn, we need to decide what to discard
        if actor == game_state.get('seat'):
            if pai:
                game_state['tsumo_pai'] = pai
                # Add to hand
                if 'hand' not in game_state:
                    game_state['hand'] = []
                game_state['hand'].append(pai)
                logger.debug(f"Drew tile: {pai} ({mjai_tile_to_display_string(pai) if validate_mjai_tile(pai) else 'invalid'})")
            
            # Check if we can act (should be indicated by can_act flag)
            if msg.get('can_act', True):
                # Bot should decide to discard
                reaction = make_dahai_decision(game_state, session)
                return reaction
        else:
            # Clear tsumo_pai when it's not our turn
            if 'tsumo_pai' in game_state:
                del game_state['tsumo_pai']
        
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
    
    elif msg_type == 'pon':
        actor = msg.get('actor')
        target = msg.get('target')
        pai = msg.get('pai')
        consumed = msg.get('consumed', [])
        
        # Update game state
        if actor == game_state.get('seat'):
            # Remove consumed tiles from hand
            if 'hand' in game_state:
                for tile in consumed:
                    if tile in game_state['hand']:
                        game_state['hand'].remove(tile)
        
        return None
    
    elif msg_type == 'chi':
        actor = msg.get('actor')
        target = msg.get('target')
        pai = msg.get('pai')
        consumed = msg.get('consumed', [])
        
        # Update game state
        if actor == game_state.get('seat'):
            # Remove consumed tiles from hand
            if 'hand' in game_state:
                for tile in consumed:
                    if tile in game_state['hand']:
                        game_state['hand'].remove(tile)
        
        return None
    
    elif msg_type in ['daiminkan', 'ankan', 'kakan']:
        actor = msg.get('actor')
        pai = msg.get('pai')
        consumed = msg.get('consumed', [])
        
        # Update game state
        if actor == game_state.get('seat'):
            # Remove consumed tiles from hand
            if 'hand' in game_state:
                for tile in consumed:
                    if tile in game_state['hand']:
                        game_state['hand'].remove(tile)
        
        return None
    
    elif msg_type == 'hora':
        # Win announcement - just track it
        actor = msg.get('actor')
        target = msg.get('target')
        if actor == game_state.get('seat'):
            game_state['won'] = True
        return None
    
    elif msg_type == 'ryukyoku':
        # Draw game
        game_state['ryukyoku'] = True
        return None
    
    elif msg_type == 'end_kyoku':
        # End of round - reset some state
        if 'hand' in game_state:
            del game_state['hand']
        if 'tsumo_pai' in game_state:
            del game_state['tsumo_pai']
        game_state['kyoku_started'] = False
        return None
    
    elif msg_type == 'end_game':
        # End of game - reset game state
        game_state.clear()
        # Ensure seat is always set after reset
        seat_value = session.get('id')
        game_state['seat'] = 0 if seat_value is None else seat_value
        return None
    
    elif msg_type == 'none':
        # No action - just pass through
        return None
    
    # For other message types, just track state without reaction
    return None


def normalize_tile_format(tile: str) -> str:
    """
    Normalize alternate tile formats to standard MJAI format
    
    Handles single-character honor tiles:
    - 'E' = East wind = '1z'
    - 'S' = South wind = '2z'
    - 'W' = West wind = '3z'
    - 'N' = North wind = '4z'
    - 'P' = White dragon (Haku/Pai) = '5z'
    - 'F' = Green dragon (Hatsu/Fa) = '6z'
    - 'C' = Red dragon (Chun) = '7z'
    
    Args:
        tile: Tile string in any supported format
    
    Returns:
        Normalized MJAI tile string
    """
    # Mapping of single-character honor tiles to standard MJAI format
    honor_tile_map = {
        'E': '1z',  # East wind (东)
        'S': '2z',  # South wind (南)
        'W': '3z',  # West wind (西)
        'N': '4z',  # North wind (北)
        'P': '5z',  # White dragon (白)
        'F': '6z',  # Green dragon (发)
        'C': '7z',  # Red dragon (中)
    }
    
    # If it's a single uppercase character, check if it's a honor tile
    if len(tile) == 1 and tile.upper() in honor_tile_map:
        return honor_tile_map[tile.upper()]
    
    # Otherwise, return as-is (already in standard format)
    return tile


def mjai_tile_to_tenhou_id(mjai_tile: str) -> int:
    """
    Convert MJAI tile notation to Tenhou tile ID
    
    MJAI: "1m", "5pr", "9s", "1z", etc.
    Tenhou: 0-135 (0-35 for manzu, 36-71 for pinzu, 72-107 for souzu, 108-135 for honors)
    Red tiles: 16 (5mr), 52 (5pr), 88 (5sr)
    
    Args:
        mjai_tile: MJAI tile string (e.g., "1m", "5pr", "9s", "1z")
    
    Returns:
        Tenhou tile ID (0-135)
    """
    if not mjai_tile:
        raise ValueError(f"Invalid MJAI tile: {mjai_tile}")
    
    # Normalize tile format first
    mjai_tile = normalize_tile_format(mjai_tile)
    
    if len(mjai_tile) < 2:
        raise ValueError(f"Invalid MJAI tile: {mjai_tile}")
    
    # Check if it's a red tile
    is_red = mjai_tile.endswith('r')
    if is_red:
        mjai_tile = mjai_tile[:-1]  # Remove 'r' suffix
    
    # Parse tile number and suit
    try:
        number = int(mjai_tile[0])
        suit = mjai_tile[1]
    except (ValueError, IndexError):
        raise ValueError(f"Invalid MJAI tile format: {mjai_tile}")
    
    # Convert to Tenhou ID
    if suit == 'm':  # Manzu (characters)
        base_id = (number - 1) * 4
        if is_red and number == 5:
            return 16  # Red 5 manzu
    elif suit == 'p':  # Pinzu (dots)
        base_id = 36 + (number - 1) * 4
        if is_red and number == 5:
            return 52  # Red 5 pinzu
    elif suit == 's':  # Souzu (bamboo)
        base_id = 72 + (number - 1) * 4
        if is_red and number == 5:
            return 88  # Red 5 souzu
    elif suit == 'z':  # Honor tiles
        if not 1 <= number <= 7:
            raise ValueError(f"Invalid honor tile number: {number}")
        base_id = 108 + (number - 1) * 4
    else:
        raise ValueError(f"Invalid suit: {suit}")
    
    # For non-red tiles, return base_id (can be any of the 4 identical tiles)
    return base_id


def tenhou_id_to_mjai_tile(tenhou_id: int) -> str:
    """
    Convert Tenhou tile ID to MJAI tile notation
    
    Args:
        tenhou_id: Tenhou tile ID (0-135)
    
    Returns:
        MJAI tile string (e.g., "1m", "5pr", "9s", "1z")
    """
    # Red tiles
    if tenhou_id == 16:
        return "5mr"
    elif tenhou_id == 52:
        return "5pr"
    elif tenhou_id == 88:
        return "5sr"
    
    # Regular tiles
    tile_type = tenhou_id // 4
    
    if tile_type < 9:  # Manzu
        return f"{tile_type + 1}m"
    elif tile_type < 18:  # Pinzu
        return f"{tile_type - 8}p"
    elif tile_type < 27:  # Souzu
        return f"{tile_type - 17}s"
    else:  # Honor tiles
        return f"{tile_type - 26}z"


def mjai_tile_to_display_string(mjai_tile: str) -> str:
    """
    Convert MJAI tile notation to human-readable Chinese display string
    
    Handles both standard MJAI format (1m-9m, 1p-9p, 1s-9s, 1z-7z) and
    alternate single-character format (E, S, W, N, P, F, C).
    
    Args:
        mjai_tile: MJAI tile string (e.g., "1m", "5pr", "9s", "1z", "5z", "P")
    
    Returns:
        Chinese display string (e.g., "一萬", "五饼", "九索", "東", "白")
    
    Examples:
        >>> mjai_tile_to_display_string("1m")
        '一萬'
        >>> mjai_tile_to_display_string("5z")
        '白'
        >>> mjai_tile_to_display_string("P")
        '白'
    """
    # Normalize alternate formats
    mjai_tile = normalize_tile_format(mjai_tile)
    
    # Chinese numerals
    chinese_numerals = {
        1: '一', 2: '二', 3: '三', 4: '四', 5: '五',
        6: '六', 7: '七', 8: '八', 9: '九'
    }
    
    # Honor tiles mapping
    honor_tiles = {
        '1z': '東',  # East
        '2z': '南',  # South
        '3z': '西',  # West
        '4z': '北',  # North
        '5z': '白',  # White dragon
        '6z': '發',  # Green dragon
        '7z': '中',  # Red dragon
    }
    
    # Handle red tiles
    is_red = mjai_tile.endswith('r')
    if is_red:
        mjai_tile = mjai_tile[:-1]
    
    # Check if it's an honor tile
    if mjai_tile in honor_tiles:
        return honor_tiles[mjai_tile]
    
    # Parse number and suit
    try:
        number = int(mjai_tile[0])
        suit = mjai_tile[1]
    except (ValueError, IndexError):
        return mjai_tile  # Return as-is if can't parse
    
    # Convert to display string
    num_str = chinese_numerals.get(number, str(number))
    
    if suit == 'm':
        return f"{'赤' if is_red else ''}{num_str}萬"
    elif suit == 'p':
        return f"{'赤' if is_red else ''}{num_str}饼"
    elif suit == 's':
        return f"{'赤' if is_red else ''}{num_str}索"
    else:
        return mjai_tile


def validate_mjai_tile(mjai_tile: str) -> bool:
    """
    Validate if a string is a valid MJAI tile notation
    
    Args:
        mjai_tile: Tile string to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not mjai_tile or not isinstance(mjai_tile, str):
        return False
    
    # Try to convert - if it succeeds, it's valid
    try:
        mjai_tile_to_tenhou_id(mjai_tile)
        return True
    except (ValueError, IndexError):
        return False


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
    tsumo_pai = game_state.get('tsumo_pai')
    
    if not hand:
        return {'type': 'none'}
    
    # Log hand for debugging
    logger.debug(f"Current hand: {hand}")
    
    # Validate all tiles in hand
    invalid_tiles = [tile for tile in hand if not validate_mjai_tile(tile)]
    if invalid_tiles:
        logger.warning(f"Invalid tiles in hand: {invalid_tiles}")
    
    # Determine the tile to discard
    selected_pai = None
    
    # If we have an AI bot, use it for decision making
    if bot is not None and TORCH_AVAILABLE:
        try:
            # Convert MJAI hand to Tenhou tile IDs for the neural network
            tenhou_hand = []
            for mjai_tile in hand:
                try:
                    tenhou_id = mjai_tile_to_tenhou_id(mjai_tile)
                    tenhou_hand.append(tenhou_id)
                    logger.debug(f"Converted {mjai_tile} -> {tenhou_id} ({mjai_tile_to_display_string(mjai_tile)})")
                except ValueError as e:
                    logger.warning(f"Failed to convert tile {mjai_tile}: {e}")
                    # Continue with other tiles
            
            if tenhou_hand:
                # Use the neural network model to make the discard decision
                # Note: The bot.discard method expects (state, tiles) where:
                # - state: numpy array of game features (shape: [291, 34])
                # - tiles: list of Tenhou tile IDs
                # 
                # For now, we use random selection because building the full state
                # requires complete game context (all discards, melds, dora, etc.)
                # TODO: Build complete game state features for neural network input
                # This would require tracking:
                # - All player discards and melds
                # - Dora indicators
                # - Round information (bakaze, kyoku, honba)
                # - Riichi declarations
                # See dataset/data.py and mahjong/game.py for state encoding
                
                import random
                selected_tenhou_id = random.choice(tenhou_hand)
                selected_pai = tenhou_id_to_mjai_tile(selected_tenhou_id)
            else:
                # Fallback if conversion failed
                import random
                selected_pai = random.choice(hand)
            
        except Exception as e:
            logger.warning(f"Error using AI bot: {e}, falling back to random")
            import random
            selected_pai = random.choice(hand)
    else:
        # Fallback: random selection when AI bot is not available
        import random
        selected_pai = random.choice(hand)
    
    # Determine if this is tsumogiri (discarding the just-drawn tile)
    tsumogiri = (selected_pai == tsumo_pai) if tsumo_pai else False
    
    return {
        'type': 'dahai',
        'pai': selected_pai,
        'actor': game_state.get('seat', 0),
        'tsumogiri': tsumogiri
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
        
        if not isinstance(data, dict):
            return jsonify({"error": "Expected JSON object"}), 400
        
        seq = data.get('seq')
        msg_data = data.get('data')
        
        # Validate msg_data
        if msg_data is None:
            return jsonify({"error": "Missing 'data' field"}), 400
        
        if not isinstance(msg_data, dict):
            return jsonify({"error": "Invalid 'data' field: must be an object"}), 400
        
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
        logger.error(f"Error in act: {str(e)}", exc_info=True)
        return jsonify({"error": "Action processing failed"}), 500


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
        for i, action in enumerate(actions):
            # Validate action structure
            if not isinstance(action, dict):
                logger.warning(f"Invalid action at index {i} for user {username}: not a dict")
                continue
            
            seq = action.get('seq')
            msg_data = action.get('data')
            
            # Validate msg_data exists
            if msg_data is None:
                logger.warning(f"Missing 'data' field in action at index {i} for user {username}")
                continue
            
            # Validate msg_data is a dict
            if not isinstance(msg_data, dict):
                logger.warning(f"Invalid 'data' field in action at index {i} for user {username}: not a dict")
                continue
            
            try:
                reaction = process_mjai_message(msg_data, session, username)
                if reaction:
                    last_reaction = reaction
            except Exception as msg_error:
                logger.error(f"Error processing message at index {i} for user {username}: {str(msg_error)}", exc_info=True)
                # Continue processing other messages instead of failing the entire batch
                continue
        
        if last_reaction:
            return jsonify({
                'act': last_reaction
            }), 200
        else:
            return '', 200
        
    except Exception as e:
        logger.error(f"Error in batch: {str(e)}", exc_info=True)
        return jsonify({"error": "Batch processing failed"}), 500


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

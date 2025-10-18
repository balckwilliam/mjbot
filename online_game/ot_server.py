"""
OT Server for MahjongCopilot compatibility
This server provides an HTTP API compatible with @latorc/MahjongCopilot's OT server interface
"""
import json
import gzip
import argparse
import logging
import sys
import os
from flask import Flask, request, jsonify

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

try:
    import torch
    from mahjong.agent import AiAgent
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available. OT server will use random decisions.")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Use Python's random module as fallback
    import random

app = Flask(__name__)
ai_agent = None
api_key = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def verify_api_key():
    """Verify API key from Authorization header"""
    if api_key is None:
        return True
    
    auth_header = request.headers.get('Authorization')
    if auth_header != api_key:
        return False
    return True


@app.route('/check', methods=['POST'])
def check():
    """Check API authorization"""
    if not verify_api_key():
        return jsonify({"result": "unauthorized"}), 401
    
    return jsonify({"result": "success"}), 200


@app.route('/react_batch', methods=['POST'])
def react_batch_4p():
    """
    Handle react_batch for 4-player mahjong
    
    Request format:
    {
        "obs": [...],  # List of observations, each observation should be:
                       # - A flattened array of length 9894 (291 features × 34 tiles)
                       # - Or a 2D array of shape [291, 34]
                       # Features are extracted from game state using game.get_feature()
        "masks": [...]  # List of action masks, each mask is a boolean array
                        # indicating which actions are valid (True) or invalid (False)
    }
    
    Response format:
    {
        "actions": [...],  # List of selected actions (indices of chosen actions)
        "q_out": [...],  # Q-values for all actions from the neural network
        "masks": [...],  # Returned masks (same as input)
        "is_greedy": [...]  # Whether actions were greedy (always True)
    }
    """
    if not verify_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Handle gzip-compressed data
        if request.headers.get('Content-Encoding') == 'gzip':
            data = gzip.decompress(request.data).decode('utf-8')
            post_data = json.loads(data)
        else:
            post_data = request.get_json()
        
        obs_list = post_data.get('obs', [])
        masks_list = post_data.get('masks', [])
        
        if not obs_list or not masks_list:
            return jsonify({"error": "Invalid request: obs and masks are required"}), 400
        
        # Process each observation and return actions
        actions = []
        q_out = []
        
        for obs, mask in zip(obs_list, masks_list):
            if TORCH_AVAILABLE and ai_agent is not None and NUMPY_AVAILABLE:
                # Convert to numpy arrays if needed
                if isinstance(obs, list):
                    obs = np.array(obs)
                if isinstance(mask, list):
                    mask = np.array(mask)
                
                # Use AI agent's discard model to make decision
                try:
                    # Convert observation to tensor
                    # Expected shape: [291, 34] or can be flattened [291*34]
                    if hasattr(obs, 'ndim') and obs.ndim == 2 and obs.shape[0] == 291 and obs.shape[1] == 34:
                        # Already in correct 2D shape
                        state_array = obs
                    elif len(obs) == 291 * 34:
                        # Flattened observation - need to reshape
                        state_array = obs.reshape(291, 34)
                    else:
                        # Invalid observation shape
                        obs_shape = getattr(obs, 'shape', f'length {len(obs)}')
                        raise ValueError(f"Invalid observation shape: expected [291, 34] or [9894], got {obs_shape}")
                    
                    state = torch.from_numpy(state_array).float()[None].to(ai_agent.device)
                    
                    # Get Q-values from the discard model
                    # Note: We use softmax to convert logits to probabilities for action selection
                    with torch.no_grad():
                        if ai_agent.discard_model is not None:
                            output = ai_agent.discard_model(state).softmax(1)[0]
                            q_values = output.cpu().numpy().tolist()
                        else:
                            # Fallback if model not loaded
                            q_values = [1.0 / len(mask)] * len(mask)
                    
                    # Apply mask to Q-values and select best valid action
                    valid_actions = [i for i, m in enumerate(mask) if m]
                    if valid_actions:
                        # Mask out invalid actions by setting their Q-values to -inf
                        masked_q_values = np.array(q_values)
                        masked_q_values[[i for i in range(len(mask)) if not mask[i]]] = -np.inf
                        action = int(np.argmax(masked_q_values))
                    else:
                        action = 0
                    
                    actions.append(action)
                    q_out.append(q_values)
                except Exception as e:
                    logger.warning(f"Error using AI model: {str(e)}, falling back to random selection")
                    # Fallback to random selection on error
                    valid_actions = [i for i, m in enumerate(mask) if m]
                    if valid_actions:
                        action = int(np.random.choice(valid_actions))
                    else:
                        action = 0
                    actions.append(action)
                    q_values = [0.0] * len(mask)
                    if valid_actions:
                        q_values[action] = 1.0
                    q_out.append(q_values)
            else:
                # Fallback: random action selection using Python's random module
                valid_actions = [i for i, m in enumerate(mask) if m]
                if valid_actions:
                    if NUMPY_AVAILABLE:
                        action = int(np.random.choice(valid_actions))
                    else:
                        action = random.choice(valid_actions)
                else:
                    action = 0
                
                actions.append(action)
                q_values = [0.0] * len(mask)
                q_values[action] = 1.0
                q_out.append(q_values)
        
        response = {
            "actions": actions,
            "q_out": q_out,
            "masks": masks_list,
            "is_greedy": [True] * len(actions)
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error processing react_batch request: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/react_batch_3p', methods=['POST'])
def react_batch_3p():
    """
    Handle react_batch for 3-player mahjong
    Same format as react_batch but for 3-player games
    """
    # For now, use the same logic as 4-player
    return react_batch_4p()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "torch_available": TORCH_AVAILABLE,
        "ai_loaded": ai_agent is not None
    }), 200


def main():
    global ai_agent, api_key
    
    parser = argparse.ArgumentParser(description='OT Server for MahjongCopilot compatibility')
    parser.add_argument('-H', '--host', type=str, default='0.0.0.0',
                        help='Host to bind the server to (default: 0.0.0.0)')
    parser.add_argument('-p', '--port', type=int, default=5000,
                        help='Port to bind the server to (default: 5000)')
    parser.add_argument('--api-key', type=str, default=None,
                        help='API key for authorization (optional)')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debug mode')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    
    api_key = args.api_key
    
    # Initialize AI agent if torch is available
    if TORCH_AVAILABLE:
        try:
            ai_agent = AiAgent()
            logger.info("AI agent initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize AI agent: {e}")
            logger.info("Server will use random decisions")
    else:
        logger.warning("PyTorch not available. Server will use random decisions.")
    
    logger.info(f"Starting OT server on {args.host}:{args.port}")
    if api_key:
        logger.info("API key authentication enabled")
    else:
        logger.info("API key authentication disabled")
    
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()

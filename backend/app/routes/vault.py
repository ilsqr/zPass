from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Vault
from app import db

vault_bp = Blueprint('vault', __name__)

@vault_bp.route('/', methods=['GET'])
@jwt_required()
def get_vault():
    """Get user's encrypted vault data"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        vault = user.vault
        if not vault:
            # Create vault if it doesn't exist
            vault = Vault(user_id=user_id)
            db.session.add(vault)
            db.session.commit()
        
        return jsonify({
            'message': 'Vault retrieved successfully',
            'vault': vault.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve vault: {str(e)}'}), 500

@vault_bp.route('/', methods=['PUT'])
@jwt_required()
def update_vault():
    """Update user's encrypted vault data"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        encrypted_data = data.get('encrypted_data')
        salt = data.get('salt')
        
        if encrypted_data is None:
            return jsonify({'error': 'Encrypted data is required'}), 400
        
        vault = user.vault
        if not vault:
            # Create vault if it doesn't exist
            vault = Vault(user_id=user_id)
            db.session.add(vault)
        
        # Update vault data
        vault.encrypted_data = encrypted_data
        if salt:
            vault.salt = salt
        
        db.session.commit()
        
        return jsonify({
            'message': 'Vault updated successfully',
            'vault': vault.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update vault: {str(e)}'}), 500



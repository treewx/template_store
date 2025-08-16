from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models.property import Property
from decimal import Decimal, InvalidOperation

properties_bp = Blueprint('properties', __name__, url_prefix='/api/properties')

def validate_property_data(data):
    """Validate property input data"""
    errors = []
    
    # Required fields
    if not data.get('name'):
        errors.append('Property name is required')
    
    if not data.get('rent_amount'):
        errors.append('Rent amount is required')
    else:
        try:
            rent_amount = Decimal(str(data['rent_amount']))
            if rent_amount <= 0:
                errors.append('Rent amount must be greater than 0')
        except (InvalidOperation, ValueError):
            errors.append('Invalid rent amount format')
    
    if not data.get('due_day'):
        errors.append('Due day is required')
    else:
        try:
            due_day = int(data['due_day'])
            if due_day < 1 or due_day > 31:
                errors.append('Due day must be between 1 and 31')
        except (ValueError, TypeError):
            errors.append('Due day must be a valid number')
    
    if not data.get('frequency'):
        errors.append('Frequency is required')
    elif data['frequency'] not in ['weekly', 'fortnightly', 'monthly']:
        errors.append('Frequency must be weekly, fortnightly, or monthly')
    
    return errors

@properties_bp.route('', methods=['GET'])
@login_required
def get_properties():
    """Get all properties for the current user"""
    try:
        properties = Property.get_by_user_id(current_user.id)
        return jsonify({
            'properties': [prop.to_dict() for prop in properties]
        }), 200
    except Exception as e:
        print(f"Error getting properties: {e}")
        return jsonify({'error': 'Failed to fetch properties'}), 500

@properties_bp.route('/<int:property_id>', methods=['GET'])
@login_required
def get_property(property_id):
    """Get a specific property"""
    try:
        property_obj = Property.get_by_id(property_id)
        
        if not property_obj:
            return jsonify({'error': 'Property not found'}), 404
        
        # Check if property belongs to current user
        if property_obj.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({'property': property_obj.to_dict()}), 200
    except Exception as e:
        print(f"Error getting property: {e}")
        return jsonify({'error': 'Failed to fetch property'}), 500

@properties_bp.route('', methods=['POST'])
@login_required
def create_property():
    """Create a new property"""
    try:
        data = request.get_json()
        
        # Validate input
        errors = validate_property_data(data)
        if errors:
            return jsonify({'error': '; '.join(errors)}), 400
        
        # Create property
        property_obj = Property.create_property(
            user_id=current_user.id,
            name=data['name'].strip(),
            address=data.get('address', '').strip(),
            rent_amount=Decimal(str(data['rent_amount'])),
            due_day=int(data['due_day']),
            frequency=data['frequency'],
            tenant_nickname=data.get('tenant_nickname', '').strip() or None
        )
        
        if not property_obj:
            return jsonify({'error': 'Failed to create property'}), 500
        
        return jsonify({
            'message': 'Property created successfully',
            'property': property_obj.to_dict()
        }), 201
        
    except Exception as e:
        print(f"Error creating property: {e}")
        return jsonify({'error': 'Failed to create property'}), 500

@properties_bp.route('/<int:property_id>', methods=['PUT'])
@login_required
def update_property(property_id):
    """Update a property"""
    try:
        data = request.get_json()
        
        # Get property
        property_obj = Property.get_by_id(property_id)
        if not property_obj:
            return jsonify({'error': 'Property not found'}), 404
        
        # Check ownership
        if property_obj.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Validate input
        errors = validate_property_data(data)
        if errors:
            return jsonify({'error': '; '.join(errors)}), 400
        
        # Update property
        success = property_obj.update(
            name=data['name'].strip(),
            address=data.get('address', '').strip(),
            rent_amount=Decimal(str(data['rent_amount'])),
            due_day=int(data['due_day']),
            frequency=data['frequency'],
            tenant_nickname=data.get('tenant_nickname', '').strip() or None
        )
        
        if not success:
            return jsonify({'error': 'Failed to update property'}), 500
        
        return jsonify({
            'message': 'Property updated successfully',
            'property': property_obj.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Error updating property: {e}")
        return jsonify({'error': 'Failed to update property'}), 500

@properties_bp.route('/<int:property_id>', methods=['DELETE'])
@login_required
def delete_property(property_id):
    """Delete a property"""
    try:
        # Get property
        property_obj = Property.get_by_id(property_id)
        if not property_obj:
            return jsonify({'error': 'Property not found'}), 404
        
        # Check ownership
        if property_obj.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Delete property
        success = property_obj.delete()
        if not success:
            return jsonify({'error': 'Failed to delete property'}), 500
        
        return jsonify({'message': 'Property deleted successfully'}), 200
        
    except Exception as e:
        print(f"Error deleting property: {e}")
        return jsonify({'error': 'Failed to delete property'}), 500

@properties_bp.route('/<int:property_id>/validate', methods=['POST'])
@login_required
def validate_property(property_id):
    """Validate property configuration for rent checking"""
    try:
        # Get property
        property_obj = Property.get_by_id(property_id)
        if not property_obj:
            return jsonify({'error': 'Property not found'}), 404
        
        # Check ownership
        if property_obj.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Validation checks
        issues = []
        
        if not property_obj.rent_amount or property_obj.rent_amount <= 0:
            issues.append('Invalid rent amount')
        
        if not property_obj.due_day or property_obj.due_day < 1 or property_obj.due_day > 31:
            issues.append('Invalid due day')
        
        if property_obj.frequency not in ['weekly', 'fortnightly', 'monthly']:
            issues.append('Invalid frequency')
        
        # Check for reasonable rent amounts (NZ context)
        if property_obj.rent_amount:
            if property_obj.frequency == 'weekly' and property_obj.rent_amount < 100:
                issues.append('Weekly rent seems unusually low')
            elif property_obj.frequency == 'monthly' and property_obj.rent_amount < 400:
                issues.append('Monthly rent seems unusually low')
        
        is_valid = len(issues) == 0
        
        return jsonify({
            'valid': is_valid,
            'issues': issues,
            'property': property_obj.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Error validating property: {e}")
        return jsonify({'error': 'Failed to validate property'}), 500
def positive_int(value, key):
    validate_result = {
        'valid': True,
        'errors':[]
    }

    try:
        value = int(value)
    except ValueError:
        validate_result['valid'] = False
        validate_result['errors'].append('invalid type of "{0}"'.format(key))
        return validate_result

    if value < 1:
        validate_result['valid'] = False
        validate_result['errors'].append('"{0}" must be 1 or more'.format(key))

    return validate_result


def sort_by(value, available_values: list):
    validate_result = {
        'valid': True,
        'errors': []
    }

    if value not in available_values:
        validate_result['valid'] = False
        validate_result['errors'].append('Sort by "{0}" field not supported'.format(value))

    return validate_result


def sort_order(value):
    validate_result = {
        'valid': True,
        'errors': []
    }

    if value.lower() not in ('asc', 'desc'):
        validate_result['valid'] = False
        validate_result['errors'].append('Sort order "' + str(value) + '" is not exist')

    return validate_result
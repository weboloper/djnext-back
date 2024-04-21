from rest_framework.views import exception_handler

REJECTED_FIELDS = ['non_field_errors', 'detail']


def build_errors(field, value, pointer=None):
    errors = []

    if isinstance(value, list):
        for err in value:
            if isinstance(err, dict):
                for k, v in err.items():
                    if field not in REJECTED_FIELDS:
                        pointer = f'{field}/{k}'

                    else:
                        pointer = f'{field}/non_field_errors'

                    return errors + build_errors(k, v, pointer)

            else:
                return errors + build_errors(field, err, pointer)

    elif isinstance(value, dict):
        for v in value.values():
            error_obj = {}
            if pointer:
                error_obj['pointer'] = pointer

            elif field not in REJECTED_FIELDS:
                error_obj['pointer'] = field

            else:
                error_obj['pointer'] = 'non_field_errors'

            error_obj['message'] = "".join(v)
            errors.append(error_obj)

    else:
        error_obj = {}

        if pointer:
            error_obj['pointer'] = pointer

        elif field not in REJECTED_FIELDS:
            error_obj['pointer'] = field

        else:
            error_obj['pointer'] = 'non_field_errors'

        error_obj['message'] = "".join(value)
        errors.append(error_obj)

    return errors


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        response_data_items = response.data
        response.data = {}
        errors = []

        if isinstance(response_data_items, list):
            for err in response_data_items:
                if isinstance(err, dict):
                    for k, v in err.items():
                        errors += build_errors(k, v)

                else:
                    errors += build_errors(response_data_items, err)

        else:
            for field, value in response_data_items.items():
                errors += build_errors(field, value)

        response.data = {
            "success": False,
            "payload": {},
            "error" : errors
        }
        # response.data["success"] = False
        # response.data["payload"] = {}
        # response.data['errors'] = errors

    return response
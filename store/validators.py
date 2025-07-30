from django.core.validators import ValidationError

def validate_file_size(file):
    max_size_kb = 5000

    if file.size > max_size_kb * 1024:
        raise ValidationError('Files can not be larger than {} KB'.format(max_size_kb))

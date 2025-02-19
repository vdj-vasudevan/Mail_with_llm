from datetime import datetime, timezone

def ct_to_one_fmt():
    # Get current time in UTC
    current_time = datetime.now(timezone.utc)

    # Format as 'Tue, 18 Feb 2025 15:45:16 GMT'
    formatted_time = current_time.strftime('%a, %d %b %Y %H:%M:%S GMT')

    return formatted_time

# print(ct_to_one_fmt())
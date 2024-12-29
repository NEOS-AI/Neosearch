def reverse_domain(domain: str):
    """
    Reverse a domain name in URI format.

    Args:
        domain (str): The domain name to reverse.

    Returns:
        str: The reversed domain name.
    """
    parts = domain.split('.')
    return '.'.join(reversed(parts))


if __name__ == "__main__":
    domain = "com.naver"
    reversed_domain = reverse_domain(domain)
    print(reversed_domain)  # naver.com

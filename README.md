# pytineye

**pytineye** is the official Python client library for the TinEye API. The TinEye API
is TinEye's paid search alternative for professional, commercial or high-volume users.
See <https://api.tineye.com/> for more information.

# Contents

- [ Installation ](#installation)
- [ Migrating from previous versions ](#migrating-from-previous-versions)
- [ Documentation ](#documentation)
- [ Support ](#support)

# Installation

Install the latest version of the library using pip:

```bash
$ python -m pip install pytineye
```

# Migrating from previous versions

If you were using any version of **pytineye** before `3.0.0`, you will need
to make minor changes to your code.

The API object is now instantiated using a single key, `api_key`. The value
of this key is the same as your previous `private_key`. The public key is no 
longer used.

#### New ✅
```python
# Sandbox key
# Note that this is the same value as the old private_key
api_key = "6mm60lsCNIB,FwOWjJqA80QZHh9BMwc-ber4u=t^"
api = TinEyeAPIRequest(
    api_url="https://api.tineye.com/rest/",
    api_key=api_key,
)
```

#### Old ❌
```python
# Sandbox keys
public_key = "LCkn,2K7osVwkX95K4Oy"
private_key = "6mm60lsCNIB,FwOWjJqA80QZHh9BMwc-ber4u=t^"
api = TinEyeAPIRequest(
    api_url="https://api.tineye.com/rest/",
    public_key=public_key,
    private_key=private_key,
)
```

# Documentation

View [documentation](https://api.tineye.com/python/docs/).

# Support

Please send comments, recommendations, and bug reports to <support@tineye.com>.
